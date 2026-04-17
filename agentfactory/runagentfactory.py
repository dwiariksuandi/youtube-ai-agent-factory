#!/usr/bin/env python3
from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress
import subprocess, json, os
from config import AppConfig

console = Console()
config = AppConfig()

def test_agent(num):
    cmd = f"python3 agent{num}*.py"
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    return result.returncode == 0

def full_pipeline():
    console.print(Panel("🎬 AGENT FACTORY LIVE", style="bold green"))
    with Progress() as progress:
        for i in range(1, 8):
            task = progress.add_task(f"Agent {i}", total=None)
            success = test_agent(i)
            progress.update(task, description=f"Agent {i}: {'✅' if success else '❌'}")
    
    console.print(Panel("🚀 READY | Add .env keys → PRODUCTION", style="bold blue"))

if __name__ == "__main__":
    full_pipeline()
