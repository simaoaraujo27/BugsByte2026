from sqlalchemy import Column, Integer, String, Float, ForeignKey, Table, UniqueConstraint, Text, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from database import Base

# Association table for many-to-many relationship between User and Allergen
user_allergens = Table(
    "user_allergens",
    Base.metadata,
    Column("user_id", Integer, ForeignKey("users.id"), primary_key=True),
    Column("allergen_id", Integer, ForeignKey("allergens.id"), primary_key=True),
)

# Association table for favorite recipes
user_favorite_recipes = Table(
    'user_favorite_recipes', Base.metadata,
    Column('user_id', Integer, ForeignKey('users.id'), primary_key=True),
    Column('recipe_id', Integer, ForeignKey('recipes.id'), primary_key=True)
)

# Association table for favorite restaurants
user_favorite_restaurants = Table(
    'user_favorite_restaurants', Base.metadata,
    Column('user_id', Integer, ForeignKey('users.id'), primary_key=True),
    Column('restaurant_id', Integer, ForeignKey('restaurants.id'), primary_key=True)
)

class Item(Base):
    __tablename__ = "items"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    description = Column(String, index=True)

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    full_name = Column(String, nullable=True)
    profile_image = Column(Text, nullable=True) # Store as base64 for simplicity in this project
    hashed_password = Column(String)
    peso = Column(Float)
    altura = Column(Float)
    sexo = Column(String)
    idade = Column(Integer)
    # Add reset_token for forgot password functionality
    reset_token = Column(String, nullable=True)
    goal = Column(String, nullable=True)
    activity_level = Column(String, nullable=True)

    allergens = relationship("Allergen", secondary=user_allergens, back_populates="users")
    diary_days = relationship("DiaryDay", back_populates="user", cascade="all, delete-orphan")
    favorite_recipes = relationship("Recipe", secondary=user_favorite_recipes)
    favorite_restaurants = relationship("Restaurant", secondary=user_favorite_restaurants)
    weight_history = relationship("WeightEntry", back_populates="user", cascade="all, delete-orphan")
    food_history = relationship("FoodHistory", back_populates="user", cascade="all, delete-orphan")

class WeightEntry(Base):
    __tablename__ = "weight_entries"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    weight = Column(Float, nullable=False)
    date = Column(String, nullable=False) # YYYY-MM-DD

    user = relationship("User", back_populates="weight_history")

class FoodHistory(Base):
    __tablename__ = "food_history"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    name = Column(String, nullable=False, index=True)
    calories_per_100g = Column(Float, nullable=False)
    protein_per_100g = Column(Float, nullable=False)
    carbs_per_100g = Column(Float, nullable=False)
    fat_per_100g = Column(Float, nullable=False)
    source = Column(String, default="search")
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    user = relationship("User", back_populates="food_history")

class Allergen(Base):
    __tablename__ = "allergens"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)

    users = relationship("User", secondary=user_allergens, back_populates="allergens")


class DiaryDay(Base):
    __tablename__ = "diary_days"
    __table_args__ = (UniqueConstraint("user_id", "date_key", name="uq_diary_user_date"),)

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    date_key = Column(String, nullable=False, index=True)  # YYYY-MM-DD
    goal = Column(Integer, nullable=False, default=1800)

    user = relationship("User", back_populates="diary_days")
    meals = relationship("DiaryMeal", back_populates="day", cascade="all, delete-orphan")


class DiaryMeal(Base):
    __tablename__ = "diary_meals"

    id = Column(Integer, primary_key=True, index=True)
    day_id = Column(Integer, ForeignKey("diary_days.id"), nullable=False, index=True)
    section = Column(String, nullable=False, index=True)  # breakfast/lunch/snack/dinner/extras
    name = Column(String, nullable=False)
    grams = Column(Float, nullable=True)
    calories = Column(Integer, nullable=False, default=0)
    protein = Column(Float, nullable=False, default=0)
    carbs = Column(Float, nullable=False, default=0)
    fat = Column(Float, nullable=False, default=0)

    day = relationship("DiaryDay", back_populates="meals")

class Recipe(Base):
    __tablename__ = 'recipes'
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    ingredients = Column(Text)
    instructions = Column(Text)

class Restaurant(Base):
    __tablename__ = 'restaurants'
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    address = Column(String)
    phone = Column(String)
