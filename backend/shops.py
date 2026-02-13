import os
import math
import requests
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
    base_url = os.getenv("OPENAI_BASE_URL")
    model = os.getenv("OPENAI_MODEL", "gpt-3.5-turbo")

    if not final_api_key:
        raise ValueError("OpenAI API key is required but was not provided or found in environment variables.")

    # Auto-detect Groq key
    if final_api_key.startswith("gsk_") and not base_url:
        print("Auto-detected Groq key. Switching to Groq API.")
        base_url = "https://api.groq.com/openai/v1"
        model = "llama-3.3-70b-versatile"

    client = OpenAI(
        api_key=final_api_key,
        base_url=base_url
    )

    ingredients_str = ", ".join(ingredients)
    prompt = (
        f"Analyze this list of ingredients: {ingredients_str}. "
        "Determine the single best OpenStreetMap 'shop' tag key to find them. "
        "Examples: 'supermarket', 'convenience', 'greengrocer', 'butcher', 'health_food', 'delicatessen'. "
        "Return ONLY the clean string of the tag with no punctuation or extra text."
    )

    try:
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": "You are a helpful assistant that maps ingredients to OpenStreetMap tags."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3,
            max_tokens=10
        )
        tag = response.choices[0].message.content.strip()
        return tag
    except Exception as e:
        print(f"Error communicating with OpenAI: {e}")
        # No more hardcoded fallback
        raise e

def find_nearby_shops(tag_value: str, lat: float, lon: float, radius: int = 3000, key: str = "shop") -> List[Dict]:
    """
    Queries the Overpass API for nodes/ways/relations with key=tag_value around the given coordinates.
    """
    # Switching to an alternative reliable mirror
    overpass_url = "https://overpass.kumi.systems/api/interpreter"
    
    # Flat query to avoid parsing issues
    query = f'[out:json][timeout:90];nwr["{key}"="{tag_value}"](around:{radius},{lat},{lon});out center;'

    try:
        response = requests.get(overpass_url, params={'data': query}, timeout=100)
        response.raise_for_status()
        data = response.json()
        
        shops = []
        for element in data.get('elements', []):
            shop_lat = element.get('lat')
            shop_lon = element.get('lon')
            
            if shop_lat is None or shop_lon is None:
                if 'center' in element:
                    shop_lat = element['center']['lat']
                    shop_lon = element['center']['lon']
                else:
                    continue

            distance = haversine_distance(lat, lon, shop_lat, shop_lon)
            
            shop_info = {
                'name': element.get('tags', {}).get('name', 'Desconhecido'),
                'lat': shop_lat,
                'lon': shop_lon,
                'distance': round(distance, 2)
            }
            shops.append(shop_info)
            
        shops.sort(key=lambda x: x['distance'])
        return shops

    except requests.exceptions.RequestException as e:
        print(f"Error querying Overpass API: {e}")
        return []
