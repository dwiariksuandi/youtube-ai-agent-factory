from dotenv import load_dotenv
import os
load_dotenv('../.env')  # Load ROOT .env

class AppConfig:
    primary_llama3_api_key = os.getenv('PRIMARY_LLAMA3_API_KEY')
    backup1_llama3_api_key = os.getenv('BACKUP1_LLAMA3_API_KEY')
    primary_gemini_api_key = os.getenv('PRIMARY_GEMINI_API_KEY')
    primary_inworld_api_key = os.getenv('PRIMARY_INWORLD_API_KEY')
    primary_stability_api_key = os.getenv('PRIMARY_STABILITY_API_KEY')
    primary_youtube_data_api_key = os.getenv('PRIMARY_YOUTUBE_DATA_API_KEY')
    youtube_channel_id = os.getenv('YOUTUBE_CHANNEL_ID')
    # Add remaining 8 keys from .env
    openai_api_key = os.getenv('OPENAI_API_KEY', '')

# Test import
if __name__ == "__main__":
    print("✅ Config syntax OK")
    print("Keys loaded:", bool(AppConfig.primary_llama3_api_key))
