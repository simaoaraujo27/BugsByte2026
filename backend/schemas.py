from pydantic import BaseModel

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

class UserBase(BaseModel):
    username: str
    peso: float
    altura: float
    sexo: str
    idade: int
    goal: str | None = None
    activity_level: str | None = None

class UserCreate(UserBase):
    password: str
    allergens: list[str] = []

class User(UserBase):
    id: int
    allergens: list[Allergen] = []

    class ConfigDict:
        from_attributes = True

class LoginRequest(BaseModel):
    username: str
    password: str

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
