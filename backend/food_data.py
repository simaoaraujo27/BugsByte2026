import os
from typing import List, Dict

import requests


USDA_SEARCH_URL = "https://api.nal.usda.gov/fdc/v1/foods/search"
OPEN_FOOD_FACTS_URL = "https://world.openfoodfacts.org/cgi/search.pl"
FATSECRET_TOKEN_URL = "https://oauth.fatsecret.com/connect/token"
FATSECRET_SEARCH_URL = "https://platform.fatsecret.com/rest/server.api"


def _safe_float(value, default: float = 0.0) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def _get_fatsecret_token(client_id: str, client_secret: str) -> str:
    response = requests.post(
        FATSECRET_TOKEN_URL,
        auth=(client_id, client_secret),
        data={"grant_type": "client_credentials", "scope": "basic"},
        timeout=10,
    )
    response.raise_for_status()
    return response.json().get("access_token")


def _search_fatsecret(query: str, client_id: str, client_secret: str, page_size: int) -> List[Dict]:
    token = _get_fatsecret_token(client_id, client_secret)
    
    response = requests.get(
        FATSECRET_SEARCH_URL,
        headers={"Authorization": f"Bearer {token}"},
        params={
            "method": "foods.search",
            "search_expression": query,
            "format": "json",
            "max_results": page_size,
        },
        timeout=10,
    )
    response.raise_for_status()
    payload = response.json()
    
    foods = []
    # FatSecret structure is foods -> food (list or single dict)
    results = payload.get("foods", {}).get("food", [])
    if isinstance(results, dict):
        results = [results]

    for item in results:
        # FatSecret search returns a 'food_description' string like:
        # "Per 100g - Calories: 155kcal | Fat: 10.61g | Carbs: 1.12g | Protein: 12.58g"
        desc = item.get("food_description", "")
        
        # Simple extraction logic for 100g basis
        # Note: This is a simplified parser for the search result string
        nutrients = {"calories": 0.0, "fat": 0.0, "carbs": 0.0, "protein": 0.0}
        if "Per 100g" in desc or "Per 100ml" in desc:
            parts = desc.split("|")
            for p in parts:
                if "Calories:" in p:
                    nutrients["calories"] = _safe_float(p.replace("Calories:", "").replace("kcal", "").strip())
                elif "Fat:" in p:
                    nutrients["fat"] = _safe_float(p.replace("Fat:", "").replace("g", "").strip())
                elif "Carbs:" in p:
                    nutrients["carbs"] = _safe_float(p.replace("Carbs:", "").replace("g", "").strip())
                elif "Protein:" in p:
                    nutrients["protein"] = _safe_float(p.replace("Protein:", "").replace("g", "").strip())

        foods.append(
            {
                "name": f"{item.get('brand_name', '')} {item.get('food_name', '')}".strip(),
                "calories_per_100g": nutrients["calories"],
                "protein_per_100g": nutrients["protein"],
                "carbs_per_100g": nutrients["carbs"],
                "fat_per_100g": nutrients["fat"],
                "source": "fatsecret",
            }
        )

    return foods


def _search_usda(query: str, api_key: str, page_size: int) -> List[Dict]:
    response = requests.get(
        USDA_SEARCH_URL,
        params={
            "api_key": api_key,
            "query": query,
            "pageSize": page_size,
        },
        timeout=10,
    )
    response.raise_for_status()
    payload = response.json()

    foods = []
    for item in payload.get("foods", []):
        nutrients = {
            int(n.get("nutrientId")): _safe_float(n.get("value"))
            for n in item.get("foodNutrients", [])
            if n.get("nutrientId") is not None
        }

        foods.append(
            {
                "name": item.get("description", "Unknown food"),
                "calories_per_100g": nutrients.get(1008, 0.0),  # Energy (kcal)
                "protein_per_100g": nutrients.get(1003, 0.0),   # Protein
                "carbs_per_100g": nutrients.get(1005, 0.0),     # Carbohydrate
                "fat_per_100g": nutrients.get(1004, 0.0),       # Total lipid (fat)
                "source": "usda",
            }
        )

    return foods


