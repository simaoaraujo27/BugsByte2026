import os
import json
from typing import List, Dict, Optional
from openai import OpenAI
import schemas
from fastapi import HTTPException

def negotiate_craving(craving: str, target_calories: int = 600, api_key: Optional[str] = None) -> schemas.NegotiatorResponse:
    final_api_key = api_key or os.getenv("OPENAI_API_KEY")
    if final_api_key:
        final_api_key = final_api_key.strip()
        
    base_url = os.getenv("OPENAI_BASE_URL")
    model = os.getenv("OPENAI_MODEL", "gpt-3.5-turbo")

    if not final_api_key:
        raise ValueError("A chave da API OpenAI/Groq não foi configurada no ficheiro .env")

    # Auto-detect Groq key
    if final_api_key.startswith("gsk_"):
        if not base_url or "openai.com" in base_url:
            print("Auto-detected Groq key. Forcing Groq API configuration.")
            base_url = "https://api.groq.com/openai/v1"
            model = "llama-3.3-70b-versatile"

    client = OpenAI(
        api_key=final_api_key,
        base_url=base_url
    )

    prompt = (
        f"O utilizador está com um desejo de '{craving}'. "
        "REGRAS CRÍTICAS DE SEGURANÇA E VALIDAÇÃO: "
        "1. Se o pedido NÃO for comida real, ou se for ofensivo, sexual, perigoso, gíria inapropriada ou sem sentido, DEVES RECUSAR terminantemente. "
        "2. Se recusares, define 'recipe' como null e escreve uma mensagem educada em PT-PT explicando que apenas aceitas pedidos de alimentação saudável. "
        "3. Se for comida, atua como um Chef e Nutricionista de elite em Portugal (PT-PT). "
        "4. A resposta deve seguir RIGOROSAMENTE esta estrutura JSON (NUNCA traduzas as chaves/keys): "
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
                {"role": "system", "content": "You are a helpful nutritionist assistant. Always answer in Portuguese (Portugal). Return only valid JSON."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
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
        # Re-raise the exception to be handled by the API layer
        raise HTTPException(status_code=500, detail=f"Erro ao gerar receita: {str(e)}")
