"""
Agent 4 – Video Agent (Veo 3.1)
Tuning prompt style: cinematic, vlog, documentary (YouTube‑style)
+ zoom‑crop FFmpeg untuk watermark removal.
"""

from config import app_config
from typing import List, Dict, Optional
import os
import json
import requests
import time
import subprocess
from pathlib import Path
from rich.console import Console
from langsmith import traceable

console = Console()


CINEMATIC_PROMPT_TEMPLATE = """
Style: cinematic, high contrast, film‑like, dramatic lighting, 4K cinema look
Camera: steady dolly‑in or slow push‑in, 16:9 ultra‑wide framing
Subject: AI/automation expert, futuristic AI interface, tech environment
Action: voiceover narration, AI‑generated explainer, automation UI, data visualization
Environment: modern office, glass walls, futuristic city at night, glowing UI on screen
Camera movement: smooth dolly‑in to reveal AI interface, slight zoom to emphasize critical UI element
Light Gulf & mood: soft shadows, dramatic key light, blue–cyan accent, sleek AI‑tech look
No logos, no watermark, no text in frame, 100% AI‑generated, 30–60 seconds, 720p.
{script_text}
"""

VLOG_PROMPT_TEMPLATE = """
Style: YouTube vlog, 9:16 vertical, smartphone‑like, casual, friendly, warm tone
Camera: handheld close‑up, shallow depth‑of‑field, 9:16 vertical
Subject: AI creator, productivity expert, automation analyst, behind‑the‑desk vlogger
Action: talking directly to camera, explaining AI automation, showing AI dashboard, working on laptop
Environment: home office, cozy desk, plants, soft background, warm ambient light
Camera movement: slight handheld pan, static medium close‑up, subtle zoom on face
Lighting & mood: natural warm light, soft shadows, YouTube‑friendly color grading
No watermark, no text in frame, 100% AI‑generated, 30 seconds, 720p.
{script_text}
"""

DOCUMENTARY_PROMPT_TEMPLATE = """
Style: documentary, educational, realistic, 4K, 16:9 wide‑frame
Camera: handheld documentary, slight shake, naturalistic, 16:9
Subject: AI engineer, productivity expert, automation technician, developers, data screen
Action: walking through office, pointing at AI dashboard, explaining workflow automation, talking to camera
Environment: open office, glass walls, monitors, graphs, automation UI on screen, city skyline outside
Camera movement: slow handheld tracking, wide establishing shot, tight medium close‑up on face
Lighting & mood: realistic daylight, soft shadows, neutral color grading, no artificial gloss
No logos, no watermark, no text in frame, 100% AI‑generated, 30–60 seconds, 720p.
{script_text}
"""


