import requests
import re
from typing import List, Dict, Optional

OPEN_FOOD_FACTS_URL = "https://world.openfoodfacts.org/cgi/search.pl"

# Fallback values for common staples if API fails (kcal/100g)
COMMON_STAPLES = {
    "azeite": 884,
    "oliva": 884,
    "mel": 304,
    "cebola": 40,
    "alho": 149,
    "arroz": 130,
    "massa": 131,
    "espaguete": 158,
    "frango": 165,
    "peru": 189,
    "salsicha": 250, # Average
    "tomate": 18,
    "batata": 77,
    "ovo": 155,
    "ovos": 155,
    "queijo": 402,
    "leite": 42,
    "pao": 265,
    "pão": 265,
    "manteiga": 717
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

def search_foods(query: str, page_size: int = 10) -> List[Dict]:
    query = query.strip()
    if not query:
        return []

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
            timeout=5
        )
        
        if not response.ok:
            return []
            
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
            
        return results

    except Exception as e:
        print(f"OFF Search Error: {e}")
        return []

def calculate_recipe_calories(ingredients: List[str]) -> int:
    total_calories = 0.0

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
            
            if not found:
                # Search OFF with simplified term
                results = search_foods(simple_term, page_size=3)
                # Filter results that actually have calories
                valid_results = [r for r in results if r["calories_per_100g"] > 0]
                
                if valid_results:
                    found_kcal = valid_results[0]["calories_per_100g"]
                elif results: 
                    # If we found items but they had 0 kcal (weird for OFF), maybe try one more simplification?
                    # Or just accept 0 if it's like "salt" or "water"
                    pass

            total_calories += found_kcal * multiplier
                
        except Exception:
            continue
            
    return int(total_calories)
