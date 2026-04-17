"""
Agent 2 – Script Agent (YouTube Long + Shorts)
Optimized for CTR & Hook
"""

from langchain.prompts import PromptTemplate
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_community.chat_models import ChatHuggingFace
from langchain_community.llms.huggingface_endpoints import HuggingFaceEndpoint
from langchain_core.output_parsers import StrOutputParser
from langchain.globals import set_llm_cache
from langchain_community.cache import InMemoryCache
from langsmith import traceable
from rich.console import Console
import json
import os
from typing import Dict, Any, List

from config import app_config

set_llm_cache(InMemoryCache())
console = Console()


# 1. CTR & Hook pattern (parametrisasi di prompt)
HOOK_PATTERNS = [
    "Provokasi: Tantang anggapan umum.",
    "Rahasia: Ungkap hal yang jarang diajarkan.",
    "'Tanpa perlu ...': Tekankan kemudahan.",
    "100% otomatis: Tidak perlu manual.",
    "AI‑wow: Tekankan AI Agent yang menghasilkan ini.",
]

TITLE_CTR_PATTERNS = [
    "Tanpa Perlu ...",
    "100% Otomatis",
    "Tanpa Sentuh Kamera",
    "Tanpa Edit Manual",
    "Tanpa Perlu Kreatif",
    "Tanpa Perlu Script Manual",
    "Dari 0 Sampai Upload",
    "1 Klik Tunggal",
]


