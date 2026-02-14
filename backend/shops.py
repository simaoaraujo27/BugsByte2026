import os
import math
import requests
import re
from typing import List, Dict, Optional
from openai import OpenAI

def haversine_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """
    Calculate the great circle distance in meters between two points 
    on the earth (specified in decimal degrees).
    """
    # Earth radius in meters
    R = 6371000

    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    delta_phi = math.radians(lat2 - lat1)
    delta_lambda = math.radians(lon2 - lon1)

    a = math.sin(delta_phi / 2)**2 + math.cos(phi1) * math.cos(phi2) * math.sin(delta_lambda / 2)**2
    
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

    return R * c

def get_shop_type(ingredients: List[str], api_key: Optional[str] = None) -> str:
    """
    Uses OpenAI API (or compatible like Groq) to determine the best OpenStreetMap shop tag.
    """
    final_api_key = api_key or os.getenv("OPENAI_API_KEY")
    if final_api_key:
        final_api_key = final_api_key.strip()

    base_url = os.getenv("OPENAI_BASE_URL")
    model = os.getenv("OPENAI_MODEL", "gpt-3.5-turbo")

    if not final_api_key:
        return "supermarket"

    # Auto-detect Groq key
    if final_api_key.startswith("gsk_"):
        if not base_url or "openai.com" in base_url:
            base_url = "https://api.groq.com/openai/v1"
            model = "llama-3.3-70b-versatile"

    client = OpenAI(
        api_key=final_api_key,
        base_url=base_url
    )

    ingredients_str = ", ".join(ingredients)
    prompt = (
        f"Analyze this list of ingredients/terms: {ingredients_str}. "
        "1. Extract the likely FOOD/SHOP intent even if the text has typos, mixed language, or noisy words. "
        "2. Ignore filler or nonsensical fragments around valid food terms (example: 'milk on darty' still implies buying milk). "
        "3. If there is at least one valid food-shopping intent, determine the single best OpenStreetMap 'shop' tag key. "
        "4. Return exactly 'invalid' only when all terms are nonsensical, inappropriate, offensive, or unrelated to food shopping. "
        "Examples: 'supermarket', 'convenience', 'greengrocer', 'butcher', 'health_food', 'delicatessen'. "
        "Examples of noisy input handling: 'milk on darty' -> supermarket, 'chiken brest' -> butcher/supermarket, 'apple banana' -> greengrocer/supermarket. "
        "Return ONLY the clean string of the tag (or 'invalid') with no punctuation or extra text."
    )

    try:
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": "You are a helpful assistant that maps ingredients to OpenStreetMap tags."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3,
            max_tokens=10,
            timeout=10
        )
        # Clean the response: lowercase, strip punctuation and extra spaces
        tag = response.choices[0].message.content.strip().lower()
        tag = re.sub(r'[^a-z_]', '', tag)
        return tag
    except Exception:
        return "supermarket"

def find_nearby_shops(tag_value: str, lat: float, lon: float, radius: int = 3000, key: str = "shop", search_term: Optional[str] = None) -> List[Dict]:
    """
    Queries the Overpass API for nodes/ways/relations with key=tag_value around the given coordinates.
    Filtering by search_term is done in Python to avoid expensive/slow Overpass regex queries (preventing 504s).
    """
    # Normalize tag and key for Overpass
    tag_value = tag_value.lower().strip()
    key = key.lower().strip()

    # Use official endpoint and a fallback
    overpass_urls = [
        "https://overpass-api.de/api/interpreter",
        "https://overpass.kumi.systems/api/interpreter"
    ]
    
    # We fetch ALL nearby establishments of the category. 
    # Removing the name filter from the query makes it MUCH faster and reliable.
    # Increased timeout to 90s to avoid 504 errors on busy instances
    query = f'[out:json][timeout:90];nwr["{key}"="{tag_value}"](around:{radius},{lat},{lon});out center;'

    for url in overpass_urls:
        try:
            response = requests.get(url, params={'data': query}, timeout=95)
            response.raise_for_status()
            data = response.json()
            
            shops = []
            # ... (rest of the processing)
            # Pre-compile regex for faster filtering if term is present
            pattern = None
            if search_term and search_term.strip():
                # Case-insensitive search anywhere in the name
                pattern = re.compile(re.escape(search_term.strip()), re.IGNORECASE)

            for element in data.get('elements', []):
                shop_lat = element.get('lat') or element.get('center', {}).get('lat')
                shop_lon = element.get('lon') or element.get('center', {}).get('lon')
                
                if shop_lat is None or shop_lon is None:
                    continue

                name = element.get('tags', {}).get('name', 'Desconhecido')
                
                # If we have a search term (like "Pizza" for restaurants), we filter here
                if pattern:
                    if not pattern.search(name):
                        continue

                distance = haversine_distance(lat, lon, shop_lat, shop_lon)
                
                shops.append({
                    'name': name,
                    'lat': shop_lat,
                    'lon': shop_lon,
                    'distance': round(distance, 2)
                })
                
            shops.sort(key=lambda x: x['distance'])
            # Return top 50 results to keep frontend snappy
            return shops[:50]

        except Exception as e:
            print(f"Error in find_nearby_shops with {url}: {e}")
            continue # Try next server
            
    return []
