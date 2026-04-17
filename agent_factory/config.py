from dotenv import load_dotenv
import os
load_dotenv('../.env')

class AppConfig:
    # LLM Chain (HF → OpenAI fallback)
    primary_llm_api_key = os.getenv('PRIMARY_LLAMA3_API_KEY') or os.getenv('OPENAI_API_KEY')
    primary_llm_url = "https://api-inference.huggingface.co/models/meta-llama/Meta-Llama-3.1-8B-Instruct"
    
    # YouTube
    youtube_api_key = os.getenv('PRIMARY_YOUTUBE_DATA_API_KEY')
    channel_id = os.getenv('YOUTUBE_CHANNEL_ID', 'YOUR_CHANNEL_ID')
    
    # Production Settings (Algorithm 2026)
    video_length_secs = 45  # Shorts sweet spot
    hook_duration = 3  # First 3s = 80% retention
    cta_end_screen = True
    
    # Viral Hooks Templates
    hooks = [
        "90% orang gagal karena...",
        "Rahasia yang disembunyikan Google...",
        "Cara hemat 10x lipat dalam 60 detik...",
        "Kesalahan fatal yang 99% lakukan..."
    ]
