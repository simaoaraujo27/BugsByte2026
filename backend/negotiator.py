import os
import json
from typing import List, Dict, Optional
from openai import OpenAI
import schemas
from fastapi import HTTPException

def get_client_config():
    api_key = os.getenv("OPENAI_API_KEY")
    if api_key:
        api_key = api_key.strip()
        
    base_url = os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1")
    model = os.getenv("OPENAI_MODEL", "gpt-4o-mini")

    if api_key.startswith("gsk_"):
        base_url = "https://api.groq.com/openai/v1"
        model = "llama-3.3-70b-versatile"
            
    return OpenAI(api_key=api_key, base_url=base_url), model

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
    
    # FAVORITES FIRST: Construct context
    fav_header = ""
    if favorite_recipes:
        fav_list = "\n".join([f"- {r.name}" for r in favorite_recipes])
        fav_header = f"CONTEXTO DE PREFERÊNCIAS DO UTILIZADOR (ESTAS SÃO AS RECEITAS QUE ELE MAIS GOSTA):\n{fav_list}\n\n"

    prompt = (
        f"{fav_header}"
        f"O utilizador tem agora um desejo de: '{craving}'. Estado emocional: {mood}. "
        "\nINSTRUÇÕES: "
        "1. Analisa as receitas favoritas acima para entender o paladar do utilizador. "
        "2. Cria uma NOVA receita GOURMET saudável que se alinhe com este perfil de gosto. "
        "3. Se o pedido for inválido (não comida), define 'recipe' como null. "
        "\nRetorna RIGOROSAMENTE este JSON em PT-PT: "
        "{ 'message': '...', 'recipe': { 'title': '...', 'calories': 500, 'time_minutes': 30, 'ingredients': [], 'steps': [] }, 'restaurant_search_term': '...' }"
    )

    try:
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": "És um Chef Michelin e Nutricionista. Prioriza sempre o perfil de gosto indicado pelas receitas favoritas do utilizador."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.85,
            response_format={"type": "json_object"},
            max_tokens=1000
        )
        data = json.loads(response.choices[0].message.content)
        return schemas.NegotiatorResponse(
            original_craving=craving,
            message=data.get('message', ''),
            recipe=schemas.NegotiatorRecipe(**data.get('recipe')) if data.get('recipe') else None,
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
