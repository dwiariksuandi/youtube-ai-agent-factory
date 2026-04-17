"""
agent_7_analytics.py – Analytics Agent (YouTube Analytics API v3)

Input:  Video yang sudah di‑upload ke YouTube (Agent 6)
Output: analytics_summary.csv + optimization_recommendations.md

Metrik utama:
- views, avgViewDuration, averageViewPercentage, likes, shares, comments
"""

from config import app_config
from typing import List, Dict, Optional
import os
import json
import pickle
import googleapiclient.discovery
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.errors import HttpError
from rich.console import Console
from langsmith import traceable
import pandas as pd
from langchain.prompts import PromptTemplate
from langchain_community.chat_models import ChatHuggingFace
from langchain_community.llms.huggingface_endpoints import HuggingFaceEndpoint
from langchain_core.output_parsers import StrOutputParser

console = Console()


ANALYTICS_SCOPES = [
    "https://www.googleapis.com/auth/yt-analytics-monetary.readonly",
    "https://www.googleapis.com/auth/yt-analytics.readonly",
]


def authenticate_analytics() -> googleapiclient.discovery.Resource:
    """
    Authenticate YouTube Analytics API v3.
    Returns analytics client object.
    """
    credentials = None
    token_path = app_config.youtube_analytics_token_file

    if os.path.exists(token_path):
        with open(token_path, "rb") as f:
            credentials = pickle.load(f)

    if not credentials or not credentials.valid:
        if credentials and credentials.expired and credentials.refresh_token:
            credentials.refresh(Request())
        else:
            secrets_path = app_config.youtube_analytics_secrets_file
            if not os.path.exists(secrets_path):
                console.log("[red]❌ client_secret.json not found for Analytics API")
                raise FileNotFoundError(secrets_path)

            flow = InstalledAppFlow.from_client_secrets_file(
                secrets_path,
                ANALYTICS_SCOPES,
            )
            credentials = flow.run_local_server(port=0)

        with open(token_path, "wb") as f:
            pickle.dump(credentials, f)

    return googleapiclient.discovery.build("youtubeAnalytics", "v2", credentials=credentials)


class AnalyticsMetrics:
    """
    Konfigurasi dasar metrics & dimensions untuk report.
    """

    DIMENSIONS = ["video"]
    METRICS = "views,estimatedMinutesWatched,averageViewDuration,averageViewPercentage,likes,dislikes,shares,comments"

    def build_query_body(self, start_date: str, end_date: str, filters: Optional[str] = None) -> Dict:
        """
        Buat body request untuk query analytics.
        """
        body = {
            "ids": "channel==MINE",
            "startDate": start_date,
            "endDate": end_date,
            "metrics": self.METRICS,
            "dimensions": ",".join(self.DIMENSIONS),
            "sort": "-views",
            "maxResults": 1000,
        }

        if filters:
            body["filters"] = filters

        return body


class AnalyticsReport:
    """
    Object kelas laporan per video.
    """

    def __init__(self, video_id: str, title: str, data: Dict):
        self.video_id = video_id
        self.title = title
        self.views = int(data.get("views", 0))
        self.minutes_watched = float(data.get("estimatedMinutesWatched", 0.0))
        self.avg_view_duration = float(data.get("averageViewDuration", 0.0))
        self.avg_view_pct = float(data.get("averageViewPercentage", 0.0))
        self.likes = int(data.get("likes", 0))
        self.dislikes = int(data.get("dislikes", 0))
        self.shares = int(data.get("shares", 0))
        self.comments = int(data.get("comments", 0))

    def to_dict(self) -> Dict:
        """
        Konversi ke dict untuk masuk ke DataFrame.
        """
        return {
            "video_id": self.video_id,
            "title": self.title,
            "views": self.views,
            "estimated_minutes_watched": self.minutes_watched,
            "average_view_duration": self.avg_view_duration,
            "average_view_percentage": self.avg_view_pct,
            "likes": self.likes,
            "dislikes": self.dislikes,
            "shares": self.shares,
            "comments": self.comments,
        }


