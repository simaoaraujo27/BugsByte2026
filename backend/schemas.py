from pydantic import BaseModel, Field, field_validator
from typing import List, Optional

class ItemBase(BaseModel):
    name: str
    description: str | None = None

class ItemCreate(ItemBase):
    pass

class Item(ItemBase):
    id: int

    class ConfigDict:
        from_attributes = True

class AllergenBase(BaseModel):
    name: str

class Allergen(AllergenBase):
    id: int

    class ConfigDict:
        from_attributes = True

class RecipeBase(BaseModel):
    name: str
    ingredients: str
    instructions: str

class RecipeCreate(RecipeBase):
    pass

class Recipe(RecipeBase):
    id: int

    class ConfigDict:
        from_attributes = True

class RestaurantBase(BaseModel):
    name: str
    address: str
    phone: str

class RestaurantCreate(RestaurantBase):
    pass

class Restaurant(RestaurantBase):
    id: int

    class ConfigDict:
        from_attributes = True

class UserBase(BaseModel):
    username: str
    full_name: Optional[str] = None
    profile_image: Optional[str] = None
    peso: float
    altura: float
    sexo: str
    idade: int
    goal: str | None = None
    activity_level: str | None = None

class UserCreate(UserBase):
    password: str
    allergens: list[str] = []

class UserUpdate(BaseModel):
    username: Optional[str] = None
    full_name: Optional[str] = None
    profile_image: Optional[str] = None
    password: Optional[str] = None
    peso: Optional[float] = None
    altura: Optional[float] = None
    sexo: Optional[str] = None
    idade: Optional[int] = None
    goal: Optional[str] = None
    activity_level: Optional[str] = None

class User(UserBase):
    id: int
    allergens: list[Allergen] = []
    favorite_recipes: List[Recipe] = []
    favorite_restaurants: List[Restaurant] = []

    class ConfigDict:
        from_attributes = True

class DashboardResponse(BaseModel):
    consumed_calories: int
    calorie_goal: int
    protein: float
    carbs: float
    fat: float
    streak_days: int
    water_liters: float = 0.0
    weight_history: dict[str, list] = {}

class LoginRequest(BaseModel):
    username: str
    password: str

class ForgotPasswordRequest(BaseModel):
    username: str

class ResetPasswordConfirm(BaseModel):
    token: str
    new_password: str = Field(..., min_length=8, max_length=128)

class Shop(BaseModel):
    name: str
    lat: float
    lon: float
    distance: float

class ShopSearchRequest(BaseModel):
    ingredients: list[str]
    lat: float
    lon: float
    radius: int = 3000
    mode: str = "shop" # 'shop' or 'restaurant'


class FoodSearchItem(BaseModel):
    name: str
    calories_per_100g: float
    protein_per_100g: float
    carbs_per_100g: float
    fat_per_100g: float
    source: str

class FoodHistoryBase(BaseModel):
    name: str
    calories_per_100g: float
    protein_per_100g: float
    carbs_per_100g: float
    fat_per_100g: float
    source: str = "search"

class FoodHistoryCreate(FoodHistoryBase):
    pass

class FoodHistoryResponse(FoodHistoryBase):
    id: int
    user_id: int
    created_at: str

    class ConfigDict:
        from_attributes = True

    @field_validator("created_at", mode="before")
    def serialize_datetime(cls, v):
        if v:
            return v.isoformat()
        return v

class NegotiatorRecipe(BaseModel):
    title: str
    calories: int
    time_minutes: int
    ingredients: list[str]
    steps: list[str]

class NegotiatorRequest(BaseModel):
    craving: str
    target_calories: int = 600
    mood: str | None = None

class MoodAnalysisResponse(BaseModel):
    mood_type: str
    empathy_message: str
    explanation: str
    eating_strategy: str

class NegotiatorResponse(BaseModel):
    original_craving: str
    message: str
    recipe: NegotiatorRecipe | None = None
    restaurant_search_term: str

class NutritionAnalysisRequest(BaseModel):
    food_text: str

class NutritionAnalysisResponse(BaseModel):
    food_text: str
    is_food: bool = True
    error_message: Optional[str] = None
    name: str
    calories: int
    protein: float
    carbs: float
    fat: float
    estimated_grams: int

class DiaryGoalUpdate(BaseModel):
    goal: int = Field(..., ge=1000, le=6000)


class DiaryMealCreate(BaseModel):
    section: str
    name: str
    calories: int = Field(..., ge=0, le=10000)
    protein: float = Field(0, ge=0, le=1000)
    carbs: float = Field(0, ge=0, le=1000)
    fat: float = Field(0, ge=0, le=1000)

    @field_validator("section")
    @classmethod
    def validate_section(cls, value: str) -> str:
        allowed = {"breakfast", "lunch", "snack", "dinner", "extras"}
        if value not in allowed:
            raise ValueError("Invalid section")
        return value

    @field_validator("name")
    @classmethod
    def validate_name(cls, value: str) -> str:
        name = value.strip()
        if not name:
            raise ValueError("Meal name is required")
        return name


class DiaryMeal(BaseModel):
    id: int
    section: str
    name: str
    calories: int
    protein: float
    carbs: float
    fat: float

    class ConfigDict:
        from_attributes = True


class DiaryDay(BaseModel):
    id: int
    user_id: int
    date_key: str
    goal: int
    meals: list[DiaryMeal] = []

    class ConfigDict:
        from_attributes = True
class VisionResponse(BaseModel):
    detected_ingredients: list[str]
    message: str
    recipe: NegotiatorRecipe

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: str | None = None