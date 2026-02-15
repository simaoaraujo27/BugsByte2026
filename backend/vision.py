import os
import json
import base64
import random
from typing import List, Optional
from openai import OpenAI
import schemas
import food_data
from fastapi import HTTPException, status
from llm_client import get_client_config

def analyze_image_ingredients(image_bytes: bytes, mode: str = "ingredients", api_key: Optional[str] = None, favorite_recipes: List[schemas.Recipe] = [], allergens: List[str] = []) -> schemas.VisionResponse:
    client, model = get_client_config()
    cuisine_focus = random.choice(["mediterrânica", "asiática leve", "mexicana equilibrada", "portuguesa moderna", "levantina"])
    technique_focus = random.choice(["forno", "grelhar", "saltear rápido", "estufar leve", "air fryer"])
    format_focus = random.choice(["bowl", "wrap", "prato no prato", "salada morna", "tosta aberta"])
    
    # Check if we are using Groq
    is_groq = "groq" in str(client.base_url)
    
    # Override model for Groq Vision if needed
    if is_groq:
         model = "meta-llama/llama-4-scout-17b-16e-instruct"

    base64_image = base64.b64encode(image_bytes).decode('utf-8')

    # FAVORITES: subtle and low-weight style reference
    fav_header = ""
    if favorite_recipes:
        sampled = random.sample(favorite_recipes, k=min(2, len(favorite_recipes)))
        fav_list = "\n".join([f"- {r.name}" for r in sampled])
        fav_header = (
            "REFERÊNCIA DE ESTILO (influência leve):\n"
            "Usa APENAS para toque subtil de sabor. NÃO copies pratos favoritos nem títulos iguais.\n"
            f"{fav_list}\n\n"
        )

    allergen_context = ""
    if allergens:
        allergen_list = ", ".join(allergens)
        allergen_context = f"AVISO DE ALERGIA: O utilizador é alérgico a: {allergen_list}. NÃO uses estes ingredientes na receita.\n\n"

    if mode == "plate":
        prompt = (
            f"{fav_header}"
            f"{allergen_context}"
            f"BRIEF CRIATIVO DESTA GERAÇÃO: cozinha {cuisine_focus}, técnica {technique_focus}, formato {format_focus}. "
            "Analisa esta imagem de um prato já cozinhado.\n"
            "0. VALIDAÇÃO: Se a imagem NÃO for de um prato de comida ou for algo não comestível (ex: objetos, eletrónicos, lixo, etc), define 'recipe' como null e explica na 'message' em PT-PT que não detetaste um prato de comida válido.\n"
            "1. Identifica o nome do prato (ex: Lasanha, Sushi, Hambúrguer).\n"
            "2. Cria uma RECRIAÇÃO SAUDÁVEL desse exato prato. Não inventes uma receita aleatória; foca-te em tornar o prato da imagem mais nutritivo.\n"
            "3. Se houver ALERGÉNIOS listados acima, substitui-os por alternativas seguras.\n"
            "4. Responde sempre em PORTUGUÊS DE PORTUGAL (PT-PT).\n"
            "5. Em 'ingredients', usa quantidades realistas por ingrediente.\n"
            "6. PROIBIDO usar quinoa/qinoa.\n"
            "IMPORTANTE: Responde APENAS com um objeto JSON válido. Define 'calories' como 0. "
            "\nEstrutura JSON: { \"detected_ingredients\": [\"nome do prato\"], \"message\": \"...\", \"recipe\": { \"title\": \"Versão Saudável de...\", \"calories\": 0, \"time_minutes\": 25, \"ingredients\": [\"...\"], \"steps\": [] } ou null }"
        )
    else:
        prompt = (
            f"{fav_header}"
            f"{allergen_context}"
            f"BRIEF CRIATIVO DESTA GERAÇÃO: cozinha {cuisine_focus}, técnica {technique_focus}, formato {format_focus}. "
            "Analisa esta imagem de ingredientes.\n"
            "0. VALIDAÇÃO: Se a imagem NÃO contiver ingredientes alimentares ou se os objetos presentes não fizerem sentido para cozinhar (ex: ferramentas, pedras, objetos aleatórios), define 'recipe' como null e explica na 'message' em PT-PT que não detetaste ingredientes válidos para criar uma receita.\n"
            "1. Identifica os ingredientes presentes.\n"
            "2. Cria uma receita saudável que combine estes ingredientes.\n"
            "3. Se houver ALERGÉNIOS listados acima, IGNORA-OS TOTALMENTE e não os uses na receita.\n"
            "4. Responde em PT-PT.\n"
            "5. Em 'ingredients', usa quantidades realistas por ingrediente.\n"
            "6. PROIBIDO usar quinoa/qinoa.\n"
            "IMPORTANTE: Responde APENAS com um objeto JSON válido. Define 'calories' como 0. "
            "\nEstrutura JSON: { \"detected_ingredients\": [], \"message\": \"...\", \"recipe\": { \"title\": \"...\", \"calories\": 0, \"time_minutes\": 25, \"ingredients\": [\"...\"], \"steps\": [] } ou null }"
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
                {"role": "system", "content": "És um Chef Michelin e Nutricionista PT-PT que prioriza variedade alta, pouca repetição e quantidades realistas por ingrediente. Quinoa/qinoa é proibida."},
                {"role": "user", "content": [
                    {"type": "text", "text": prompt},
                    {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"}}
                ]}
            ],
            temperature=1.08,
            presence_penalty=0.9,
            frequency_penalty=0.8,
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
            recipe=schemas.NegotiatorRecipe(**raw_recipe) if raw_recipe else None
        )
    except Exception as e:
        error_text = str(e).lower()
        status_code = getattr(e, "status_code", None)
        if (
            status_code == status.HTTP_413_REQUEST_ENTITY_TOO_LARGE
            or "request_too_large" in error_text
            or "request entity too large" in error_text
        ):
            raise HTTPException(
                status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                detail="A imagem enviada é demasiado grande para análise. Tenta novamente com uma imagem mais leve."
            )
        print(f"Erro Vision ({model}): {e}")
        if 'content' in locals():
            print(f"Raw content from model: {content}")
        raise HTTPException(status_code=500, detail=f"Erro na análise visual: {str(e)}")