def _search_open_food_facts(query: str, page_size: int) -> List[Dict]:
    response = requests.get(
        OPEN_FOOD_FACTS_URL,
        params={
            "search_terms": query,
            "search_simple": 1,
            "action": "process",
            "json": 1,
            "page_size": page_size,
        },
        timeout=10,
    )
    response.raise_for_status()
    payload = response.json()

    foods = []
    for item in payload.get("products", []):
        nutriments = item.get("nutriments", {})
        name = item.get("product_name") or item.get("generic_name") or item.get("brands")
        if not name:
            continue

        foods.append(
            {
                "name": name,
                "calories_per_100g": _safe_float(
                    nutriments.get("energy-kcal_100g", nutriments.get("energy-kcal"))
                ),
                "protein_per_100g": _safe_float(nutriments.get("proteins_100g")),
                "carbs_per_100g": _safe_float(nutriments.get("carbohydrates_100g")),
                "fat_per_100g": _safe_float(nutriments.get("fat_100g")),
                "source": "openfoodfacts",
            }
        )

    return foods


def search_foods(query: str, page_size: int = 10) -> List[Dict]:
    query = query.strip()
    if not query:
        return []

    page_size = max(1, min(page_size, 20))
    
    # Try FatSecret first
    # Checking for both standard and user-specific .env names
    fs_id = os.getenv("FATSECRET_CLIENT_ID") or os.getenv("Client ID")
    fs_secret = os.getenv("FATSECRET_CLIENT_SECRET") or os.getenv("Client Secret")
    
    if fs_id and fs_secret:
        try:
            foods = _search_fatsecret(query, fs_id, fs_secret, page_size)
            if foods:
                return foods
        except Exception:
            # Fallback to other sources on error
            pass

    usda_key = os.getenv("USDA_API_KEY")
    if usda_key:
        try:
            foods = _search_usda(query, usda_key, page_size)
            if foods:
                return foods
        except requests.RequestException:
            pass

    try:
        return _search_open_food_facts(query, page_size)
    except requests.RequestException:
        return []


def get_nutrition_for_recipe(ingredients: List[str]) -> Dict:
    """
    Estimates total nutrition for a list of ingredients using FatSecret.
    Parses quantities (g, kg, ml, etc.) for better accuracy.
    """
    fs_id = os.getenv("FATSECRET_CLIENT_ID") or os.getenv("Client ID")
    fs_secret = os.getenv("FATSECRET_CLIENT_SECRET") or os.getenv("Client Secret")
    
    total_nutrients = {"calories": 0, "protein": 0.0, "carbs": 0.0, "fat": 0.0}
    
    if not fs_id or not fs_secret or not ingredients:
        return total_nutrients

    try:
        token = _get_fatsecret_token(fs_id, fs_secret)
        
        for ing in ingredients:
            try:
                # 1. Extract quantity and unit
                # Pattern to find numbers and units (g, kg, ml, l)
                qty_match = re.search(r"(\d+(?:[.,]\d+)?)\s*(g|kg|ml|l|colher|unidade|chávena|dente|fatia)", ing.lower())
                multiplier = 1.0 # Default to 1 unit or 100g depending on result
                
                search_term = ing
                if qty_match:
                    val = float(qty_match.group(1).replace(",", "."))
                    unit = qty_match.group(2)
                    search_term = ing.replace(qty_match.group(0), "").strip()
                    
                    if unit == "kg" or unit == "l":
                        multiplier = val * 10 # Since FS usually returns per 100g
                    elif unit == "g" or unit == "ml":
                        multiplier = val / 100
                    else:
                        multiplier = val # For units like "2 eggs"

                # 2. Search for the ingredient
                response = requests.get(
                    FATSECRET_SEARCH_URL,
                    headers={"Authorization": f"Bearer {token}"},
                    params={
                        "method": "foods.search",
                        "search_expression": search_term,
                        "format": "json",
                        "max_results": 1,
                    },
                    timeout=5,
                )
                if not response.ok:
                    continue
                    
                payload = response.json()
                results = payload.get("foods", {}).get("food", [])
                if isinstance(results, dict):
                    results = [results]
                
                if results:
                    desc = results[0].get("food_description", "")
                    parts = desc.split("|")
                    for p in parts:
                        if "Calories:" in p:
                            cal = _safe_float(p.replace("Calories:", "").replace("kcal", "").strip())
                            total_nutrients["calories"] += cal * multiplier
                        elif "Fat:" in p:
                            fat = _safe_float(p.replace("Fat:", "").replace("g", "").strip())
                            total_nutrients["fat"] += fat * multiplier
                        elif "Carbs:" in p:
                            carbs = _safe_float(p.replace("Carbs:", "").replace("g", "").strip())
                            total_nutrients["carbs"] += carbs * multiplier
                        elif "Protein:" in p:
                            prot = _safe_float(p.replace("Protein:", "").replace("g", "").strip())
                            total_nutrients["protein"] += prot * multiplier
            except Exception:
                continue
                
    except Exception as e:
        print(f"Error in get_nutrition_for_recipe: {e}")
        
    return total_nutrients
