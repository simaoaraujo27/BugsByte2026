import os
import json
from typing import List, Dict, Optional
from openai import OpenAI
import schemas
from fastapi import HTTPException

def negotiate_craving(craving: str, target_calories: int = 600, api_key: Optional[str] = None) -> schemas.NegotiatorResponse:
    final_api_key = api_key or os.getenv("OPENAI_API_KEY")
    base_url = os.getenv("OPENAI_BASE_URL")
    model = os.getenv("OPENAI_MODEL", "gpt-3.5-turbo")

    if not final_api_key:
        raise ValueError("A chave da API OpenAI/Groq não foi configurada no ficheiro .env")

    # Auto-detect Groq key
    if final_api_key.startswith("gsk_") and not base_url:
        print("Auto-detected Groq key. Switching to Groq API.")
        base_url = "https://api.groq.com/openai/v1"
        model = "llama-3.3-70b-versatile"

    client = OpenAI(
        api_key=final_api_key,
        base_url=base_url
    )

    prompt = (
        f"O utilizador está com um desejo incontrolável de '{craving}'. O teu objetivo é negociar uma versão saudável de cerca de {target_calories} kcal. "
        "Atua como um Chef de Cozinha e Nutricionista de renome em Portugal (PT-PT). "
        "A receita deve ser EXTREMAMENTE detalhada e profissional. "
        "1. Cria uma versão 'Gourmet Saudável' do prato (DIY). "
        "2. Divide a resposta em secções claras: 'Ingredientes Necessários' (com quantidades precisas), 'Preparação dos Alimentos' e 'Instruções de Confeção Passo-a-Passo'. "
        "3. Adiciona uma secção de 'Dicas de Chef' para tornar o prato mais saboroso sem somar calorias. "
        "4. O tom deve ser motivador e sofisticado. "
        "Retorna um objeto JSON com esta estrutura: "
        "{ "
        "  'message': 'Uma resposta carismática e motivadora em PT-PT sobre como esta versão é superior ao desejo original', "
        "  'recipe': { "
        "    'title': 'Nome sofisticado da versão saudável', "
        "    'calories': 550, "
        "    'time_minutes': 35, "
        "    'ingredients': ['Lista exaustiva e detalhada com quantidades (ex: 200g de peito de frango)'], "
        "    'steps': ['Passo 1: Preparação detalhada...', 'Passo 2: Técnica de confeção...', 'Passo 3: Finalização e empratamento...', 'Dica Pro: ...'] "
        "  }, "
        "  'restaurant_search_term': 'termo de pesquisa para o mapa' "
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
        
        return schemas.NegotiatorResponse(
            original_craving=craving,
            message=data.get('message', 'Aqui está uma alternativa saudável!'),
            recipe=schemas.Recipe(**data.get('recipe', {})),
            restaurant_search_term=data.get('restaurant_search_term', craving)
        )
    except Exception as e:
        print(f"Erro no negotiator: {e}")
        # Re-raise the exception to be handled by the API layer
        raise HTTPException(status_code=500, detail=f"Erro ao gerar receita: {str(e)}")
