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

    # Force Groq for SPEED if key is available
    if api_key.startswith("gsk_"):
        base_url = "https://api.groq.com/openai/v1"
        model = "llama-3.3-70b-versatile"
            
    return OpenAI(api_key=api_key, base_url=base_url), model

def analyze_mood(craving: str, mood: str) -> schemas.MoodAnalysisResponse:
    client, model = get_client_config()

    prompt = (
        f"User craving: '{craving}', Mood: '{mood}'. "
        "Atua como um assistente de decisão alimentar inteligente e empático (PT-PT). "
        "VALIDAÇÃO: Se o desejo for algo não comestível (ex: pedras, objetos), recusa educadamente. "
        "Retorna JSON: { 'mood_type': '...', 'empathy_message': '...', 'explanation': '...', 'eating_strategy': '...' }"
    )

    try:
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": "És um assistente sofisticado e rápido. Responde em PT-PT. Retorna APENAS JSON."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            response_format={"type": "json_object"},
            max_tokens=300
        )
        data = json.loads(response.choices[0].message.content)
        return schemas.MoodAnalysisResponse(**data)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

def negotiate_craving(craving: str, target_calories: int = 600, mood: Optional[str] = None, favorite_recipes: List[schemas.Recipe] = []) -> schemas.NegotiatorResponse:
    client, model = get_client_config()
    
    # Format favorite recipes context
    fav_context = ""
    if favorite_recipes:
        fav_list = "\n".join([f"- {r.name}" for r in favorite_recipes])
        fav_context = f"\nO utilizador já gosta destas receitas:\n{fav_list}\nTenta seguir um estilo ou nível de sofisticação semelhante."

    prompt = (
        f"O utilizador quer: '{craving}'. Estado: {mood}. {fav_context}"
        "\nREGRAS CRÍTICAS: "
        "1. Se o pedido NÃO FOR COMIDA ou prato culinário, define 'recipe' como null e explica porquê na 'message'. "
        "2. Caso contrário, cria uma receita GOURMET saudável em PT-PT. "
        "3. Sê extremamente conciso mas profissional para garantir rapidez. "
        "Retorna JSON: { 'message': '...', 'recipe': { 'title': '...', 'calories': 500, 'time_minutes': 30, 'ingredients': [], 'steps': [] }, 'restaurant_search_term': '...' }"
    )

    try:
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": "You are a world-class creative Chef. Every recipe you provide must be unique, gourmet, and healthy. Always answer in Portuguese (Portugal). Return only valid JSON."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.9,
            response_format={"type": "json_object"},
            max_tokens=800
        )
        content = response.choices[0].message.content
        data = json.loads(content)
        
        try:
            return schemas.NegotiatorResponse(
                original_craving=craving,
                message=data.get('message', 'Aqui está uma alternativa saudável!'),
                recipe=schemas.NegotiatorRecipe(**data.get('recipe')) if data.get('recipe') else None,
                restaurant_search_term=data.get('restaurant_search_term', craving)
            )
        except Exception as ve:
            print(f"Erro de validação na resposta da AI: {ve}")
            return schemas.NegotiatorResponse(
                original_craving=craving,
                message="Desculpa, não consegui processar esse pedido de forma segura. Por favor, tenta outro prato real.",
                recipe=None,
                restaurant_search_term=craving
            )
    except Exception as e:
        print(f"Erro no negotiator: {e}")
        raise HTTPException(status_code=500, detail=f"Erro ao gerar receita: {str(e)}")
