import json
from typing import List, Dict
from llm_client import get_client_config

def search_foods(query: str, page_size: int = 10) -> List[Dict]:
    """
    Searches for food items using the LLM (Groq) to generate nutritional data.
    Replaces external APIs like OpenFoodFacts/USDA.
    """
    query = query.strip()
    if not query:
        return []

    client, model = get_client_config()

    prompt = (
        f"Gera uma lista de {page_size} alimentos comuns que correspondam à pesquisa: '{query}'. "
        "Para cada alimento, fornece uma estimativa nutricional realista por 100g. "
        "Responde APENAS com um JSON array válido. "
        "Formato: "
        "[{"
        "  \"name\": \"Nome do Alimento\","
        "  \"calories_per_100g\": 0,"
        "  \"protein_per_100g\": 0.0,"
        "  \"carbs_per_100g\": 0.0,"
        "  \"fat_per_100g\": 0.0,"
        "  \"source\": \"ai_estimate\""
        "}]"
    )

    try:
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": "És uma base de dados nutricional precisa. Responde apenas JSON."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3,
            response_format={"type": "json_object"}
        )
        
        content = response.choices[0].message.content
        # Handle potential wrapper keys if the model adds them (e.g. {"foods": [...]})
        try:
            data = json.loads(content)
        except json.JSONDecodeError:
            return []
        
        if isinstance(data, list):
            return data
        elif isinstance(data, dict):
            # Look for common list keys including 'alimentos'
            for key in ["foods", "items", "results", "alimentos", "data"]:
                if key in data and isinstance(data[key], list):
                    return data[key]
            # If the dict values are a single list (e.g. {"something": [...]}), take it
            for value in data.values():
                if isinstance(value, list) and len(value) > 0 and isinstance(value[0], dict):
                    return value
            
            # If plain dict but not list, maybe single item? Wrap it if it looks like an item
            if "name" in data and "calories_per_100g" in data:
                return [data]
            
        return []

    except Exception:
        return []
