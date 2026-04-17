#!/usr/bin/env python3
from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress
import subprocess, json, os
from config import AppConfig

console = Console()
config = AppConfig()

def run_agent(agent_num):
    cmd = f"python3 agent_{agent_num}_*.py"
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    return result.returncode == 0

def full_pipeline():
    with Progress(console=console) as progress:
        tasks = [
            ("🧠 Agent 1: Viral Idea", lambda: run_agent(1)),
            ("📝 Agent 2: Script + Hook", lambda: run_agent(2)), 
            ("🎙️ Agent 3: Voiceover", lambda: run_agent(3)),
            ("🎥 Agent 4: Video Edit", lambda: run_agent(4)),
            ("🖼️ Agent 5: Thumbnail", lambda: run_agent(5)),
            ("📤 Agent 6: YouTube Upload", lambda: run_agent(6)),
            ("📊 Agent 7: Analytics", lambda: run_agent(7))
        ]
        
        for desc, func in tasks:
            task = progress.add_task(desc, total=None)
            success = func()
            progress.update(task, description=f"{desc} ✅" if success else f"{desc} ❌")
    
    console.print(Panel("🎬 SHORTS READY | output/ + videos/", style="bold green"))

if __name__ == "__main__":
    full_pipeline()
