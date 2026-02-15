import json
import random
import re
import unicodedata
from urllib.parse import quote_plus
from urllib.request import urlopen
from typing import List, Optional
import schemas
import food_data
from fastapi import HTTPException
from llm_client import get_chat_completion

MEALDB_BASE_URL = "https://www.themealdb.com/api/json/v1/1"
PT_STOPWORDS = {
    "de", "da", "do", "das", "dos", "com", "sem", "para", "uma", "um", "ao", "aos",
    "as", "os", "na", "no", "nas", "nos", "e", "ou", "quero", "fazer", "receita",
    "prato", "algo", "coisa", "tipo", "hoje", "jantar", "almoco", "almoço", "lanche"
}
PT_TO_EN_TERM_MAP = {
    "frango": "chicken",
    "carne": "beef",
    "porco": "pork",
    "peixe": "fish",
    "atum": "tuna",
    "camarao": "shrimp",
    "camarão": "shrimp",
    "arroz": "rice",
    "massa": "pasta",
    "batata": "potato",
    "ovo": "egg",
    "ovos": "egg",
    "queijo": "cheese",
    "cebola": "onion",
    "alho": "garlic",
    "tomate": "tomato",
    "limao": "lemon",
    "coentro": "coriander",
    "salsa": "parsley",
    "pimento": "pepper",
}


def _normalize_text(value: str) -> str:
    if not value:
        return ""
    normalized = unicodedata.normalize("NFKD", value).encode("ascii", "ignore").decode("ascii")
    return normalized.lower().strip()


def _extract_query_terms(craving: str) -> list[str]:
    normalized = _normalize_text(craving)
    tokens = re.findall(r"[a-z0-9]{3,}", normalized)
    terms = []
    for token in tokens:
        if token in PT_STOPWORDS:
            continue
        if token not in terms:
            terms.append(token)
    return terms[:8]


def _to_en_term(term: str) -> str:
    return PT_TO_EN_TERM_MAP.get(_normalize_text(term), _normalize_text(term))


def _expand_terms_for_api(terms: list[str]) -> list[str]:
    expanded: list[str] = []
    for term in terms:
        normalized = _normalize_text(term)
        translated = _to_en_term(term)
        if normalized and normalized not in expanded:
            expanded.append(normalized)
        if translated and translated not in expanded:
            expanded.append(translated)
    return expanded


def _safe_fetch_json(url: str) -> dict:
    try:
        with urlopen(url, timeout=6) as response:
            payload = response.read().decode("utf-8")
        data = json.loads(payload)
        return data if isinstance(data, dict) else {}
    except Exception:
        return {}


def _get_meal_details(meal_id: str) -> Optional[dict]:
    data = _safe_fetch_json(f"{MEALDB_BASE_URL}/lookup.php?i={quote_plus(str(meal_id))}")
    meals = data.get("meals") if isinstance(data, dict) else None
    if not meals:
        return None
    return meals[0]


def _extract_meal_ingredients(meal: dict) -> list[str]:
    ingredients: list[str] = []
    for i in range(1, 21):
        ingredient = str(meal.get(f"strIngredient{i}", "")).strip()
        measure = str(meal.get(f"strMeasure{i}", "")).strip()
        if not ingredient:
            continue
        if ingredient.lower() in {"none", "null"}:
            continue
        entry = f"{measure} {ingredient}".strip()
        ingredients.append(entry)
    return ingredients


def _contains_allergen(ingredients: list[str], allergens: list[str]) -> bool:
    if not allergens:
        return False
    normalized_ingredients = [_normalize_text(item) for item in ingredients]
    normalized_allergens = [_normalize_text(item) for item in allergens if item]
    for allergen in normalized_allergens:
        if not allergen:
            continue
        for ingredient in normalized_ingredients:
            if allergen in ingredient:
                return True
    return False


def _score_meal_for_query(meal: dict, requested_terms: list[str]) -> int:
    if not requested_terms:
        return 0

    meal_name = _normalize_text(str(meal.get("strMeal", "")))
    ingredients = [_normalize_text(item) for item in _extract_meal_ingredients(meal)]

    ingredient_matches = 0
    name_matches = 0

    for term in requested_terms:
        if any(term in ingredient for ingredient in ingredients):
            ingredient_matches += 1
        if term in meal_name:
            name_matches += 1

    return ingredient_matches * 10 + name_matches * 3


