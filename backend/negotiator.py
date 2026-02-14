import os
import json
from typing import List, Dict, Optional
from openai import OpenAI
import schemas
from fastapi import HTTPException

def get_client_config():
    final_api_key = os.getenv("OPENAI_API_KEY")
    if final_api_key:
        final_api_key = final_api_key.strip()
        
    base_url = os.getenv("OPENAI_BASE_URL")
    model = os.getenv("OPENAI_MODEL", "gpt-3.5-turbo")

    if not final_api_key:
        raise ValueError("A chave da API não foi configurada.")

    # Auto-detect Groq key
    if final_api_key.startswith("gsk_"):
        if not base_url or "openai.com" in base_url:
            base_url = "https://api.groq.com/openai/v1"
            model = "llama-3.3-70b-versatile"
            
    return OpenAI(api_key=final_api_key, base_url=base_url), model

def analyze_mood(craving: str, mood: str) -> schemas.MoodAnalysisResponse:
    client, model = get_client_config()

    prompt = (
        f"O utilizador está com desejo de '{craving}' e sente-se '{mood}'. "
        "Atua como um assistente de decisão alimentar inteligente, empático e ALTAMENTE criativo (PT-PT). "
        "REGRAS IMPORTANTES: "
        "1. EVITA conselhos genéricos e repetitivos (como apenas 'beber água' ou 'esperar 10 minutos'). "
        "2. Fornece uma estratégia ÚNICA baseada especificamente na combinação do desejo e da emoção atual. "
        "3. Classifica o tipo de fome/impulso. "
        "4. Explica a raíz neurobiológica ou psicológica (ex: busca de magnésio, conforto familiar, regulação de cortisol). "
        "5. O tom deve ser de um especialista sofisticado. "
        "Retorna um objeto JSON com esta estrutura: "
        "{ "
        "  'mood_type': 'impulso emocional / fome física / recompensa', "
        "  'empathy_message': 'mensagem calorosa e profunda de apoio', "
        "  'explanation': 'explicação científica ou psicológica detalhada', "
        "  'eating_strategy': 'estratégia personalizada, inovadora e prática' "
        "}"
    )

    try:
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": "És um assistente nutricional sofisticado. Nunca dês a mesma resposta duas vezes. Sê variado e criativo. Responde sempre em Português de Portugal."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.9,
            response_format={"type": "json_object"}
        )
        data = json.loads(response.choices[0].message.content)
        return schemas.MoodAnalysisResponse(**data)
    except Exception as e:
        print(f"Erro na análise emocional: {e}")
        raise HTTPException(status_code=500, detail="Erro ao processar estado emocional.")

def negotiate_craving(craving: str, target_calories: int = 600, mood: Optional[str] = None) -> schemas.NegotiatorResponse:
    client, model = get_client_config()

    mood_context = f" O utilizador sente-se {mood}." if mood else ""
    
    prompt = (
        f"O utilizador está com um desejo de '{craving}'.{mood_context} "
        "REGRAS CRÍTICAS DE SEGURANÇA E VALIDAÇÃO: "
        "1. Se o pedido NÃO for comida real, ou se for ofensivo, sexual, perigoso, gíria inapropriada ou sem sentido, DEVES RECUSAR terminantemente. "
        "2. Se recusares, define 'recipe' como null e escreve uma mensagem educada em PT-PT explicando que apenas aceitas pedidos de alimentação saudável. "
        "3. Se for comida, atua como um Chef e Nutricionista de elite em Portugal (PT-PT). "
        "4. A receita deve ser GOURMET, única e nunca antes vista. Evita receitas padrão. "
        "5. A resposta deve seguir RIGOROSAMENTE esta estrutura JSON (NUNCA traduzas as chaves/keys): "
        "{ "
        "  'message': 'Mensagem carismática em PT-PT', "
        "  'recipe': { "
        "    'title': 'Nome da versão saudável', "
        "    'calories': 550, "
        "    'time_minutes': 35, "
        "    'ingredients': ['lista detalhada com quantidades'], "
        "    'steps': ['passos detalhados'] "
        "  }, "
        "  'restaurant_search_term': 'termo para mapa' "
        "}"
    )

    try:
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": "You are a world-class creative Chef. Every recipe you provide must be unique, gourmet, and healthy. Never repeat yourself. Always answer in Portuguese (Portugal). Return only valid JSON."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.9,
            response_format={"type": "json_object"}
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
