from openai import OpenAI
from config import AppConfig
import json

config = AppConfig()
client = OpenAI(api_key=config.primary_llama3_api_key)

def generate_viral_idea(topic="AI Tools"):
    prompt = f"""
    Generate YouTube Shorts idea for "{topic}" that gets 10x views:
    1. HOOK (3s): Shocking stat/question
    2. VALUE: 1 actionable tip  
    3. CTA: Subscribe/comment
    
    Format JSON: {{"hook": "...", "content": "...", "cta": "...", "title": "...", "thumbnail_text": "..."}}
    """
    
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}]
    )
    
    idea = json.loads(response.choices[0].message.content)
    idea['timestamp'] = str(pd.Timestamp.now())
    return idea

if __name__ == "__main__":
    from rich import print
    idea = generate_viral_idea()
    print(idea)
    with open("../output/idea.json", "w") as f:
        json.dump(idea, f, indent=2)
