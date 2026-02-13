from sqlalchemy import Column, Integer, String, Float, ForeignKey, Table
from sqlalchemy.orm import relationship
from .database import Base

# Association table for many-to-many relationship between User and Allergen
user_allergens = Table(
    "user_allergens",
    Base.metadata,
    Column("user_id", Integer, ForeignKey("users.id"), primary_key=True),
    Column("allergen_id", Integer, ForeignKey("allergens.id"), primary_key=True),
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
    hashed_password = Column(String)
    peso = Column(Float)
    altura = Column(Float)
    sexo = Column(String)
    idade = Column(Integer)

    allergens = relationship("Allergen", secondary=user_allergens, back_populates="users")

class Allergen(Base):
    __tablename__ = "allergens"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)

    users = relationship("User", secondary=user_allergens, back_populates="allergens")