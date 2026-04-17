"""
Agent 1 – Idea Agent (High‑CTR topic generator)
"""

from langchain.prompts import PromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser
from langchain.community.chat_models import ChatHuggingFace
from langchain_community.llms.huggingface_endpoints import HuggingFaceEndpoint
from langchain.globals import set_llm_cache
from langchain_community.cache import InMemoryCache
from langsmith import traceable
import json
import os
from typing import List, Dict, Optional
from rich.console import Console

from config import app_config

set_llm_cache(InMemoryCache())
console = Console()


class IdeaAgent:
    def __init__(self, niche: str = "", max_topics: int = 20):
        self.niche = niche or app_config.youtube_niche
        self.max_topics = max_topics
        self.model = HuggingFaceEndpoint(
            endpoint_url=app_config.llm_api_url,
            task="text-generation",
            model_kwargs={"temperature": 0.8, "max_new_tokens": 1024, "return_full_text": False},
        )
        self.llm = ChatHuggingFace(llm=self.model)

    def build_prompt(self) -> str:
        return """
Niche: {niche}

Instruksi:
Hasilkan daftar TOPIC untuk YouTube video (LONG 5–20m & SHORTS 15–60d).
Format JSON:
{{
  "long_form": [
    {{
      "topic_id": "long_001",
      "title": "judul video panjang",
      "keyword_focus": ["AI", "Automation", "Business"],
      "duration_seconds": 300,
      "hook": "0–30s hook",
      "description": "1–2 kalimat deskripsi",
      "tags": ["AI Agent", "Productivity", "YouTube"]
    }}
  ],
  "shorts": [
    {{
      "topic_id": "shorts_001",
      "title": "judul singkat provokatif",
      "duration_seconds": 30,
      "hook": "0–3s hook",
      "cta": "call to action",
      "tags": ["AI", "Shorts"]
    }}
  ]
}}
Hanya output JSON, tanpa tambahan teks.
"""

    def generate_topics(self) -> Dict:
        prompt_text = self.build_prompt()
        template = PromptTemplate(template=prompt_text, input_variables=["niche"])
        chain = (
            {"niche": RunnablePassthrough()}
            | template
            | self.llm
            | StrOutputParser()
        )
        result = chain.invoke(input={"niche": self.niche})
        result = result.strip()
        if result.startswith("```json") and result.endswith("```"):
            result = result[7:-3]
        elif result.startswith("```"):
            result = result[3:-3]
        try:
            data = json.loads(result)
            console.log("[green]✅ Agent 1: JSON topics parsed")
            return data
        except Exception as e:
            console.log(f"[red]❌ Agent 1: JSON parse error: {e}")
            return {"long_form": [], "shorts": []}

    def save_to_file(self, data: Dict, path: Optional[str] = None):
        out_path = path or app_config.topics_queue_path
        os.makedirs(os.path.dirname(out_path), exist_ok=True)
        with open(out_path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        console.log(f"[blue]📝 Agent 1: topics saved to {out_path}")

    def run(self):
        console.rule("[bold magenta]AGENT 1 – IDEA AGENT")
        topics = self.generate_topics()
        if not topics:
            console.log("[yellow]⚠️ Agent 1: no topics generated")
        else:
            self.save_to_file(topics)


if __name__ == "__main__":
    agent = IdeaAgent(max_topics=20)
    agent.run()
