#!/usr/bin/env python3
"""
Voice Agent v1.0: Convert MD scripts → Human-like MP3 voiceover
Input: data/scripts/*.md → Output: data/audio/*.mp3
ElevenLabs API (free tier friendly)
"""

import os
import glob
import json
from datetime import datetime
from dotenv import load_dotenv
from elevenlabs.client import ElevenLabs
from elevenlabs import VoiceSettings, play

load_dotenv()

class VoiceAgent:
    def __init__(self):
        self.client = ElevenLabs(api_key=os.getenv('ELEVENLABS_API_KEY'))
        os.makedirs("data/audio", exist_ok=True)
        self.voice_id = "pNInz6obpgDQGcFmaJgB"  # Adam (natural male ID)
    
    def text_to_speech(self, text: str, output_file: str):
        """Convert text → MP3 with studio quality"""
        audio = self.client.generate(
            text=text,
            voice=self.voice_id,
            model="eleven_turbo_v2_5",  # Fast + high quality
            voice_settings=VoiceSettings(
                stability=0.5,
                similarity_boost=0.75,
                style=0.2,
                use_speaker_boost=True
            )
        )
        with open(output_file, "wb") as f:
            for chunk in audio:
                f.write(chunk)
        print(f"🎙️ Generated: {output_file}")
    
    def process_scripts(self):
        """Pipeline: Load latest MD scripts → MP3 batch"""
        script_files = sorted(glob.glob("data/scripts/*.md"), reverse=True)[:3]  # Latest 3
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M')
        
        for script_file in script_files:
            filename = os.path.basename(script_file)
            base_name = filename.replace('.md', f'_{timestamp}')
            mp3_file = f"data/audio/voice_{base_name}.mp3"
            
            with open(script_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Extract main content (skip metadata)
            main_content = content.split('**CTA')[0]  # Up to CTA
            
            self.text_to_speech(main_content, mp3_file)
        
        print(f"\n✅ VOICE AGENT COMPLETE: {len(script_files)} MP3 files ready!")
        print("📁 Next: Video Agent #4")

def main():
    print("🎙️ VOICE AGENT v1.0 - ElevenLabs TTS Factory")
    agent = VoiceAgent()
    agent.process_scripts()

if __name__ == "__main__":
    main()
