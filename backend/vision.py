import os
import json
import base64
from typing import List, Optional
from openai import OpenAI
import schemas
from fastapi import HTTPException

def analyze_image_ingredients(image_bytes: bytes, api_key: Optional[str] = None) -> schemas.VisionResponse:
    final_api_key = api_key or os.getenv("OPENAI_API_KEY")
    if final_api_key:
        final_api_key = final_api_key.strip()
        
    base_url = os.getenv("OPENAI_BASE_URL")
    # Updated to the new Llama 4 Scout multimodal model
    model = "meta-llama/llama-4-scout-17b-16e-instruct"

    if not final_api_key:
        raise ValueError("A chave da API não foi configurada.")

    # Auto-detect Groq key and set appropriate base URL if not provided
    if final_api_key.startswith("gsk_") and (not base_url or "openai.com" in base_url):
        base_url = "https://api.groq.com/openai/v1"

    client = OpenAI(
        api_key=final_api_key,
        base_url=base_url
    )

    # Encode image to base64
    base64_image = base64.b64encode(image_bytes).decode('utf-8')

    prompt = (
        "Analisa esta imagem de ingredientes de cozinha. "
        "1. Identifica todos os ingredientes visíveis que podem ser usados numa receita. "
        "2. Cria uma receita saudável e criativa usando principalmente estes ingredientes (podes assumir ingredientes básicos de despensa como sal, azeite, especiarias). "
        "3. A resposta deve ser em Português de Portugal (PT-PT). "
        "4. Retorna RIGOROSAMENTE um objeto JSON com esta estrutura: "
        "{ "
        "  'detected_ingredients': ['ingrediente 1', 'ingrediente 2'], "
        "  'message': 'Um comentário encorajador do Chef sobre os ingredientes encontrados', "
        "  'recipe': { "
        "    'title': 'Nome da receita', "
        "    'calories': 450, "
        "    'time_minutes': 25, "
        "    'ingredients': ['lista completa com quantidades'], "
        "    'steps': ['passo 1', 'passo 2'] "
        "  } "
        "}"
    )

    try:
        response = client.chat.completions.create(
            model=model,
            messages=[
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": prompt},
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{base64_image}",
                            },
                        },
                    ],
                }
            ],
            temperature=0.5,
            response_format={"type": "json_object"}
        )
        
        content = response.choices[0].message.content
        data = json.loads(content)
        
        return schemas.VisionResponse(
            detected_ingredients=data.get('detected_ingredients', []),
            message=data.get('message', 'Encontrei excelentes ingredientes!'),
            recipe=schemas.Recipe(**data.get('recipe', {}))
        )
    except Exception as e:
        print(f"Erro na análise de imagem: {e}")
        raise HTTPException(status_code=500, detail=f"Erro ao analisar imagem: {str(e)}")
