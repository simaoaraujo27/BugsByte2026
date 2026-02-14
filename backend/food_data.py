import os
from typing import List, Dict

import requests


USDA_SEARCH_URL = "https://api.nal.usda.gov/fdc/v1/foods/search"
OPEN_FOOD_FACTS_URL = "https://world.openfoodfacts.org/cgi/search.pl"


def _safe_float(value, default: float = 0.0) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


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