class VideoAgent:
    def __init__(
        self,
        audio_dir: str = "audio",
        long_video_dir: str = "",
        shorts_video_dir: str = "",
    ):
        self.audio_dir = audio_dir or "audio"
        self.long_video_dir = long_video_dir or app_config.videos_long_dir
        self.shorts_video_dir = shorts_video_dir or app_config.videos_shorts_dir

        self.gemini_api_key = os.getenv("GEMINI_API_KEY", "")
        assert self.gemini_api_key, "❌ GEMINI_API_KEY must be set"

        self.base_url = "https://generativelanguage.googleapis.com/v1beta"
        self.model = "veo-3.1-generate-preview"

        os.makedirs(self.long_video_dir, exist_ok=True)
        os.makedirs(self.shorts_video_dir, exist_ok=True)

    def load_audio_files(self) -> List[Dict]:
        """
        Output: [{"path": str, "topic_id": "XX", "kind": "long|shorts"}, ...]
        """
        p = Path(self.audio_dir)
        result = []

        # long/*.audio.mp3
        for f in p.glob("long/*.audio.mp3"):
            stem = f.stem
            topic_id = stem.replace(".audio", "")
            if topic_id.startswith("long_"):
                result.append({
                    "path": str(f),
                    "topic_id": topic_id,
                    "kind": "long",
                    "output_dir": self.long_video_dir,
                })

        # shorts/*.audio.mp3
        for f in p.glob("shorts/*.audio.mp3"):
            stem = f.stem
            topic_id = stem.replace(".audio", "")
            if topic_id.startswith("shorts_"):
                result.append({
                    "path": str(f),
                    "topic_id": topic_id,
                    "kind": "shorts",
                    "output_dir": self.shorts_video_dir,
                })

        console.log(f"[cyan]📁 Found {len(result)} audio files")
        return result

    def load_markdown_by_topic_id(self, topic_id: str, kind: str) -> Optional[Path]:
        """
        cari: long_XX.md / shorts_XX.md
        """
        dir_md = Path(app_config.markdown_dir)
        if kind == "long":
            p = dir_md / f"long_{topic_id}.md"
        else:
            p = dir_md / f"shorts_{topic_id}.md"

        if p.exists():
            return p
        return None

    def extract_text_from_markdown(self, md_path: Path) -> str:
        with open(md_path, "r", encoding="utf-8") as f:
            content = f.read()
        lines = content.splitlines()
        skip = 0
        for i, line in enumerate(lines):
            line = line.strip()
            if line and not line.startswith("#"):
                skip = i
                break
        return "\n".join(lines[skip:]).strip() or "(No script)"

    def build_veo_prompt(self, script_text: str, style: str) -> str:
        if style == "cinematic":
            return CINEMATIC_PROMPT_TEMPLATE.format(script_text=script_text)
        elif style == "vlog":
            return VLOG_PROMPT_TEMPLATE.format(script_text=script_text)
        elif style == "documentary":
            return DOCUMENTARY_PROMPT_TEMPLATE.format(script_text=script_text)
        return script_text  # default plain text

    def make_veo_payload(self, script_text: str, duration: int, resolution: str, prompt_style: str) -> Dict:
        instances = [
            {
                "prompt": self.build_veo_prompt(script_text, prompt_style),
            }
        ]
        parameters = {
            "numberOfVideos": 1,
            "videoDuration": duration,
            "resolution": resolution,
        }
        return {"instances": instances, "parameters": parameters}

    def call_veo_create_job(self, script_text: str, duration: int, resolution: str, style: str) -> Optional[str]:
        headers = {
            "x-goog-api-key": self.gemini_api_key,
            "Content-Type": "application/json",
        }

        payload = self.make_veo_payload(script_text, duration, resolution, style)
        url = f"{self.base_url}/models/{self.model}:predictLongRunning"

        try:
            resp = requests.post(url, headers=headers, json=payload, timeout=60)
            resp.raise_for_status()
            result = resp.json()
            operation_name = result.get("name")

            if not operation_name:
                console.log("[red]❌ No operation name in Veo response")
                return None

            console.log(f"[green]✅ Veo job: {operation_name}")
            return operation_name

        except Exception as e:
            console.log(f"[red]❌ Veo create job error: {e}")
            return None

    def poll_veo_job_status(self, operation_name: str, max_wait: int = 900) -> Optional[str]:
        url = f"{self.base_url}/{operation_name}"
        headers = {"x-goog-api-key": self.gemini_api_key}

        waited = 0
        interval = 10
        while waited < max_wait:
            try:
                resp = requests.get(url, headers=headers, timeout=30)
                resp.raise_for_status()
                status = resp.json()

                if status.get("done", False):
                    res = status.get("response", {})
                    uri = res.get("generateVideoResponse", {}).get(
                        "generatedSamples", [{}])[0].get(
                        "video", {}).get("uri")
                    if uri:
                        console.log(f"[green]🎥 Veo video ready: {uri}")
                        return uri
                    console.log("[red]❌ No video URI in response")
                    return None

                console.log(f"[blue]🕒 Veo running: {status.get('metadata', {})}")

            except Exception as e:
                console.log(f"[red]❌ Polling error: {e}")

            time.sleep(interval)
            waited += interval

        console.log("[red]❌ Veo timeout: max_wait reached")
        return None

    def download_video(self, video_uri: str, out_path: str) -> bool:
        headers = {"x-goog-api-key": self.gemini_api_key}
        try:
            resp = requests.get(video_uri, headers=headers, stream=True, timeout=60)
            resp.raise_for_status()

            with open(out_path, "wb") as f:
                for chunk in resp.iter_content(chunk_size=8192):
                    f.write(chunk)

            console.log(f"[green]📥 Video downloaded (RAW): {out_path}")
            return True

        except Exception as e:
            console.log(f"[red]❌ Download error: {e}")
            return False

    def apply_zoom_crop_ffmpeg(self, raw_video_path: str, kind: str) -> str:
        """
        Jalankan FFmpeg zoom‑crop:
        - Long: 16:9; 107% zoom + crop 1920:1080 → watermark di sudut hilang.
        - Shorts: 9:16; 106% zoom + crop 1080:1920.

        Kembalikan path VIDEO TANPA WATERMARK.
        """
        stem = Path(raw_video_path).stem
        final_dir = Path(raw_video_path).parent
        clean_path = final_dir / f"{stem}_clean.mp4"

        if kind == "long":
            # 16:9; zoom 107% + crop 1920:1080
            cmd = [
                "ffmpeg", "-y",
                "-i", raw_video_path,
                "-vf", "scale=iw*1.07:-1,crop=1920:1080",
                "-c:a", "copy",
                str(clean_path),
            ]
        else:
            # 9:16 Shorts; zoom 106% + crop 1080:1920
            cmd = [
                "ffmpeg", "-y",
                "-i", raw_video_path,
                "-vf", "scale=iw*1.06:ih*1.06,crop=1080:1920",
                "-c:a", "copy",
                str(clean_path),
            ]

        console.log(f"[blue]🎬 Applying FFmpeg zoom‑crop: {' '.join(cmd)}")

        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
            if result.returncode != 0:
                console.log(f"[red]❌ FFmpeg error: {result.stderr}")
                return raw_video_path  # fallback ke video raw

            console.log(f"[green]🎥 Zoom‑crop success: {clean_path}")
            return str(clean_path)

        except Exception as e:
            console.log(f"[red]❌ FFmpeg subprocess error: {e}")
            return raw_video_path

    def categorize_style(self, topic_id: str) -> str:
        """
        Categorize style: cinematic, vlog, documentary (based on topic_id pattern).
        """
        if "doc_" in topic_id or "episode" in topic_id:
            return "documentary"
        elif "shorts" in topic_id or "snack" in topic_id:
            return "vlog"
        else:
            return "cinematic"

    @traceable
    def process_single_audio_with_script(
        self,
        audio_info: Dict,
        script_text: str,
    ) -> Optional[str]:
        topic_id = audio_info["topic_id"]
        kind = audio_info["kind"]
        out_dir = audio_info["output_dir"]

        duration = app_config.long_300s_video_duration if kind == "long" else app_config.shorts_video_duration
        resolution = app_config.veo_video_resolution
        style = self.categorize_style(topic_id)

        stem = f"veo_{kind}_{topic_id}"
        raw_path = os.path.join(out_dir, f"{stem}.raw.mp4")
        final_path = os.path.join(out_dir, f"{stem}.mp4")

        op_name = self.call_veo_create_job(script_text, duration, resolution, style)
        if not op_name:
            return None

        uri = self.poll_veo_job_status(op_name)
        if not uri:
            return None

        # 1. Download video RAW (masih ber‑watermark)
        if not self.download_video(uri, raw_path):
            return None

        # 2. Zoom‑crop dengan FFmpeg (hilangkan watermark)
        clean_path = self.apply_zoom_crop_ffmpeg(raw_path, kind)

        # 3. Rename ke final_path (path yang dipakai Agent 6)
        if os.path.exists(clean_path) and clean_path != final_path:
            os.rename(clean_path, final_path)
            console.log(f"[green]📦 Final video (no watermark): {final_path}")

        # 4. Cleanup raw file (opsional)
        if os.path.exists(raw_path):
            os.remove(raw_path)

        return final_path

    def run(self) -> List[str]:
        console.rule("[bold magenta]AGENT 4 – VIDEO AGENT (VEO 3.1 + ZOOM‑CROP + Style‑tuned Prompt)")
        video_files = []

        audio_infos = self.load_audio_files()
        if not audio_infos:
            console.log("[yellow]⚠️ No audio files to process")
            return video_files

        for audio_info in audio_infos:
            audio_path = audio_info["path"]
            topic_id = audio_info["topic_id"]
            kind = audio_info["kind"]

            md_path = self.load_markdown_by_topic_id(topic_id, kind)
            if not md_path:
                console.log(f"[yellow]⚠️ No Markdown for topic {topic_id}")
                continue

            script_text = self.extract_text_from_markdown(md_path)
            if not script_text.strip():
                console.log(f"[yellow]⚠️ Empty script for {md_path}")
                continue

            video_path = self.process_single_audio_with_script(audio_info, script_text)
            if video_path:
                video_files.append(video_path)

        console.log(f"[green]✅ Agent 4 done: {len(video_files)} video (no watermark) generated.")
        return video_files


if __name__ == "__main__":
    agent = VideoAgent(
        audio_dir="agent_factory/audio",
        long_video_dir="agent_factory/videos/long",
        shorts_video_dir="agent_factory/videos/shorts",
    )
    agent.run()
