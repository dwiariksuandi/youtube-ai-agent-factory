#!/usr/bin/env python3
"""
MASTER FACTORY ORCHESTRATOR: Full 7-Agent Pipeline
Cron-scheduled daily production
"""

import os
from apscheduler.schedulers.blocking import BlockingScheduler
import subprocess

AGENTS = [
    "agents/idea_agent.py",
    "agents/script_agent.py", 
    "agents/voice_agent.py",
    "agents/video_agent.py",
    "agents/thumbnail_agent.py",
    "agents/publishing_agent.py",
    "agents/analytics_agent.py"
]

def run_pipeline():
    print("🏭 FULL FACTORY PIPELINE START")
    for agent in AGENTS:
        print(f"Running {agent}...")
        subprocess.run(["python3", agent], check=True)
    print("🏭 FACTORY COMPLETE - 7/7 Agents")

if __name__ == "__main__":
    scheduler = BlockingScheduler()
    scheduler.add_job(run_pipeline, 'interval', hours=24)
    print("🚀 Factory scheduled - Run once now:")
    run_pipeline()
    scheduler.start()
