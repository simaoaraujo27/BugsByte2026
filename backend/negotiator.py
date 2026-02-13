import os
import json
from typing import List, Dict, Optional
from openai import OpenAI
import schemas

def negotiate_craving(craving: str, target_calories: int = 600, api_key: Optional[str] = None) -> schemas.NegotiatorResponse:
    final_api_key = api_key or os.getenv("OPENAI_API_KEY")
    if not final_api_key:
        # For dev/testing without key, return mock
        # raise ValueError("OpenAI API key is required.")
        print("Warning: No API key, using mock negotiator response.")
        return schemas.NegotiatorResponse(
            original_craving=craving,
            message="Mock response: That sounds delicious, but let's try a lighter version!",
            recipe=schemas.Recipe(
                title=f"Lighter {craving}",
                calories=target_calories - 100,
                time_minutes=25,
                ingredients=["Zucchini", "Chicken Breast", "Olive Oil", "Spices"],
                steps=["Slice zucchini", "Grill chicken", "Mix and serve"]
            ),
            restaurant_search_term=craving
        )

    client = OpenAI(api_key=final_api_key)

    prompt = (
        f"The user is craving '{craving}'. They have a target of around {target_calories} kcal. "
        "Act as a nutritional negotiator. "
        "1. Create a healthier, lower-calorie homemade version of this dish (DIY). "
        "2. Provide a search term to find restaurants serving this dish. "
        "Return a JSON object with this structure: "
        "{ "
        "  'message': 'A witty short comment about their craving', "
        "  'recipe': { "
        "    'title': 'Name of the healthy version', "
        "    'calories': 550, "
        "    'time_minutes': 30, "
        "    'ingredients': ['list', 'of', 'simple', 'ingredients'], "
        "    'steps': ['step 1', 'step 2'] "
        "  }, "
        "  'restaurant_search_term': 'search term for map' "
        "}"
    )

    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a helpful nutritionist assistant. Return only valid JSON."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            response_format={"type": "json_object"}
        )
        content = response.choices[0].message.content
        data = json.loads(content)
        
        return schemas.NegotiatorResponse(
            original_craving=craving,
            message=data.get('message', 'Here is a healthy alternative!'),
            recipe=schemas.Recipe(**data.get('recipe', {})),
            restaurant_search_term=data.get('restaurant_search_term', craving)
        )
    except Exception as e:
        print(f"Error in negotiator: {e}")
        # Fallback response
        return schemas.NegotiatorResponse(
            original_craving=craving,
            message="Couldn't generate a specific recipe, but here is a generic healthy option.",
            recipe=schemas.Recipe(
                title=f"Healthy {craving}", 
                calories=target_calories, 
                time_minutes=30, 
                ingredients=["Fresh vegetables", "Lean protein", "Whole grains"], 
                steps=["Grill the protein", "Steam vegetables", "Serve together"]
            ),
            restaurant_search_term=craving
        )
