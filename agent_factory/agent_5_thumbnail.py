"""
Agent 5 – Thumbnail Agent (Stable Diffusion XL via Stability API)

Input:  Markdown script dari Agent 2 (title, hook)
Output: thumbnails/ thumb_long_*.jpg dan thumb_shorts_*.jpg
"""

from config import app_config
from typing import List, Dict, Optional
import os
import json
import requests
import base64
from pathlib import Path
from rich.console import Console
from langsmith import traceable

console = Console()


class ThumbnailAgent:
    def __init__(self, markdown_dir: str = "", thumbnail_dir: str = ""):
        self.markdown_dir = markdown_dir or app_config.markdown_dir
        self.thumbnail_dir = thumbnail_dir or app_config.thumbnail_dir

        self.api_url = app_config.sdxl_api_url
        self.api_key = app_config.sdxl_api_key
        self.model_id = app_config.thumbnail_model_id
        self.width, self.height = app_config.thumbnail_resolution

        os.makedirs(self.thumbnail_dir, exist_ok=True)

    def load_markdown_files(self) -> List[Path]:
        """
        Cari semua .md di output/ (Agent 2).
        """
        p = Path(self.markdown_dir)
        files = list(p.glob("*.md"))
        console.log(f"[cyan]📁 Found {len(files)} .md script files")
        return files

    def generate_thumbnail_name(self, md_file: Path) -> str:
        """
        long_long_001.md → thumbnails/thumb_long_long_001.jpg
        shorts_shorts_001.md → thumbnails/thumb_shorts_shorts_001.jpg
        """
        stem = md_file.stem
        kind = "long" if "long_" in stem else "shorts"
        base = os.path.join(self.thumbnail_dir, f"thumb_{kind}_{stem}.jpg")
        return base

    def build_thumbnail_prompt(self, title: str, hook: str, niche: str) -> str:
        """
        Generate prompt thumbnail YouTube CTR‑tinggi.
        """
        return f"""
YouTube Thumbnail untuk video: "{title}"

Niche: {niche}

Hook: {hook}

Tugas:
Buat thumbnail YouTube dengan CTR tinggi.

Guideline:
- High contrast, warna cerah, sangat kontras.
- Teks judul besar dan mudah dibaca, 1–3 kata kunci saja.
- Background simple: tema AI/tech/automation, gradient, icon minimal.
- Thumbnail harus jelas di mode mobile (small view).
- Tidak perlu banyak detail, tetap rapi dan menarik.

Prompt: YouTube thumbnail untuk video {niche} dengan judul "{title}", tulisan besar, warna cerah, AI/automation theme, high contrast, modern look, tidak terlalu rumit, minimal text.
"""

    def extract_title_and_hook(self, file_path: Path) -> Dict[str, str]:
        """
        Ekstrak title dan hook dari .md.
        """
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()

        lines = content.splitlines()
        title = hook = "(No title)"

        # Cari header
        for i, line in enumerate(lines):
            line = line.strip()
            if line and line.startswith("# "):
                title = line[2:].strip()
                break

        # Cari hook dari 1–2 paragraf pertama
        for i, line in enumerate(lines):
            line = line.strip()
            if line and not line.startswith("#"):
                hook = line[:200]
                break

        return {"title": title, "hook": hook}

    def call_stability_sdxl(
        self,
        prompt: str,
        width: int,
        height: int,
        steps: int = 30,
    ) -> Optional[bytes]:
        """
        Panggil Stable Diffusion XL via Stability API.
        Kembalikan data binary image, atau None jika gagal.
        """
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}",
        }

        payload = {
            "text_prompts": [
                {"text": prompt}
            ],
            "cfg_scale": 7,
            "clip_guidance_preset": "FAST_BLUE",
            "height": height,
            "width": width,
            "samples": 1,
            "steps": steps,
        }

        try:
            resp = requests.post(
                self.api_url,
                headers=headers,
                json=payload,
                timeout=60,
            )
            resp.raise_for_status()
            result = resp.json()

            for artifact in result.get("artifacts", []):
                if artifact.get("base64"):
                    data = base64.b64decode(artifact["base64"])
                    console.log(f"[green]✅ SDXL thumbnail: {len(data)} bytes")
                    return data

            console.log("[red]❌ No base64 image in SDXL response")
            return None

        except Exception as e:
            console.log(f"[red]❌ SDXL API error: {e}")
            return None

    def generate_thumbnail_for_md(self, md_file: Path) -> Optional[str]:
        """
        Generate 1 thumbnail per .md file.
        Kembalikan path thumbnail file, atau None jika gagal.
        """
        console.log(f"[blue]🖼️ Processing {md_file.name} for thumbnail")

        # 1. Ekstrak title & hook
        meta = self.extract_title_and_hook(md_file)
        title = meta["title"]
        hook = meta["hook"]
        niche = app_config.youtube_niche

        # 2. Buat prompt
        full_prompt = self.build_thumbnail_prompt(title, hook, niche)

        # 3. Call SDXL
        image_data = self.call_stability_sdxl(
            prompt=full_prompt,
            width=self.width,
            height=self.height,
            steps=30,
        )

        if not image_data:
            return None

        # 4. Simpan file
        thumb_path = self.generate_thumbnail_name(md_file)

        os.makedirs(os.path.dirname(thumb_path), exist_ok=True)
        with open(thumb_path, "wb") as f:
            f.write(image_data)

        console.log(f"[blue]📺 Thumbnail saved: {thumb_path}")
        return thumb_path

    def run(self) -> List[str]:
        """
        Jalankan seluruh pipeline Agent 5.
        Kembalikan daftar path thumbnail.
        """
        console.rule("[bold magenta]AGENT 5 – THUMBNAIL AGENT (SDXL)")
        thumbnail_files = []

        markdown_files = self.load_markdown_files()
        if not markdown_files:
            console.log("[yellow]⚠️ Agent 5: no markdown files to generate thumbnails for")
            return thumbnail_files

        for mdfile in markdown_files:
            thumb_path = self.generate_thumbnail_for_md(mdfile)
            if thumb_path:
                thumbnail_files.append(thumb_path)

        console.log(f"[green]✅ Agent 5 done: {len(thumbnail_files)} thumbnail generated.")
        return thumbnail_files


if __name__ == "__main__":
    agent = ThumbnailAgent(
        markdown_dir="agent_factory/output",
        thumbnail_dir="agent_factory/thumbnails",
    )
    agent.run()
