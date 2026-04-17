#!/usr/bin/env python3
"""
Script Agent v1.0: Generate YouTube scripts (Long + Shorts) 
Input: data/topics/*.json → Output: data/scripts/*.md
"""

import os
import json
import glob
from datetime import datetime
from jinja2 import Template
from typing import Dict, List

# Jinja2 Templates - YouTube Algorithm Optimized
LONG_TEMPLATE = """
# {{ title }}
**Hook (0:00-0:15)**: {{ hook }}

**Intro (0:15-1:00)**: {{ intro }}

## Tutorial Lengkap (1:00-{{ duration_min|default(12) }}:00)
### Step 1: {{ step1_title }}
{{ step1_content }}

### Step 2: {{ step2_title }}
{{ step2_content }}

{% if step3_title %}
### Step 3: {{ step3_title }}
{{ step3_content }}
{% endif %}

**Summary ({{ duration_min|default(12) }}-{{ (duration_min|default(12)) + 1 }}:00)**: {{ summary }}

**CTA (Akhir)**: {{ cta }}
👍 Like | 🔔 Subscribe | 💬 Comment: "{{ comment_prompt }}"
#{{ tags|join(' #') }}
"""

SHORTS_TEMPLATE = """
**0-3s HOOK**: {{ hook_short }}

**3-{{ duration_sec|default(45) }}s INSIGHT**: {{ insight }}

**CTA END**: {{ cta_short }}
#{{ tags|join(' #') }} #shorts
"""

class ScriptAgent:
    def __init__(self):
        os.makedirs("data/scripts", exist_ok=True)
        self.templates = {
            'long': Template(LONG_TEMPLATE),
            'shorts': Template(SHORTS_TEMPLATE)
        }
    
    def load_topics(self) -> List[Dict]:
        """Load latest topics JSON"""
        long_files = glob.glob("data/topics/topics_long_*.json")
        shorts_files = glob.glob("data/topics/topics_shorts_*.json")
        
        topics = []
        if long_files:
            with open(long_files[-1], 'r', encoding='utf-8') as f:
                topics.extend(json.load(f))
        if shorts_files:
            with open(shorts_files[-1], 'r', encoding='utf-8') as f:
                topics.extend(json.load(f))
        
        print(f"📥 Loaded {len(topics)} topics from JSON")
        return topics[:5]  # Batch pertama 5 topics
    
    def generate_script_content(self, topic: Dict) -> Dict:
        """AI-generated script structure (template-based)"""
        if topic['type'] == 'long':
            return {
                'title': topic['title'],
                'hook': f"Hampir 90% pebisnis gagal karena {topic['title'].lower()[:30]}...",
                'intro': f"Selamat datang di tutorial lengkap {topic['title']}. Hari ini kita bangun sistem AI otomatis!",
                'step1_title': 'Setup AI Agent',
                'step1_content': 'Langkah 1: Install Llama-3 via HuggingFace... (detail 300 kata)',
                'step2_title': 'Automation Workflow',
                'step2_content': 'Langkah 2: Connect YouTube API + pipeline... (detail 400 kata)',
                'step3_title': 'Deploy Production',
                'step3_content': 'Langkah 3: Codespaces + cron jobs... (detail 300 kata)',
                'summary': f"Ringkasan: {topic['title']} siap produksi dalam 30 menit!",
                'cta': 'Subscribe untuk 50+ tutorial AI gratis!',
                'comment_prompt': 'Tool AI mana favoritmu?',
                'tags': ['AI', 'Automation', 'Productivity', 'Bisnis', 'NoCode', '2026'],
                'duration_min': topic.get('duration_min', 12)
            }
        else:  # shorts
            return {
                'title': topic['title'],
                'hook_short': f"🤯 {topic['title'][:20]}...",
                'insight': f"Insight kunci: {topic['title']} hemat 10 jam/minggu!",
                'cta_short': 'Full tutorial di bio!',
                'tags': ['AI', 'Shorts', 'Productivity', 'Hack'],
                'duration_sec': topic.get('duration_sec', 45)
            }
    
    def render_script(self, topic: Dict, template_type: str) -> str:
        """Render Jinja2 template"""
        content = self.generate_script_content(topic)
        return self.templates[template_type].render(**content)
    
    def process_batch(self):
        """Main pipeline: topics → scripts"""
        topics = self.load_topics()
        timestamp = datetime.now().strftime('%Y%m%d_%H%M')
        
        for i, topic in enumerate(topics, 1):
            script_content = self.render_script(topic, topic['type'])
            filename = f"data/scripts/{topic['type']}_{timestamp}_{i:02d}.md"
            
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(script_content)
            
            print(f"✍️ Generated: {filename}")
        
        print(f"\n✅ SCRIPT AGENT COMPLETE: {len(topics)} scripts ready!")
        print("📁 Next: Voice Agent #3")

def main():
    agent = ScriptAgent()
    agent.process_batch()

if __name__ == "__main__":
    main()
