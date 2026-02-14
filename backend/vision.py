import os
import json
import base64
from typing import List, Optional
from openai import OpenAI
import schemas
import food_data
from fastapi import HTTPException
from llm_client import get_client_config

def analyze_image_ingredients(image_bytes: bytes, mode: str = "ingredients", api_key: Optional[str] = None, favorite_recipes: List[schemas.Recipe] = []) -> schemas.VisionResponse:
    client, model = get_client_config()
    
    # Check if we are using Groq
    is_groq = "groq" in str(client.base_url)
    
    # Override model for Groq Vision if needed
    if is_groq:
         model = "meta-llama/llama-4-scout-17b-16e-instruct"

    base64_image = base64.b64encode(image_bytes).decode('utf-8')

    # FAVORITES: subtle style reference
    fav_header = ""
    if favorite_recipes:
        fav_list = "\n".join([f"- {r.name}" for r in favorite_recipes])
        fav_header = f"REFERÊNCIA DE ESTILO (Usa isto apenas como inspiração subtil para o tipo de pratos que o utilizador gosta):\n{fav_list}\n\n"

    if mode == "plate":
        prompt = (
            f"{fav_header}"
            "Analisa esta imagem de um prato já cozinhado. "
            "1. Identifica o nome do prato (ex: Lasanha, Sushi, Hambúrguer). "
            "2. Cria uma RECRIAÇÃO SAUDÁVEL desse exato prato. Não inventes uma receita aleatória; foca-te em tornar o prato da imagem mais nutritivo. "
            "3. Usa a lista de 'REFERÊNCIA DE ESTILO' apenas como inspiração. "
            "4. Responde sempre em PORTUGUÊS DE PORTUGAL (PT-PT). "
            "IMPORTANTE: Responde APENAS com um objeto JSON válido. Define 'calories' como 0. "
            "\nEstrutura JSON esperada: { \"detected_ingredients\": [\"nome do prato\"], \"message\": \"...\", \"recipe\": { \"title\": \"Versão Saudável de...\", \"calories\": 0, \"time_minutes\": 25, \"ingredients\": [\"200g massa\", \"100g carne\"], \"steps\": [] } }"
        )
    else:
        prompt = (
            f"{fav_header}"
            "Analisa esta imagem de ingredientes. "
            "1. Identifica os ingredientes presentes. "
            "2. Cria uma receita saudável que combine estes ingredientes. "
            "3. Usa a lista de 'REFERÊNCIA DE ESTILO' APENAS como base para o perfil de sabor, mas foca-te em ser VARIADO e ORIGINAL. "
            "4. Responde em PT-PT. "
            "IMPORTANTE: Responde APENAS com um objeto JSON válido. Define 'calories' como 0. "
            "\nEstrutura JSON esperada: { \"detected_ingredients\": [], \"message\": \"...\", \"recipe\": { \"title\": \"...\", \"calories\": 0, \"time_minutes\": 25, \"ingredients\": [\"200g de arroz\", \"1 tomate\"], \"steps\": [] } }"
        )

    try:
        # Groq might have issues with response_format={"type": "json_object"} for some vision models
        # We'll rely on the prompt instruction for Groq if needed, but let's try strict mode if not Groq
        extra_args = {}
        if not is_groq:
            extra_args["response_format"] = {"type": "json_object"}

        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": "És um Chef Michelin e Nutricionista PT-PT que adora variedade. Cria receitas novas e surpreendentes."},
                {"role": "user", "content": [
                    {"type": "text", "text": prompt},
                    {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"}}
                ]}
            ],
            temperature=0.9,
            presence_penalty=0.6,
            frequency_penalty=0.5,
            **extra_args
        )
        
        content = response.choices[0].message.content
        # Clean up possible markdown code blocks
        if content.startswith("```json"):
            content = content.replace("```json", "", 1).replace("```", "", 1).strip()
        elif content.startswith("```"):
            content = content.replace("```", "", 1).replace("```", "", 1).strip()
            
        data = json.loads(content)
        
        # Calcular calorias reais via "food_data" (que usa a IA como DB)
        raw_recipe = data.get('recipe', {})
        if raw_recipe:
            real_calories = food_data.calculate_recipe_calories(raw_recipe.get('ingredients', []))
            if real_calories > 0:
                raw_recipe['calories'] = real_calories

        return schemas.VisionResponse(
            detected_ingredients=data.get('detected_ingredients', []),
            message=data.get('message', ''),
            recipe=schemas.NegotiatorRecipe(**raw_recipe)
        )
    except Exception as e:
        print(f"Erro Vision ({model}): {e}")
        if 'content' in locals():
            print(f"Raw content from model: {content}")
        raise HTTPException(status_code=500, detail=f"Erro na análise visual: {str(e)}")
