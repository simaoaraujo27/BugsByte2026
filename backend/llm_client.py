import os
from openai import OpenAI
import time

def get_client_config():
    api_key = os.getenv("OPENAI_API_KEY")
    if api_key:
        api_key = api_key.strip()
        
    base_url = os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1")
    model = os.getenv("OPENAI_MODEL", "gpt-4o-mini")

    if api_key and api_key.startswith("gsk_"):
        base_url = "https://api.groq.com/openai/v1"
        # Primary model
        if not os.getenv("OPENAI_MODEL"):
            model = "llama-3.3-70b-versatile"
            
    return OpenAI(api_key=api_key, base_url=base_url), model

def get_chat_completion(messages, temperature=0.3, response_format=None, max_tokens=500):
    client, model = get_client_config()
    
    # List of models to try in case of rate limits (especially for Groq)
    models_to_try = [model]
    if "groq" in client.base_url.host.lower():
        if model == "llama-3.3-70b-versatile":
            models_to_try.append("llama-3.1-8b-instant")
            models_to_try.append("mixtral-8x7b-32768")
        elif model != "llama-3.1-8b-instant":
            models_to_try.append("llama-3.1-8b-instant")

    last_exception = None
    for current_model in models_to_try:
        try:
            response = client.chat.completions.create(
                model=current_model,
                messages=messages,
                temperature=temperature,
                response_format=response_format,
                max_tokens=max_tokens
            )
            return response
        except Exception as e:
            last_exception = e
            # If it's a rate limit error (429), try the next model
            if "429" in str(e) or "rate_limit_exceeded" in str(e).lower():
                print(f"Rate limit hit for {current_model}, trying next model...")
                continue
            else:
                # For other errors, raise immediately
                raise e
    
    # If all models failed
    raise last_exception
