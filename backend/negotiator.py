import os
import json
from typing import List, Dict, Optional
from openai import OpenAI
import schemas
from fastapi import HTTPException
from llm_client import get_client_config

def analyze_mood(craving: str, mood: str) -> schemas.MoodAnalysisResponse:
    client, model = get_client_config()
    prompt = (
        f"User craving: '{craving}', Mood: '{mood}'. "
        "Atua como um assistente de decisão alimentar inteligente e empático (PT-PT). "
        "VALIDAÇÃO: Se o desejo for algo não comestível, recusa educadamente. "
        "Retorna JSON: { 'mood_type': '...', 'empathy_message': '...', 'explanation': '...', 'eating_strategy': '...' }"
    )
    try:
        response = client.chat.completions.create(
            model=model,
            messages=[{"role": "system", "content": "És um assistente sofisticado. Responde em PT-PT. Retorna APENAS JSON."},
                      {"role": "user", "content": prompt}],
            temperature=0.7,
            response_format={"type": "json_object"},
            max_tokens=300
        )
        return schemas.MoodAnalysisResponse(**json.loads(response.choices[0].message.content))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

def negotiate_craving(craving: str, target_calories: int = 600, mood: Optional[str] = None, favorite_recipes: List[schemas.Recipe] = []) -> schemas.NegotiatorResponse:
    client, model = get_client_config()
    
    # FAVORITES: Construct context as subtle inspiration
    fav_header = ""
    if favorite_recipes:
        fav_list = "\n".join([f"- {r.name}" for r in favorite_recipes])
        fav_header = f"REFERÊNCIA DE ESTILO (Usa isto apenas como inspiração subtil para o tipo de cozinha que o utilizador gosta):\n{fav_list}\n\n"

    prompt = (
        f"{fav_header}"
        f"O utilizador enviou o seguinte: '{craving}'. Estado emocional: {mood}. "
        "\nINSTRUÇÕES: "
        "1. Se o utilizador descreveu um desejo específico, cria uma versão saudável. "
        "2. Se forneceu ingredientes, cria uma receita criativa com eles. "
        "3. Usa a lista de 'estilo' acima APENAS como base para o perfil de sabor, mas foca-te em ser VARIADO e ORIGINAL. Não sugiras sempre o mesmo tipo de prato. "
        "4. Se o pedido for inválido, define 'recipe' como null. "
        "\nRetorna RIGOROSAMENTE este JSON em PT-PT (define SEMPRE 'calories' como 0, pois eu vou calcular o valor real): "
        "{ 'message': '...', 'recipe': { 'title': '...', 'calories': 0, 'time_minutes': 30, 'ingredients': ['Lista em PT-PT'], 'ingredients_en': ['Lista em Inglês apenas para pesquisa técnica'], 'steps': [] }, 'restaurant_search_term': '...' }"
    )

    try:
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": "És um Chef Michelin e Nutricionista que adora variedade. Cria receitas novas e surpreendentes, usando as preferências do utilizador apenas como guia de estilo."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.85,
            response_format={"type": "json_object"},
            max_tokens=1000
        )
        data = json.loads(response.choices[0].message.content)
        
        # Integrar FatSecret para calorias mais precisas se possível
        raw_recipe = data.get('recipe')
        if raw_recipe and raw_recipe.get('ingredients'):
            fs_nutrition = food_data.get_nutrition_for_recipe(
                raw_recipe['ingredients'], 
                ingredients_en=raw_recipe.get('ingredients_en')
            )
            if fs_nutrition['calories'] > 0:
                raw_recipe['calories'] = int(fs_nutrition['calories'])

        return schemas.NegotiatorResponse(
            original_craving=craving,
            message=data.get('message', ''),
            recipe=schemas.NegotiatorRecipe(**raw_recipe) if raw_recipe else None,
            restaurant_search_term=data.get('restaurant_search_term', craving)
        )
    except Exception as e:
        print(f"Erro Negotiator: {e}")
        raise HTTPException(status_code=500, detail="Erro ao processar receita personalizada.")

def analyze_nutrition(food_text: str) -> schemas.NutritionAnalysisResponse:
    client, model = get_client_config()

    prompt = (
        f"Analisa a informação nutricional para: '{food_text}'. "
        "Estima as calorias e macronutrientes totais para a quantidade indicada. "
        "Se a quantidade não for explícita, assume uma porção padrão média. "
        "VALIDAÇÃO: Se o item indicado NÃO for um alimento ou for algo impossível de comer (ex: pedras, objetos), define 'is_food' como false e fornece uma 'error_message' explicativa em PT-PT. "
        "Responde APENAS com um objeto JSON com este formato (sem markdown): "
        "{ "
        "  'is_food': true, "
        "  'error_message': null, "
        "  'name': 'Nome curto e claro do alimento (PT-PT)', "
        "  'calories': 0, "
        "  'protein': 0.0, "
        "  'carbs': 0.0, "
        "  'fat': 0.0, "
        "  'estimated_grams': 0 "
        "}"
    )

    try:
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": "You are a nutritional expert API. Output valid JSON only."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3,
            response_format={"type": "json_object"}
        )
        content = response.choices[0].message.content
        data = json.loads(content)
        
        if not data.get("is_food", True):
            raise HTTPException(status_code=400, detail=data.get("error_message", "O item indicado não é um alimento válido."))
        
        return schemas.NutritionAnalysisResponse(
            food_text=food_text,
            is_food=True,
            name=data.get("name", food_text),
            calories=data.get("calories", 0),
            protein=data.get("protein", 0),
            carbs=data.get("carbs", 0),
            fat=data.get("fat", 0),
            estimated_grams=data.get("estimated_grams", 0)
        )
    except Exception as e:
        print(f"Erro na análise nutricional: {e}")
        raise HTTPException(status_code=500, detail=f"Erro ao analisar nutrição: {str(e)}")
