"""
Agent 3 – Voice Agent (TTS: Inworld TTS‑1.5 Max)

Input:  Markdown script (output Agent 2)
Output: MP3 voiceover (audio/long/ & audio/shorts/)
"""

from config import app_config
from typing import List, Dict, Optional
import os
import requests
import json
import base64
from pathlib import Path
from rich.console import Console
from langsmith import traceable

console = Console()


class VoiceAgent:
    def __init__(self, markdown_dir: str = "", result_audio_dir: str = "audio"):
        self.markdown_dir = markdown_dir or app_config.markdown_dir
        self.result_audio_dir = result_audio_dir

        self.tts_api_url = app_config.inworld_api_url
        self.tts_model = app_config.inworld_tts_model
        self.tts_api_key = app_config.inworld_api_key

        # Buat direktori audio
        os.makedirs(os.path.join(self.result_audio_dir, "long"), exist_ok=True)
        os.makedirs(os.path.join(self.result_audio_dir, "shorts"), exist_ok=True)

    def load_markdown_files(self) -> List[Path]:
        p = Path(self.markdown_dir)
        files = list(p.glob("*.md"))
        console.log(f"[cyan]📁 Found {len(files)} .md files")
        return files

    def extract_script_text(self, file_path: Path) -> str:
        """
        Hanya ambil isi script, skip baris header #title.
        """
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()

        lines = content.splitlines()
        skip = 0
        for i, line in enumerate(lines):
            line = line.strip()
            if line and not line.startswith("#"):
                skip = i
                break
        body = "\n".join(lines[skip:]).strip()
        return body or "No script content."

    def generate_voicefile_name(self, file_path: Path, media_type: str = "audio") -> str:
        """
        Latih file: long_long_001.md → audio/long/long_long_001.audio.mp3
        """
        stem = file_path.stem
        if "long_" in stem:
            kind = "long"
        elif "shorts_" in stem:
            kind = "shorts"
        else:
            kind = "long"  # default

        audio_dir = os.path.join(self.result_audio_dir, kind)
        base = os.path.join(audio_dir, f"{stem}.{media_type}.mp3")
        return base

    def call_inworld_tts(self, text: str, voice_id: str = "Sarah") -> Optional[bytes]:
        headers = {
            "Authorization": f"Basic {self.tts_api_key}",
            "Content-Type": "application/json",
        }
        body = {
            "voiceId": voice_id,
            "modelId": self.tts_model,
            "text": text,
        }

        try:
            resp = requests.post(
                self.tts_api_url,
                headers=headers,
                json=body,
                timeout=30,
            )
            resp.raise_for_status()
            result = resp.json()
            audio_b64 = result.get("audioContent", "")
            if not audio_b64:
                console.log("[red]❌ No audioContent in TTS response")
                return None

            binary = base64.b64decode(audio_b64)
            console.log(f"[green]✅ TTS: generated {len(binary)} bytes audio")
            return binary

        except Exception as e:
            console.log(f"[red]❌ TTS API error: {e}")
            return None

    @traceable
    def process_single_file(self, md_file: Path, voice_id: str = "Sarah") -> Optional[str]:
        console.log(f"[blue]🔊 Processing {md_file.name}")
        text = self.extract_script_text(md_file)
        audio_path = self.generate_voicefile_name(md_file, media_type="audio")

        audio_data = self.call_inworld_tts(text, voice_id)
        if not audio_data:
            return None

        os.makedirs(os.path.dirname(audio_path), exist_ok=True)
        with open(audio_path, "wb") as f:
            f.write(audio_data)

        console.log(f"[green]📩 TTS saved: {audio_path}")
        return audio_path

    def run(self, voice_id: str = "Sarah") -> List[str]:
        console.rule("[bold magenta]AGENT 3 – VOICE AGENT (TTS)")
        audio_files = []

        markdown_files = self.load_markdown_files()
        if not markdown_files:
            console.log("[yellow]⚠️ No markdown files for TTS")
            return audio_files

        for mdfile in markdown_files:
            audio_path = self.process_single_file(mdfile, voice_id)
            if audio_path:
                audio_files.append(audio_path)

        console.log(f"[green]✅ Agent 3 done: {len(audio_files)} voice files generated.")
        return audio_files


if __name__ == "__main__":
    agent = VoiceAgent(
        markdown_dir="agent_factory/output",
        result_audio_dir="agent_factory/audio",
    )
    agent.run()
