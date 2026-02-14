import os
import json
import base64
from typing import List, Optional
from openai import OpenAI
import schemas
from fastapi import HTTPException

def analyze_image_ingredients(image_bytes: bytes, api_key: Optional[str] = None, favorite_recipes: List[schemas.Recipe] = []) -> schemas.VisionResponse:
    final_api_key = api_key or os.getenv("OPENAI_API_KEY")
    if final_api_key:
        final_api_key = final_api_key.strip()
        
    base_url = os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1")
    
    # Se for Groq, precisamos de usar um modelo que suporte Visão
    is_groq = final_api_key and final_api_key.startswith("gsk_")
    if is_groq:
        model = "meta-llama/llama-4-scout-17b-16e-instruct"
        if "openai.com" in base_url:
            base_url = "https://api.groq.com/openai/v1"
    else:
        # Para OpenAI, o gpt-4o-mini já suporta visão
        model = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
        if "llama" in model.lower(): # Se o utilizador pôs um modelo llama na config geral da OpenAI (via Groq/Azure)
            model = "gpt-4o-mini" # Forçamos um modelo com visão

    client = OpenAI(api_key=final_api_key, base_url=base_url)
    base64_image = base64.b64encode(image_bytes).decode('utf-8')

    # FAVORITES FIRST
    fav_header = ""
    if favorite_recipes:
        fav_list = "\n".join([f"- {r.name}" for r in favorite_recipes])
        fav_header = f"CONTEXTO DE PREFERÊNCIAS DO UTILIZADOR (RECEITAS QUE ELE ADORA):\n{fav_list}\n\n"

    prompt = (
        f"{fav_header}"
        "Analisa esta imagem de ingredientes. "
        "1. Identifica os ingredientes. "
        "2. Cria uma receita saudável que combine com o estilo das receitas favoritas listadas acima. "
        "3. Responde em PT-PT. "
        "IMPORTANTE: Responde APENAS com um objeto JSON válido. "
        "\nEstrutura JSON esperada: { \"detected_ingredients\": [], \"message\": \"...\", \"recipe\": { \"title\": \"...\", \"calories\": 450, \"time_minutes\": 25, \"ingredients\": [], \"steps\": [] } }"
    )

    try:
        # Groq might have issues with response_format={"type": "json_object"} for some vision models
        # We'll rely on the prompt instruction for Groq
        extra_args = {}
        if not is_groq:
            extra_args["response_format"] = {"type": "json_object"}

        response = client.chat.completions.create(
            model=model,
            messages=[{
                "role": "user",
                "content": [
                    {"type": "text", "text": prompt},
                    {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"}}
                ]
            }],
            temperature=0.3,
            **extra_args
        )
        
        content = response.choices[0].message.content
        # Clean up possible markdown code blocks if the model included them
        if content.startswith("```json"):
            content = content.replace("```json", "", 1).replace("```", "", 1).strip()
        elif content.startswith("```"):
            content = content.replace("```", "", 1).replace("```", "", 1).strip()
            
        data = json.loads(content)
        return schemas.VisionResponse(
            detected_ingredients=data.get('detected_ingredients', []),
            message=data.get('message', ''),
            recipe=schemas.NegotiatorRecipe(**data.get('recipe', {}))
        )
    except Exception as e:
        print(f"Erro Vision ({model}): {e}")
        if 'content' in locals():
            print(f"Raw content from model: {content}")
        raise HTTPException(status_code=500, detail=f"Erro na análise visual: {str(e)}")
