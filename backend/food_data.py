import requests
import re
import os
import json
from functools import lru_cache
from typing import List, Dict
from llm_client import get_client_config, get_chat_completion

OPEN_FOOD_FACTS_URL = "https://world.openfoodfacts.org/cgi/search.pl"
OFF_TIMEOUT_SECONDS = float(os.getenv("OFF_TIMEOUT_SECONDS", "1.5"))
OFF_DEFAULT_PAGE_SIZE = int(os.getenv("OFF_DEFAULT_PAGE_SIZE", "3"))
OFF_LOG_ERRORS = os.getenv("OFF_LOG_ERRORS", "0").strip() == "1"

# Fallback values for common staples if API fails (kcal/100g)
COMMON_STAPLES = {
    "azeite": 884, "oliva": 884, "mel": 304, "cebola": 40, "alho": 149,
    "arroz": 130, "massa": 131, "espaguete": 158, "frango": 165,
    "peru": 189, "salsicha": 250, "tomate": 18, "batata": 77,
    "ovo": 155, "ovos": 155, "queijo": 402, "leite": 42,
    "pao": 265, "pão": 265, "manteiga": 717,
    "salmão": 208, "atum": 130, "carne": 250, "vaca": 250, "porco": 242,
    "alface": 15, "cenoura": 41, "brócolos": 34, "espinafres": 23,
    "maçã": 52, "banana": 89, "laranja": 47, "iogurte": 59, "pimento": 20
}

def _safe_float(value, default: float = 0.0) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return default

def _simplify_search_term(term: str) -> str:
    # Lowercase first
    term = term.lower()
    # Remove "de", "da", "do", "ou", "sem", "com"
    term = re.sub(r"\b(de|da|do|dos|das|ou|e|sem|com|fresco|natural|integral|magro|magra)\b", " ", term, flags=re.IGNORECASE)
    # Remove punctuation
    term = re.sub(r"[^\w\s]", "", term)
    # Get first 1-2 significant words
    words = term.split()
    if not words:
        return ""
    # Use first two words if available (e.g. "salsicha peru"), else just one
    return " ".join(words[:2])

@lru_cache(maxsize=512)
def _search_foods_cached(query: str, page_size: int) -> tuple[dict, ...]:
    query = query.strip()
    if not query:
        return tuple()

    try:
        response = requests.get(
            OPEN_FOOD_FACTS_URL,
            params={
                "search_terms": query,
                "search_simple": 1,
                "action": "process",
                "json": 1,
                "page_size": page_size,
                "lc": "pt", 
                "fields": "product_name,nutriments,brands"
            },
            timeout=OFF_TIMEOUT_SECONDS
        )
        
        if not response.ok:
            return tuple()
            
        data = response.json()
        products = data.get("products", [])
        
        results = []
        for p in products:
            nutriments = p.get("nutriments", {})
            name = p.get("product_name") or "Alimento desconhecido"
            
            kcal = _safe_float(nutriments.get("energy-kcal_100g", 0))
            if kcal == 0:
                kcal = _safe_float(nutriments.get("energy-kcal", 0))

            results.append({
                "name": name,
                "calories_per_100g": kcal,
                "protein_per_100g": _safe_float(nutriments.get("proteins_100g", 0)),
                "carbs_per_100g": _safe_float(nutriments.get("carbohydrates_100g", 0)),
                "fat_per_100g": _safe_float(nutriments.get("fat_100g", 0)),
                "source": "openfoodfacts"
            })
            
        return tuple(results)

    except requests.exceptions.Timeout:
        print(f"OFF Search Timeout for: {query}")
        raise requests.exceptions.Timeout(f"Timeout searching OFF for {query}")
    except Exception as e:
        if OFF_LOG_ERRORS:
            print(f"OFF Search Error: {e}")
        return tuple()

def search_foods(query: str, page_size: int = 10) -> List[Dict]:
    normalized_size = max(1, min(page_size or OFF_DEFAULT_PAGE_SIZE, 10))
    return [dict(item) for item in _search_foods_cached(query.strip(), normalized_size)]

def estimate_recipe_calories_with_ai(ingredients: List[str]) -> int:
    if not ingredients:
        return 0

    try:
        joined = ", ".join(ingredients[:30])
        prompt = (
            "Estima as calorias totais aproximadas desta receita com base nos ingredientes e quantidades indicadas. "
            "Responde APENAS JSON válido com formato: "
            "{ \"estimated_total_calories\": 0 }. "
            f"Ingredientes: {joined}"
        )
        response = get_chat_completion(
            messages=[
                {"role": "system", "content": "És um nutricionista. Retorna apenas JSON."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.2,
            response_format={"type": "json_object"},
            max_tokens=120
        )
        content = response.choices[0].message.content
        data = json.loads(content)
        calories = int(float(data.get("estimated_total_calories", 0)))
        return max(0, calories)
    except Exception as e:
        if OFF_LOG_ERRORS:
            print(f"AI Calories Fallback Error: {e}")
        return 0

def calculate_recipe_calories(ingredients: List[str]) -> int:
    total_calories = 0.0
    off_available = True

    for ing in ingredients:
        try:
            # 1. Parse quantity
            qty_match = re.search(r"(\d+(?:[.,]\d+)?)\s*(g|kg|ml|l|colher|unidade|chávena|dente|fatia|fatias|ovo|ovos)", ing.lower())
            
            multiplier = 1.0 # Default relative to 100g
            raw_term = ing

            if qty_match:
                val = float(qty_match.group(1).replace(",", "."))
                unit = qty_match.group(2)
                raw_term = ing.replace(qty_match.group(0), "").strip()

                if unit in ["kg", "l"]:
                    multiplier = val * 10
                elif unit in ["g", "ml"]:
                    multiplier = val / 100.0
                elif "colher" in unit:
                    multiplier = (val * 15) / 100.0
                elif "chávena" in unit or "xícara" in unit:
                    multiplier = (val * 240) / 100.0
                elif "dente" in unit:
                    multiplier = (val * 5) / 100.0
                else:
                    multiplier = (val * 80) / 100.0
            
            # 2. Simplification strategy
            simple_term = _simplify_search_term(raw_term)
            
            # Check hardcoded fallbacks first for super common low-error items
            found_kcal = 0
            found = False
            
            for key, val in COMMON_STAPLES.items():
                if key in simple_term.lower():
                    found_kcal = val
                    found = True
                    break
            
            if not found and off_available:
                # Search OFF with simplified term
                try:
                    results = search_foods(simple_term, page_size=3)
                    # Filter results that actually have calories
                    valid_results = [r for r in results if r["calories_per_100g"] > 0]
                    
                    if valid_results:
                        found_kcal = valid_results[0]["calories_per_100g"]
                except requests.exceptions.Timeout:
                    off_available = False # API is slow, don't try again for this recipe
                except Exception:
                    pass # Other errors, just skip this ingredient

            total_calories += found_kcal * multiplier
                
        except Exception:
            continue

    total_int = int(total_calories)
    if total_int > 0:
        return total_int

    # Fallback final: if OFF/common staples failed and total is 0, ask LLM for an estimate.
    return estimate_recipe_calories_with_ai(ingredients)