def _score_calorie_alignment(calories: int, target_calories: int, plan_goal: Optional[str]) -> int:
    if calories <= 0 or target_calories <= 0:
        return 0

    diff = abs(calories - target_calories)
    score = max(0, 50 - (diff // 12))

    goal = _normalize_text(plan_goal or "")
    if goal == "lose" and calories <= target_calories:
        score += 10
    elif goal == "lose" and calories > int(target_calories * 1.12):
        score -= 10
    elif goal == "gain" and calories >= target_calories:
        score += 10
    elif goal == "gain" and calories < int(target_calories * 0.88):
        score -= 10

    return score


def _split_steps(instructions: str) -> list[str]:
    if not instructions:
        return []
    chunks = [item.strip() for item in re.split(r"[\r\n]+", instructions) if item.strip()]
    if len(chunks) >= 2:
        return chunks[:12]
    sentences = [item.strip() for item in re.split(r"(?<=[.!?])\s+", instructions) if item.strip()]
    return sentences[:12] if sentences else [instructions.strip()]


def _build_negotiator_recipe_from_meal(meal: dict, target_calories: int) -> Optional[dict]:
    ingredients = _extract_meal_ingredients(meal)
    if not ingredients:
        return None

    steps = _split_steps(str(meal.get("strInstructions", "")))
    if not steps:
        steps = ["Segue o modo de preparação tradicional do prato."]

    calories = food_data.calculate_recipe_calories(ingredients)
    if calories <= 0:
        calories = max(250, target_calories)

    return {
        "title": str(meal.get("strMeal", "Receita sugerida")).strip(),
        "calories": calories,
        "time_minutes": 35,
        "ingredients": ingredients,
        "steps": steps,
    }


def _translate_recipe_to_pt(recipe: dict) -> dict:
    try:
        payload = {
            "title": recipe.get("title", ""),
            "ingredients": recipe.get("ingredients", []),
            "steps": recipe.get("steps", []),
        }
        prompt = (
            "Traduz para português de Portugal (PT-PT) mantendo quantidades e sentido culinário. "
            "Responde APENAS com JSON válido no mesmo formato, sem texto extra: "
            "{ 'title': '...', 'ingredients': ['...'], 'steps': ['...'] }.\n\n"
            f"DADOS:\n{json.dumps(payload, ensure_ascii=False)}"
        )
        response = get_chat_completion(
            messages=[
                {"role": "system", "content": "És um tradutor culinário PT-PT. Responde apenas JSON válido."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.2,
            response_format={"type": "json_object"},
            max_tokens=900
        )
        translated = json.loads(response.choices[0].message.content)

        title = str(translated.get("title") or payload["title"]).strip()
        ingredients = translated.get("ingredients") if isinstance(translated.get("ingredients"), list) else payload["ingredients"]
        steps = translated.get("steps") if isinstance(translated.get("steps"), list) else payload["steps"]

        return {
            **recipe,
            "title": title or recipe.get("title", ""),
            "ingredients": [str(item) for item in ingredients if str(item).strip()],
            "steps": [str(item) for item in steps if str(item).strip()],
        }
    except Exception:
        return recipe


def _try_recipe_api_first(craving: str, target_calories: int, allergens: List[str], plan_goal: Optional[str]) -> Optional[schemas.NegotiatorResponse]:
    requested_terms = _extract_query_terms(craving)
    if not requested_terms:
        return None
    api_terms = _expand_terms_for_api(requested_terms)

    candidate_ids: dict[str, None] = {}

    name_queries = [craving.strip()]
    translated_query = " ".join([_to_en_term(t) for t in requested_terms]).strip()
    if translated_query and translated_query.lower() != craving.strip().lower():
        name_queries.append(translated_query)

    for query in name_queries:
        by_name = _safe_fetch_json(f"{MEALDB_BASE_URL}/search.php?s={quote_plus(query)}")
        for meal in by_name.get("meals") or []:
            meal_id = str(meal.get("idMeal", "")).strip()
            if meal_id:
                candidate_ids[meal_id] = None

    for term in api_terms[:6]:
        by_ingredient = _safe_fetch_json(f"{MEALDB_BASE_URL}/filter.php?i={quote_plus(term)}")
        for meal in by_ingredient.get("meals") or []:
            meal_id = str(meal.get("idMeal", "")).strip()
            if meal_id:
                candidate_ids[meal_id] = None

    if not candidate_ids:
        return None

    scored_meals: list[tuple[int, dict]] = []

    for meal_id in list(candidate_ids.keys())[:14]:
        meal = _get_meal_details(meal_id)
        if not meal:
            continue
        ingredients = _extract_meal_ingredients(meal)
        if _contains_allergen(ingredients, allergens):
            continue
        semantic_score = _score_meal_for_query(meal, requested_terms)
        if semantic_score > 0:
            scored_meals.append((semantic_score, meal))

    if not scored_meals:
        return None

    scored_meals.sort(key=lambda x: x[0], reverse=True)

    best_raw_recipe = None
    best_total_score = -10_000
    for semantic_score, meal in scored_meals[:6]:
        raw_recipe = _build_negotiator_recipe_from_meal(meal, target_calories)
        if not raw_recipe:
            continue
        calories = int(raw_recipe.get("calories", 0) or 0)
        calorie_score = _score_calorie_alignment(calories, target_calories, plan_goal)
        total_score = semantic_score * 8 + calorie_score
        if total_score > best_total_score:
            best_total_score = total_score
            best_raw_recipe = raw_recipe

    if not best_raw_recipe:
        return None

    best_raw_recipe = _translate_recipe_to_pt(best_raw_recipe)

    return schemas.NegotiatorResponse(
        original_craving=craving,
        message="Encontrei uma receita numa base externa com boa correspondência aos alimentos pedidos.",
        recipe=schemas.NegotiatorRecipe(**best_raw_recipe),
        restaurant_search_term=craving
    )

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

def negotiate_craving(
    craving: str,
    target_calories: int = 600,
    mood: Optional[str] = None,
    favorite_recipes: List[schemas.Recipe] = [],
    allergens: List[str] = [],
    plan_goal: Optional[str] = None,
    daily_target_calories: Optional[int] = None
) -> schemas.NegotiatorResponse:
    api_recipe_response = _try_recipe_api_first(craving, target_calories, allergens, plan_goal)
    if api_recipe_response:
        return api_recipe_response

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

    goal_text = (plan_goal or "maintain").lower()
    if goal_text == "lose":
        goal_instruction = "Objetivo do utilizador: PERDER PESO. Prioriza receita mais leve e fica preferencialmente na metade inferior da faixa calórica."
    elif goal_text == "gain":
        goal_instruction = "Objetivo do utilizador: GANHAR MASSA/PESO. Prioriza receita mais energética e fica preferencialmente na metade superior da faixa calórica."
    else:
        goal_instruction = "Objetivo do utilizador: MANUTENÇÃO. Prioriza equilíbrio nutricional e aproximação ao alvo calórico."

    lower_bound = max(200, int(target_calories * 0.85))
    upper_bound = int(target_calories * 1.15)
    daily_hint = f"Meta diária estimada: {daily_target_calories} kcal.\n" if daily_target_calories else ""

    prompt = (
        "OBJETIVO: Criar uma receita saudável que cumpra OBRIGATORIAMENTE o desejo do utilizador.\n"
        f"DESEJO MANDATÓRIO DO UTILIZADOR: '{craving}'\n"
        f"ESTADO EMOCIONAL: {mood or 'Normal'}\n"
        f"META CALÓRICA DESTA REFEIÇÃO: {target_calories} kcal (faixa aceitável: {lower_bound}-{upper_bound} kcal).\n"
        f"{daily_hint}"
        f"{goal_instruction}\n"
        f"{allergen_context}"
        "\nFILTRO DE SEGURANÇA E VALIDAÇÃO:\n"
        "0. ANTES DE TUDO: Se o pedido do utilizador NÃO for um alimento (ex: objetos, químicos, pedras, eletrónicos, partes do corpo, ou qualquer coisa não comestível), ou se for um pedido perigoso, ofensivo ou estúpido, deves OBRIGATORIAMENTE definir 'recipe' como null e explicar na 'message' de forma educada mas firme que apenas geras receitas de comida real e saudável.\n"
        "\nINSTRUÇÕES DE CUMPRIMENTO ESTRITO (apenas para comida):\n"
        "1. Se passar o filtro acima, é PROIBIDO alterar o prato base. Se o utilizador pediu Sushi, a receita TEM de ser de Sushi. Se pediu Pizza, TEM de ser Pizza.\n"
        "2. A criatividade deve ser aplicada APENAS para tornar o prato pedido mais saudável, MAS NUNCA para mudar o tipo de comida.\n"
        "3. Ignora sugestões de 'Estilo' ou 'Inspiração' se estas entrarem em conflito com o prato mandatório.\n"
        "4. Responde sempre em PORTUGUÊS DE PORTUGAL (PT-PT).\n"
        "5. PROIBIDO usar quinoa/qinoa.\n"
        "6. A receita final deve ficar o mais perto possível da meta calórica indicada.\n"
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
            restaurant_search_term=data.get('restaurant_search_term', craving)
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
