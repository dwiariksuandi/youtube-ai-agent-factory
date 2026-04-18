#!/usr/bin/env python3
"""
Thumbnail Agent v1.0: AI-generated YouTube thumbnails (SDXL Turbo)
Input: topics/scripts → Output: data/thumbs/*.jpg
"""

import os
import glob
import json
from datetime import datetime
from PIL import Image, ImageDraw, ImageFont
from typing import List

class ThumbnailAgent:
    def __init__(self):
        os.makedirs("data/thumbs", exist_ok=True)
    
    def generate_thumbnail_prompts(self, topic_title: str) -> List[str]:
        """SDXL-optimized prompts untuk high-CTR thumbnails"""
        base_prompts = [
            f"Professional YouTube thumbnail {topic_title}, cinematic lighting, bold red text overlay, high contrast, 1280x720, Indonesian audience, viral style",
            f"Clickbait YouTube thumbnail {topic_title}, shocked face emoji, number 10 in gold, gradient background, 16:9, ultra detailed",
            f"Clean tech tutorial thumbnail {topic_title}, laptop screen with AI code, blue neon glow, modern UI, perfect composition"
        ]
        return base_prompts
    
    def create_mock_thumbnail(self, topic_title: str, output_file: str):
        """Simulate Stability AI SDXL output (real API later)"""
        # Create mock high-quality thumbnail
        img = Image.new('RGB', (1280, 720), color=(36, 36, 60))  # Dark tech bg
        draw = ImageDraw.Draw(img)
        
        # Bold title text
        try:
            font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 80)
        except:
            font = ImageFont.load_default()
        
        # Title wrap
        title = topic_title[:60] + "..." if len(topic_title) > 60 else topic_title
        draw.text((50, 200), title, fill=(255, 215, 0), font=font, stroke_width=3, stroke_fill=(0,0,0))
        
        # CTR elements
        draw.text((50, 450), "🚀 2026 AI HACKS", fill=(255, 255, 255), font=ImageFont.load_default())
        draw.text((50, 550), "10x Produktivitas", fill=(0, 255, 150), font=ImageFont.load_default())
        
        img.save(output_file, quality=95)
        print(f"🖼️ Thumbnail: {output_file} (1280x720 - CTR optimized)")
    
    def process_topics(self):
        """Batch generate thumbnails from latest topics"""
        topic_files = glob.glob("data/topics/*.json")
        if not topic_files:
            print("⚠️ No topics found - run idea_agent first")
            return
        
        latest_topic_file = sorted(topic_files)[-1]
        with open(latest_topic_file, 'r') as f:
            topics = json.load(f)
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M')
        
        for i, topic in enumerate(topics[:3]):  # 3 thumbnails
            filename = f"thumb_{topic['type']}_{timestamp}_{i+1:02d}.jpg"
            output_file = f"data/thumbs/{filename}"
            
            self.create_mock_thumbnail(topic['title'], output_file)
        
        print(f"\n✅ THUMBNAIL AGENT COMPLETE: {len(topics[:3])} high-CTR JPGs!")
        print("🎯 Real: Stability AI API → production quality")

def main():
    print("🖼️ THUMBNAIL AGENT v1.0 - SDXL CTR-Killer Factory")
    agent = ThumbnailAgent()
    agent.process_topics()

if __name__ == "__main__":
    main()
