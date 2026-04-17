"""
config.py
Dibuat untuk membaca .env dari root repo: /.env
Dijalankan dari agent_factory/ atau root.
"""

from pydantic import BaseModel
from dotenv import load_dotenv
import os
import sys

# Dapatkan path root repo (dari agent_factory ke ../)
if __name__ == "__main__":
    # Jika dijalankan langsung, pastikan path relatif ke root
    current_dir = os.path.dirname(os.path.abspath(__file__))
    root_dir = os.path.abspath(os.path.join(current_dir, ".."))
else:
    root_dir = os.path.abspath("..")

env_path = os.path.join(root_dir, ".env")

# Muat environment dari root repo
if os.path.exists(env_path):
    load_dotenv(env_path)
else:
    print(f"[WARNING] .env not found at {env_path}")

# 1. LLM API (Hugging Face) – 3 akun
PRIMARY_LLAMA3_API_URL = os.getenv("PRIMARY_LLAMA3_API_URL", "")
PRIMARY_LLAMA3_API_KEY = os.getenv("PRIMARY_LLAMA3_API_KEY", "")

BACKUP1_LLAMA3_API_URL = os.getenv("BACKUP1_LLAMA3_API_URL", "")
BACKUP1_LLAMA3_API_KEY = os.getenv("BACKUP1_LLAMA3_API_KEY", "")

BACKUP2_LLAMA3_API_URL = os.getenv("BACKUP2_LLAMA3_API_URL", "")
BACKUP2_LLAMA3_API_KEY = os.getenv("BACKUP2_LLAMA3_API_KEY", "")

# 2. Gemini API (Veo 3.1) – 3 akun
PRIMARY_GEMINI_API_KEY = os.getenv("PRIMARY_GEMINI_API_KEY", "")
BACKUP1_GEMINI_API_KEY = os.getenv("BACKUP1_GEMINI_API_KEY", "")
BACKUP2_GEMINI_API_KEY = os.getenv("BACKUP2_GEMINI_API_KEY", "")

# 3. Inworld TTS API – 3 akun
PRIMARY_INWORLD_API_KEY = os.getenv("PRIMARY_INWORLD_API_KEY", "")
BACKUP1_INWORLD_API_KEY = os.getenv("BACKUP1_INWORLD_API_KEY", "")
BACKUP2_INWORLD_API_KEY = os.getenv("BACKUP2_INWORLD_API_KEY", "")

# 4. Stability AI (SDXL) – 3 akun
PRIMARY_STABILITY_API_KEY = os.getenv("PRIMARY_STABILITY_API_KEY", "")
BACKUP1_STABILITY_API_KEY = os.getenv("BACKUP1_STABILITY_API_KEY", "")
BACKUP2_STABILITY_API_KEY = os.getenv("BACKUP2_STABILITY_API_KEY", "")

# 5. YouTube Data API – 3 akun
PRIMARY_YOUTUBE_DATA_API_KEY = os.getenv("PRIMARY_YOUTUBE_DATA_API_KEY", "")
BACKUP1_YOUTUBE_DATA_API_KEY = os.getenv("BACKUP1_YOUTUBE_DATA_API_KEY", "")
BACKUP2_YOUTUBE_DATA_API_KEY = os.getenv("BACKUP2_YOUTUBE_DATA_API_KEY", "")

class GlobalConfig(BaseModel):
    # 6. Niche YouTube
    youtube_niche: str = "AI & Automation for Productivity & Business"

    # 7. Video setting (Veo 3.1)
    long_300s_video_duration: int = 300
    shorts_video_duration: int = 30
    veo_video_resolution: str = "720p"

    # 8. Thumbnail (SDXL)
    sdxl_api_url: str = "https://api.stability.ai/v1/generation/stable-diffusion-xl-beta-v2-2-2/text-to-image"
    thumbnail_resolution: tuple = (1280, 720)
    thumbnail_dir: str = "thumbnails"

    # 9. Analytics (Veo 3.1 / YouTube Analytics)
    youtube_analytics_mindays: int = 1
    analytics_output_dir: str = "analytics"
    analytics_summary_csv: str = "analytics_summary.csv"
    analytics_reco_md: str = "optimization_recommendations.md"

    # 10. Directories
    markdown_dir: str = "output"
    topics_queue_path: str = "data/topics_queue.json"
    videos_long_dir: str = "videos/long"
    videos_shorts_dir: str = "videos/shorts"

    # 11. API Keys
    primary_llm_api_url: str = PRIMARY_LLAMA3_API_URL
    primary_llm_api_key: str = PRIMARY_LLAMA3_API_KEY
    backup1_llm_api_url: str = BACKUP1_LLAMA3_API_URL
    backup1_llm_api_key: str = BACKUP1_LLAMA3_API_KEY
    backup2_llm_api_url: str = BACKUP2_LLAMA3_API_URL
    backup2_llm_api_key: str = BACKUP2_LLAMA3_API_KEY

    primary_gemini_api_key: str = PRIMARY_GEMINI_API_KEY
    backup1_gemini_api_key: str = BACKUP1_GEMINI_API_KEY
    backup2_gemini_api_key: str = BACKUP2_GEMINI_API_KEY

    primary_inworld_api_key: str = PRIMARY_INWORLD_API_KEY
    backup1_inworld_api_key: str = BACKUP1_INWORLD_API_KEY
    backup2_inworld_api_key: str = BACKUP2_INWORLD_API_KEY

    primary_stability_api_key: str = PRIMARY_STABILITY_API_KEY
    backup1_stability_api_key: str = BACKUP1_STABILITY_API_KEY
    backup2_stability_api_key: str = BACKUP2_STABILITY_API_KEY

    primary_youtube_data_api_key: str = PRIMARY_YOUTUBE_DATA_API_KEY
    backup1_youtube_data_api_key: str = BACKUP1_YOUTUBE_DATA_API_KEY
    backup2_youtube_data_api_key: str = BACKUP2_YOUTUBE_DATA_API_KEY


# Inisialisasi global config
app_config = GlobalConfig()
