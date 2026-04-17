#!/usr/bin/env python3
"""
Idea Agent v1.0: Generate high-CTR YouTube topics (AI/Productivity niche)
No API key required for initial test - simulated trending data
"""

import os
import json
from datetime import datetime
from typing import List, Dict
import pandas as pd
from pytrends.request import TrendReq

os.makedirs("data/topics", exist_ok=True)

class IdeaAgent:
    def __init__(self):
        try:
            self.pytrends = TrendReq(hl='id-ID', tz=420)  # WIB
        except:
            print("⚠️ pytrends offline - using simulated data")
            self.pytrends = None
    
    def get_simulated_trending_topics(self) -> Dict:
        """Simulated high-CTR topics untuk testing (no API needed)"""
        topics_long = [
            {"title": "Cara AI Agent Otomatisasi Bisnis 100% - No Code Tutorial", "ctr_score": 92, "type": "long", "timestamp": "20260418"},
            {"title": "10 Tools AI Gratis Terbaik 2026 untuk Produktivitas", "ctr_score": 88, "type": "long", "timestamp": "20260418"},
            {"title": "Bangun AI Factory Sendiri - Full Tutorial Llama 3", "ctr_score": 95, "type": "long", "timestamp": "20260418"},
        ]
        
        topics_shorts = [
            {"title": "AI Hemat 10 Jam/Minggu #shorts", "ctr_score": 97, "type": "shorts", "timestamp": "20260418"},
            {"title": "1 Tool AI Ubah Bisnis Anda #productivity", "ctr_score": 94, "type": "shorts", "timestamp": "20260418"},
        ]
        
        return {
            "long_topics": topics_long,
            "shorts_topics": topics_shorts,
            "generated_at": datetime.now().isoformat(),
            "niche": "AI & Automation Productivity Indonesia"
        }
    
    def get_trending_topics(self) -> Dict:
        """Production: Google Trends + YouTube API"""
        if self.pytrends:
            self.pytrends.build_payload(['AI productivity', 'automation bisnis'], timeframe='today 7-d', geo='ID')
            df = self.pytrends.interest_over_time()
            print(f"✅ Trends data: {df.head()}")
        
        # Return simulated untuk instant test
        return self.get_simulated_trending_topics()
    
    def save_topics(self, data: Dict):
        """Save structured JSON output"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M')
        
        long_file = f"data/topics/topics_long_{timestamp}.json"
        shorts_file = f"data/topics/topics_shorts_{timestamp}.json"
        
        # Save long topics
        with open(long_file, 'w', encoding='utf-8') as f:
            json.dump(data['long_topics'], f, indent=2, ensure_ascii=False)
        
        # Save shorts topics  
        with open(shorts_file, 'w', encoding='utf-8') as f:
            json.dump(data['shorts_topics'], f, indent=2, ensure_ascii=False)
        
        print(f"🎯 SAVED: {long_file} ({len(data['long_topics'])} Long topics)")
        print(f"🎯 SAVED: {shorts_file} ({len(data['shorts_topics'])} Shorts topics)")

def main():
    print("🚀 IDEA AGENT v1.0 - Generating trending topics...")
    agent = IdeaAgent()
    topics = agent.get_trending_topics()
    agent.save_topics(topics)
    print("✅ IDEA AGENT COMPLETE - Ready for Script Agent #2")

if __name__ == "__main__":
    main()
