"""
run_agent_factory.py – 1x‑click dengan failover API key
Failover untuk: LLM, Gemini, Inworld, Stability, YouTube.
"""

import os
import subprocess
import time
from rich.console import Console
from config import app_config

console = Console()

AGENT_1 = "agent_1_idea.py"
AGENT_2 = "agent_2_script.py"
AGENT_3 = "agent_3_voice.py"
AGENT_4 = "agent_4_video.py"
AGENT_5 = "agent_5_thumbnail.py"
AGENT_6 = "agent_6_publishing.py"
AGENT_7 = "agent_7_analytics.py"

API_KEYS = {
    "llm": [
        (app_config.primary_llm_api_url, app_config.primary_llm_api_key),
        (app_config.backup1_llm_api_url, app_config.backup1_llm_api_key),
        (app_config.backup2_llm_api_url, app_config.backup2_llm_api_key),
    ],
    "gemini": [
        (app_config.primary_gemini_api_key, "primary_gemini"),
        (app_config.backup1_gemini_api_key, "backup1_gemini"),
        (app_config.backup2_gemini_api_key, "backup2_gemini"),
    ],
    "inworld": [
        (app_config.primary_inworld_api_key, "primary_inworld"),
        (app_config.backup1_inworld_api_key, "backup1_inworld"),
        (app_config.backup2_inworld_api_key, "backup2_inworld"),
    ],
    "stability": [
        (app_config.primary_stability_api_key, "primary_stability"),
        (app_config.backup1_stability_api_key, "backup1_stability"),
        (app_config.backup2_stability_api_key, "backup2_stability"),
    ],
    "youtube": [
        (app_config.primary_youtube_data_api_key, "primary_youtube"),
        (app_config.backup1_youtube_data_api_key, "backup1_youtube"),
        (app_config.backup2_youtube_data_api_key, "backup2_youtube"),
    ],
}

def run_agent_with_failover(script_name: str, api_type: str, failover_key: str) -> bool:
    """
    Run agent dan switch ke API key lain jika error.
    """
    for i, (url, key) in enumerate(API_KEYS[api_type]):
        cmd = [
            "python",
            os.path.join("agent_factory", script_name),
        ]
        if key:
            env = os.environ.copy()
            env[failover_key] = key
            console.log(f"[blue]Running {script_name} with {api_type} API key: {key}")
            result = subprocess.run(
                cmd,
                cwd="agent_factory",
                capture_output=True,
                text=True,
                env=env,
            )
        else:
            console.log(f"[yellow]Skipping {script_name} due to no API key: {key}")
            continue

        if result.returncode == 0:
            console.log(f"[green]✅ Agent {script_name} succeeded")
            break
        else:
            console.log(f"[red]❌ Agent {script_name} failed with key: {key}")
            if i == len(API_KEYS[api_type]) - 1:
                console.log(f"[red] Failed after all API keys for {api_type}")
                return False

    return True


def main():
    console.rule("[bold yellow]🎬 1x‑CLICK AGENTIC AI FACTORY (Agent 1–7) + Failover API")

    # 1. Agent 1 – Idea (LLM failover)
    if not run_agent_with_failover(AGENT_1, "llm", "PRIMARY_LLAMA3_API_KEY"):
        console.log("[red]❌ Agent 1 failed; aborting pipeline")
        return

    time.sleep(2)

    # 2. Agent 2 – Script (LLM failover)
    if not run_agent_with_failover(AGENT_2, "llm", "PRIMARY_LLAMA3_API_KEY"):
        console.log("[red]❌ Agent 2 failed; aborting pipeline")
        return

    time.sleep(2)

    # 3. Agent 3 – Voice (Inworld TTS failover)
    if not run_agent_with_failover(AGENT_3, "inworld", "PRIMARY_INWORLD_API_KEY"):
        console.log("[yellow]⚠️ Agent 3 failed; TTS audio may be missing")
    else:
        console.log("[green]✅ Agent 3 succeeded")

    time.sleep(2)

    # 4. Agent 4 – Video (Veo 3.1 failover)
    if not run_agent_with_failover(AGENT_4, "gemini", "PRIMARY_GEMINI_API_KEY"):
        console.log("[red]❌ Agent 4 failed; video may be missing")
    else:
        console.log("[green]✅ Agent 4 succeeded")

    time.sleep(2)

    # 5. Agent 5 – Thumbnail (SDXL failover)
    if not run_agent_with_failover(AGENT_5, "stability", "PRIMARY_STABILITY_API_KEY"):
        console.log("[yellow]⚠️ Agent 5 failed; thumbnail may be missing")
    else:
        console.log("[green]✅ Agent 5 succeeded")

    time.sleep(2)

    # 6. Agent 6 – Publishing (YouTube API failover)
    if not run_agent_with_failover(AGENT_6, "youtube", "PRIMARY_YOUTUBE_DATA_API_KEY"):
        console.log("[red]❌ Agent 6 failed; upload may be missing")
    else:
        console.log("[green]✅ Agent 6 succeeded")

    time.sleep(2)

    # 7. Agent 7 – Analytics (YouTube Analytics failover)
    if not run_agent_with_failover(AGENT_7, "youtube", "PRIMARY_YOUTUBE_DATA_API_KEY"):
        console.log("[yellow]⚠️ Agent 7 failed; analytics may be missing")
    else:
        console.log("[green]✅ Agent 7 succeeded")

    console.rule("[bold green]🎉 1x‑CLICK DONE (Agent 1–7 + Failover API)")
    console.log(
        "📊 Hasil:"
        f"\n- Topics: agent_factory/data/topics_queue.json"
        f"\n- Scripts: agent_factory/output/"
        f"\n- Videos: agent_factory/videos/"
        f"\n- Thumbnails: agent_factory/thumbnails/"
        f"\n- Analytics: agent_factory/analytics/"
    )


if __name__ == "__main__":
    main()
