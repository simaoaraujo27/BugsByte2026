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
    if final_api_key and final_api_key.startswith("gsk_"):
        model = "llama-3.2-11b-vision-preview"
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
        "\nRetorna JSON: { 'detected_ingredients': [], 'message': '...', 'recipe': { 'title': '...', 'calories': 450, 'time_minutes': 25, 'ingredients': [], 'steps': [] } }"
    )

    try:
        response = client.chat.completions.create(
            model=model,
            messages=[{
                "role": "user",
                "content": [
                    {"type": "text", "text": prompt},
                    {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"}}
                ]
            }],
            temperature=0.5,
            response_format={"type": "json_object"}
        )
        data = json.loads(response.choices[0].message.content)
        return schemas.VisionResponse(
            detected_ingredients=data.get('detected_ingredients', []),
            message=data.get('message', ''),
            recipe=schemas.NegotiatorRecipe(**data.get('recipe', {}))
        )
    except Exception as e:
        print(f"Erro Vision: {e}")
        raise HTTPException(status_code=500, detail="Erro na análise visual personalizada.")
