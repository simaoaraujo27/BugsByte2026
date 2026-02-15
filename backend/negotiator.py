import os
import json
import random
from typing import List, Dict, Optional
from openai import OpenAI
import schemas
import food_data
from fastapi import HTTPException
from llm_client import get_client_config, get_chat_completion

def analyze_mood(craving: str, mood: str) -> schemas.MoodAnalysisResponse:
    prompt = (
        f"User craving: '{craving}', Mood: '{mood}'. "
        "Atua como um assistente de decisão alimentar inteligente e empático (PT-PT). "
        "VALIDAÇÃO: Se o desejo for algo não comestível, recusa educadamente. "
        "Retorna JSON: { 'mood_type': '...', 'empathy_message': '...', 'explanation': '...', 'eating_strategy': '...' }"
    )
    try:
        response = get_chat_completion(
            messages=[{"role": "system", "content": "És um assistente sofisticado. Responde em PT-PT. Retorna APENAS JSON."},
                      {"role": "user", "content": prompt}],
            temperature=0.7,
            response_format={"type": "json_object"},
            max_tokens=300
        )
        return schemas.MoodAnalysisResponse(**json.loads(response.choices[0].message.content))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

def negotiate_craving(craving: str, target_calories: int = 600, mood: Optional[str] = None, favorite_recipes: List[schemas.Recipe] = [], allergens: List[str] = []) -> schemas.NegotiatorResponse:
    cuisine_focus = random.choice(["mediterrânica", "asiática leve", "mexicana equilibrada", "portuguesa moderna", "levantina"])
    technique_focus = random.choice(["forno", "grelhar", "saltear rápido", "estufar leve", "air fryer"])
    format_focus = random.choice(["bowl", "wrap", "prato no prato", "salada morna", "tosta aberta"])
    
    # FAVORITES: used only as subtle inspiration
    style_inspiration = ""
    if favorite_recipes:
        sampled = random.sample(favorite_recipes, k=min(2, len(favorite_recipes)))
        fav_list = ", ".join([r.name for r in sampled])
        style_inspiration = f"Se possível, podes inspirar-te levemente no perfil de sabor destes pratos: {fav_list}. MAS PRIORIZA TOTALMENTE O PEDIDO DO USER."

    allergen_context = ""
    if allergens:
        allergen_list = ", ".join(allergens)
        allergen_context = f"AVISO DE ALERGIA: O utilizador é alérgico a: {allergen_list}. PROIBIDO usar estes ingredientes.\n"

    prompt = (
        "OBJETIVO: Criar uma receita saudável que cumpra OBRIGATORIAMENTE o desejo do utilizador.\n"
        f"DESEJO MANDATÓRIO DO UTILIZADOR: '{craving}'\n"
        f"ESTADO EMOCIONAL: {mood or 'Normal'}\n"
        f"{allergen_context}"
        "\nFILTRO DE SEGURANÇA E VALIDAÇÃO:\n"
        "0. ANTES DE TUDO: Avalia se o pedido é comida real. Se o pedido for sem sentido, calão não relacionado com comida, objetos, ou qualquer coisa que não seja claramente um prato ou ingrediente, deves OBRIGATORIAMENTE definir 'recipe' como null.\n"
        "0.1. PROIBIDO TENTAR ADIVINHAR: Não tentes encontrar semelhanças fonéticas ou interpretar termos estranhos para 'forçar' uma ligação a comida (ex: se o user pedir algo que não conheces, não inventes que é uma proteína ou prato regional). Se não tens 100% de certeza que é comida, recusa.\n"
        "0.2. Se recusares, a 'message' deve ser apenas uma explicação curta de que o pedido não foi reconhecido como um alimento válido. NUNCA dês uma receita alternativa se o pedido original for inválido.\n"
        "\nINSTRUÇÕES DE CUMPRIMENTO ESTRITO (apenas para comida reconhecida):\n"
        "1. Se passar o filtro acima, é PROIBIDO alterar o prato base. Se o utilizador pediu Sushi, a receita TEM de ser de Sushi. Se pediu Pizza, TEM de ser Pizza.\n"
        "2. A criatividade deve ser aplicada APENAS para tornar o prato pedido mais saudável, MAS NUNCA para mudar o tipo de comida.\n"
        "3. Ignora sugestões de 'Estilo' ou 'Inspiração' se estas entrarem em conflito com o prato mandatório.\n"
        "4. Responde sempre em PORTUGUÊS DE PORTUGAL (PT-PT).\n"
        "5. PROIBIDO usar quinoa/qinoa.\n"
        f"\nNOTAS ADICIONAIS (Secundárias):\n"
        f"- Estilo: {cuisine_focus}, técnica {technique_focus}, formato {format_focus}.\n"
        f"- {style_inspiration}\n"
        "\nRetorna JSON:\n"
        "{ 'message': '...', 'recipe': { 'title': '...', 'calories': 0, 'time_minutes': 30, 'ingredients': ['...'], 'steps': [] } ou null, 'restaurant_search_term': '...' }"
    )

    strict_json_rules = (
        "\nREGRAS JSON ESTRITAS: "
        "Retorna APENAS JSON válido, sem markdown e sem texto fora do objeto. "
        "Em 'ingredients' e 'steps', cada item deve ser APENAS uma string simples. "
        "NÃO uses quinoa/qinoa."
    )

    def request_recipe_response(temp: float, presence: float, frequency: float, strict_mode: bool = False):
        system_content = (
            "És um Chef Michelin e Nutricionista PT-PT que adora variedade alta, pouca repetição e quantidades realistas por ingrediente. Quinoa/qinoa é proibida."
        )
        user_content = prompt + (strict_json_rules if strict_mode else "")
        # Note: presence and frequency penalties are not currently supported by get_chat_completion helper, 
        # but we prioritize resilience over these specific penalties for now.
        response = get_chat_completion(
            messages=[
                {"role": "system", "content": system_content},
                {"role": "user", "content": user_content}
            ],
            temperature=temp,
            response_format={"type": "json_object"},
            max_tokens=1000
        )
        return json.loads(response.choices[0].message.content)

    try:
        data = request_recipe_response(temp=1.08, presence=0.9, frequency=0.8, strict_mode=False)
    except Exception as first_error:
        error_text = str(first_error).lower()
        should_retry = "json_validate_failed" in error_text or "failed to generate json" in error_text
        if not should_retry:
            print(f"Erro Negotiator: {first_error}")
            raise HTTPException(status_code=500, detail="Erro ao processar receita personalizada.")
        try:
            data = request_recipe_response(temp=0.65, presence=0.35, frequency=0.35, strict_mode=True)
        except Exception as retry_error:
            print(f"Erro Negotiator (retry): {retry_error}")
            raise HTTPException(status_code=500, detail="Erro ao processar receita personalizada.")
    try:
        
        # Calcular calorias reais via "food_data" (que usa a IA como DB)
        raw_recipe = data.get('recipe')
        if raw_recipe:
            # FIX: Ensure steps are always strings
            if 'steps' in raw_recipe and isinstance(raw_recipe['steps'], list):
                sanitized_steps = []
                for step in raw_recipe['steps']:
                    if isinstance(step, dict):
                        # Convert dict to string (e.g. {'acao': '...', 'tempo': 1} -> '...')
                        sanitized_steps.append(step.get('acao', str(step)))
                    else:
                        sanitized_steps.append(str(step))
                raw_recipe['steps'] = sanitized_steps

            real_calories = food_data.calculate_recipe_calories(raw_recipe.get('ingredients', []))
            if real_calories > 0:
                raw_recipe['calories'] = real_calories

        return schemas.NegotiatorResponse(
            original_craving=craving,
            message=data.get('message', ''),
            recipe=schemas.NegotiatorRecipe(**raw_recipe) if raw_recipe else None,
            restaurant_search_term=data.get('restaurant_search_term') or craving
        )
    except Exception as e:
        print(f"Erro Negotiator: {e}")
        raise HTTPException(status_code=500, detail="Erro ao processar receita personalizada.")

def analyze_nutrition(food_text: str) -> schemas.NutritionAnalysisResponse:
    prompt = (
        f"Analisa a informação nutricional para: '{food_text}'. "
        "Estima as calorias e macronutrientes totais para a quantidade indicada. "
        "Se a quantidade não for explícita, assume uma porção padrão média (ex: 1 banana = 120g). "
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
        "  'estimated_grams': 100 "
        "}"
    )

    try:
        response = get_chat_completion(
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
