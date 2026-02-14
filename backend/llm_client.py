import os
from openai import OpenAI

def get_client_config():
    api_key = os.getenv("OPENAI_API_KEY")
    if api_key:
        api_key = api_key.strip()
        
    base_url = os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1")
    model = os.getenv("OPENAI_MODEL", "gpt-4o-mini")

    if api_key and api_key.startswith("gsk_"):
        base_url = "https://api.groq.com/openai/v1"
        model = "llama-3.3-70b-versatile"
            
    return OpenAI(api_key=api_key, base_url=base_url), model
