from langchain_huggingface import HuggingFaceEndpoint
from dotenv import load_dotenv
import os

load_dotenv()
llm = None

def get_llama_instance():
    global llm
    if llm is None:
        llm = HuggingFaceEndpoint(
            repo_id="meta-llama/Llama-3-70b-chat-hf",
            huggingfacehub_api_token=os.getenv('HF_TOKEN'),
            temperature=0.7,
            max_new_tokens=2048
        )
    return llm