class AnalyticsAgent:
    """
    Agent 7 – Analytics Agent Utama
    """

    def __init__(
        self,
        llm_api_url: str = "",
        llm_name: str = "llama3-70b",
    ):
        # 1. Setup YouTube Analytics API
        self.analytics = authenticate_analytics()

        # 2. Tanggal periode
        self.start_date = "2026-01-01"  # sesuaikan dengan kebutuhan mu
        self.end_date = "2026-04-17"   # hari ini (April 17, 2026)

        # 3. Output
        self.output_dir = app_config.analytics_output_dir
        self.csv_path = os.path.join(self.output_dir, app_config.analytics_summary_csv)
        self.reco_path = os.path.join(self.output_dir, app_config.analytics_reco_md)

        # 4. Setup LLM untuk rekomendasi (reuse Llama‑3)
        self.llm_name = llm_name
        self.llm = ChatHuggingFace(
            llm=HuggingFaceEndpoint(
                endpoint_url=llm_api_url,
                task="text-generation",
                model_kwargs={"temperature": 0.7, "max_new_tokens": 1024},
            )
        )

    @traceable
    def fetch_analytics_report(self) -> List[Dict]:
        """
        Query YouTube Analytics API v3 dan collect data per video.
        Kembalikan list of dictionaries (siap ke DataFrame).
        """
        metrics = AnalyticsMetrics()
        body = metrics.build_query_body(
            start_date=self.start_date,
            end_date=self.end_date,
        )

        try:
            request = self.analytics.reports().query(**body)
            response = request.execute()

            rows = response.get("rows", [])
            result = []

            for r in rows:
                # r adalah list: [video_id, views, ..., ...]
                values = r
                video_id = values[0] if len(values) > 0 else "unknown"

                # mapping ke metric
                mapping = {
                    "views": 1,
                    "estimatedMinutesWatched": 2,
                    "averageViewDuration": 3,
                    "averageViewPercentage": 4,
                    "likes": 5,
                    "dislikes": 6,
                    "shares": 7,
                    "comments": 8,
                }

                data = {}
                for key, idx in mapping.items():
                    if idx < len(values):
                        try:
                            if key in ["likes", "dislikes", "shares", "comments"]:
                                data[key] = int(float(values[idx]))
                            else:
                                data[key] = float(values[idx])
                        except (ValueError, TypeError):
                            data[key] = 0.0

                # Untuk title, saat ini pakai template
                # Di implementasi nyata, kamu bisa fetch title dari YouTube Data API atau cache
                # Untuk contoh ini, kita pakai: Video 12345...
                title = f"Video {video_id}"

                report = AnalyticsReport(
                    video_id=video_id,
                    title=title,
                    data=data,
                )
                result.append(report.to_dict())

            console.log(f"[green]✅ Fetched {len(result)} video reports from Analytics API.")
            return result

        except HttpError as e:
            console.log(f"[red]❌ Analytics API error: {e}")
            return []

    @traceable
    def save_to_csv(self, data: List[Dict]):
        """
        Simpan DataFrame ke CSV di folder `analytics/`.
        """
        os.makedirs(self.output_dir, exist_ok=True)
        df = pd.DataFrame(data)
        df.to_csv(self.csv_path, index=False)
        console.log(f"[blue]📁 Analytics CSV saved: {self.csv_path}")

    @traceable
    def generate_optimization_plan(self, data: List[Dict]) -> str:
        """
        Gunakan LLM untuk membuat rekomendasi berbasis analytics data.
        """
        df = pd.DataFrame(data)
        summary = df.describe().to_string()

        prompt_text = """
YouTube Analytics Summary (output dari `df.describe()`):

{summary}

Instruksi:

Kamu adalah YouTube Strategy Consultant ber‑AI Agent Factory.

Tugas kamu:
1. Identifikasi:
   - 5 video terbaik:
     - AVD (Average View Duration) tertinggi
     - View percentage tertinggi
     - Engagement tertinggi (likes + shares + comments)
   - 5 video terburuk:
     - AVD rendah, view percentage rendah, engagement rendah
2. Tulis 10 rekomendasi praktis untuk:
   - Hook (3–5 detik awal, sangat menarik, jelas, AI‑wow).
   - Judul & CTR (judul lebih provokatif, jelas, klikbait positif, relevan niche).
   - Thumbnail (kontras tinggi, teks besar, 1–3 kata kunci, tema AI/automation/tech).
   - Durasi video (apakah terlalu panjang / terlalu pendek, pacing, cutting).
   - Call‑to‑action (lebih kuat: subscribe, klik, comment, like, etc.)
3. Berikan 2 contoh template perbaikan:
   - 1 video terbaik: apa yang sudah berhasil, cara scala.
   - 1 video terburuk: cara perbaiki hook, thumbnail, script, durasi, dsb.

Format output:
Gunakan Markdown, rapi, jelas, struktur:

- Terbaik 5:
- Terburuk 5:
- 10 Rekomendasi Umum:
- 2 Contoh Template Perbaikan:
"""

        template = PromptTemplate(
            template=prompt_text,
            input_variables=["summary"],
        )

        chain = (
            {"summary": RunnablePassthrough()}
            | template
            | self.llm
            | StrOutputParser()
        )

        try:
            result = chain.invoke({"summary": summary})
            return result or "No AI recommendations generated."
        except Exception as e:
            console.log(f"[red]❌ LLM failed during optimization planning: {e}")
            return "No AI recommendations generated (error during LLM call)."

    def run(self):
        """
        Jalankan seluruh pipeline Agent 7:
        1. Fetch analytics
        2. Save CSV
        3. Generate optimization recommendations
        4. Save ke .md
        """
        console.rule("[bold magenta]AGENT 7 – ANALYTICS AGENT (YouTube + AI Optimization)")

        # 1. Ambil data dari Analytics API
        data = self.fetch_analytics_report()
        if not data:
            console.log("[yellow]⚠️ No analytics data retrieved; skip.")
            return

        # 2. Simpan CSV
        self.save_to_csv(data)

        # 3. Generate AI‑based optimization plan
        plan = self.generate_optimization_plan(data)

        # 4. Simpan rekomendasi Markdown
        os.makedirs(self.output_dir, exist_ok=True)

        with open(self.reco_path, "w", encoding="utf-8") as f:
            f.write("# YouTube Analytics + Optimization Recommendations\n\n")
            f.write("## Data Summary\n\n")
            f.write("Data berikut berasal dari `agent_7_analytics.py` dan API YouTube Analytics v3.\n\n")
            f.write("## AI‑Generated Optimization Plan\n\n")
            f.write(plan)

        console.log(f"[green]✅ Optimization recommendations saved to {self.reco_path}")
        console.log("[bold green]📊 Agent 7 complete: analytics + AI‑driven strategy for YouTube performance.")


if __name__ == "__main__":
    agent = AnalyticsAgent(
        llm_api_url="http://localhost:8080",  # sesuaikan dengan `llm_api_url` di config.py
    )
    agent.run()