class ScriptAgent:
    def __init__(self, topics_file: str = ""):
        self.topics_file = topics_file or app_config.topics_queue_path
        self.model = HuggingFaceEndpoint(
            endpoint_url=app_config.llm_api_url,
            task="text-generation",
            model_kwargs={"temperature": 0.75, "top_p": 0.92, "max_new_tokens": 1792, "return_full_text": False},
        )
        self.llm = ChatHuggingFace(llm=self.model)

    def load_topics(self) -> Dict[str, List[Dict]]:
        path = self.topics_file
        if not os.path.exists(path):
            console.log(f"[red]❌ Agent 2: topics file not found: {path}")
            return {"long_form": [], "shorts": []}
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)

    def build_long_prompt(self) -> str:
        hook_list = "\n".join(f"- {p}" for p in HOOK_PATTERNS)
        title_list = "\n".join(f"- {p}" for p in TITLE_CTR_PATTERNS)

        return f"""
Niche: {app_config.youtube_niche}

INSTRUKSI OPTIMASI CTR:
Kamu adalah YouTube Script Writer profesional + AI Agent Factory.

1) HOOK 0–30 detik (Long):
GUNAKAN minimal 1 dari pola hook berikut:
{hook_list}

- Hook harus provokatif, jelas, AI‑wow, dan langsung ke inti.
- Jangan bertele‑tele; 1–2 kalimat maksimum.

2) JUDUL & CTA:
GUNAKAN minimal 1 dari pola CTR berikut:
{title_list}

- Judul harus menarik, klikbait positif, jelas, dan relevan niche.
- CTA (Call‑to‑Action) HARUS KUAT: subscribe, klik, comment, like, dsb.

3) FORMAT OUTPUT:
Gunakan MARKDOWN + timestamp.
Contoh: "0:00–0:30: HOOK ...".

JSON input: {{"long_form": [...] }}

Output:
  - 1 MARKDOWN file per TOPIC LONG.
  - Include: hook, intro, body, summary, CTA.
  - Hanya MARKDOWN, tanpa komentar tambahan.
"""

    def build_shorts_prompt(self) -> str:
        shorts_hook_list = "\n".join(f"- {p}" for p in [
            "Hook 0–3 detik: Provokasi, rahasia, 'Tanpa perlu ...'",
            "Pancing penonton: Tantang, bikin penasaran, curiga",
            "AI‑wow: Tegaskan ini 100% otomatis, no manual editing",
        ])

        return f"""
Niche: {app_config.youtube_niche}

Instruksi untuk SHORTS:

1) HOOK 0–3 detik:
Pakai minimal 1 pola berikut:
{shorts_hook_list}

- 0–3 detik MANDATORY sangat menarik.
- Sangat singkat; 1 kalimat sangat kuat.

2) FORMAT OUTPUT:
MARKDOWN + timestamps (0–3s, 3–15s, 15–akhir).
- 0–3s: HOOK
- 3–15s: INSIGHT (3–5 point singkat)
- 15–akhir: CTA

JSON input: {{"shorts": [...] }}

Output:
  - 1 MARKDOWN per TOPIC SHORTS.
  - Hanya MARKDOWN, tanpa komentar tambahan.
"""

    def build_long_template(self) -> ChatPromptTemplate:
        prompt_text = self.build_long_prompt()
        return ChatPromptTemplate.from_messages([("system", prompt_text), ("human", "Topic input: {topic_json}")])

    def build_shorts_template(self) -> ChatPromptTemplate:
        prompt_text = self.build_shorts_prompt()
        return ChatPromptTemplate.from_messages([("system", prompt_text), ("human", "Topic input: {topic_json}")])

    def generate_long_script_batch(self, topics: Dict):
        chain = self.build_long_template() | self.llm | StrOutputParser()
        console.rule("[blue]Generating LONG scripts (CTR‑optimized)")

        for long_topic in topics.get("long_form", []):
            if not long_topic:
                continue

            topic_id = long_topic["topic_id"]
            title = long_topic["title"]
            duration = long_topic["duration_seconds"]
            filename = f"output/long_{topic_id}.md"

            # 1. Coba modifikasi title dengan pola CTR
            base_title = title
            ctr_title = base_title
            for pattern in TITLE_CTR_PATTERNS:
                if pattern not in title:
                    ctr_title = f"{pattern}: {base_title}"
                    break

            long_topic_mod = dict(long_topic)
            long_topic_mod["title"] = ctr_title

            topic_str = json.dumps(long_topic_mod, ensure_ascii=False, indent=2)
            input_dict = {"topic_json": topic_str}
            result = chain.invoke(input_dict)

            os.makedirs(os.path.dirname(filename), exist_ok=True)
            with open(filename, "w", encoding="utf-8") as f:
                f.write(f"# Title: {ctr_title}\n# Duration: {duration} seconds\n\n{result}")

            console.log(f"[cyan]📄 Long script (CTR‑optimized): {filename}")

    def generate_shorts_script_batch(self, topics: Dict):
        chain = self.build_shorts_template() | self.llm | StrOutputParser()
        console.rule("[blue]Generating SHORTS scripts (CTR‑optimized)")

        for shorts_topic in topics.get("shorts", []):
            if not shorts_topic:
                continue

            topic_id = shorts_topic["topic_id"]
            title = shorts_topic["title"]
            duration = shorts_topic["duration_seconds"]
            filename = f"output/shorts_{topic_id}.md"

            # 1. Coba modifikasi title shorts dengan pola singkat & kuat
            base_title = title
            if len(base_title) > 50:
                base_title = base_title[:50] + " ..."

            ctr_title = base_title
            for pattern in [
                "Tanpa Perlu ...",
                "100% Otomatis",
                "Tanpa Edit Manual",
            ]:
                if pattern not in title:
                    ctr_title = f"{pattern}: {base_title}"
                    break

            shorts_topic_mod = dict(shorts_topic)
            shorts_topic_mod["title"] = ctr_title

            topic_str = json.dumps(shorts_topic_mod, ensure_ascii=False, indent=2)
            input_dict = {"topic_json": topic_str}
            result = chain.invoke(input_dict)

            os.makedirs(os.path.dirname(filename), exist_ok=True)
            with open(filename, "w", encoding="utf-8") as f:
                f.write(f"# Title: {ctr_title}\n# Duration: {duration} seconds\n\n{result}")

            console.log(f"[cyan]📄 Shorts script (CTR‑optimized): {filename}")

    def run(self):
        console.rule("[bold magenta]AGENT 2 – SCRIPT AGENT (CTR & HOOK OPTIMIZED)")
        topics = self.load_topics()
        if not topics:
            console.log("[red]❌ Agent 2: no topics")
            return

        if topics.get("long_form"):
            self.generate_long_script_batch(topics)
        if topics.get("shorts"):
            self.generate_shorts_script_batch(topics)


if __name__ == "__main__":
    agent = ScriptAgent()
    agent.run()
