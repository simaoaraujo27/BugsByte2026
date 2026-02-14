import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import hashlib
import uuid
from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from dotenv import load_dotenv

# Force load .env from the current directory
env_path = os.path.join(os.path.dirname(__file__), '.env')
load_dotenv(env_path)

print("="*30)
print(f"Loading .env from: {env_path}")
print(f"API Key present: {'Yes' if os.getenv('OPENAI_API_KEY') else 'No'}")
print(f"Base URL: {os.getenv('OPENAI_BASE_URL', 'Default (OpenAI)')}")
print(f"Model: {os.getenv('OPENAI_MODEL', 'Default')}")
print("="*30)

# Use absolute imports (as per local requirement and working state)
import models, schemas, shops, negotiator, auth
from database import SessionLocal, engine, get_db
from fastapi.middleware.cors import CORSMiddleware
from datetime import timedelta

models.Base.metadata.create_all(bind=engine)

app = FastAPI()

# Configure CORS to allow frontend to access the backend
origins = [
    "http://localhost:5173",  # Default Vue.js development server port
    "http://127.0.0.1:5173",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/users/", response_model=schemas.User)
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    db_user = db.query(models.User).filter(models.User.username == user.username).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Username already registered")
    
    hashed_password = auth.get_password_hash(user.password)
    
    # Create user instance without allergens first
    new_user = models.User(
        username=user.username,
        hashed_password=hashed_password,
        peso=user.peso,
        altura=user.altura,
        sexo=user.sexo,
        idade=user.idade,
        goal=user.goal,
        activity_level=user.activity_level
    )
    db.add(new_user)
    
    # Handle allergens
    for allergen_name in user.allergens:
        db_allergen = db.query(models.Allergen).filter(models.Allergen.name == allergen_name).first()
        if not db_allergen:
            db_allergen = models.Allergen(name=allergen_name)
            db.add(db_allergen)
            db.flush() # Use flush instead of commit to keep it in the transaction
        new_user.allergens.append(db_allergen)

    db.commit()
    db.refresh(new_user)
    return new_user

@app.post("/login/", response_model=schemas.Token)
def login(request: schemas.LoginRequest, db: Session = Depends(get_db)):
    db_user = db.query(models.User).filter(models.User.username == request.username).first()
    if not db_user or not auth.verify_password(request.password, db_user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid username or password")
    
    access_token_expires = timedelta(minutes=auth.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = auth.create_access_token(
        data={"sub": db_user.username}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

@app.get("/users/me", response_model=schemas.User)
def read_user_me(current_user: models.User = Depends(auth.get_current_user)):
    return current_user

@app.post("/forgot-password/")
def forgot_password(request: schemas.ForgotPasswordRequest, db: Session = Depends(get_db)):
    db_user = db.query(models.User).filter(models.User.username == request.username).first()
    if not db_user:
        # Security: Don't reveal if user exists or not, just return success
        return {"message": "If the email exists, a reset link has been sent."}
    
    # Generate a random token
    token = str(uuid.uuid4())
    db_user.reset_token = token
    db.commit()
    
    # SIMULATE EMAIL SENDING (Free & Reliable for Hackathon)
    print("="*50)
    print(f"EMAIL SIMULATION FOR: {request.username}")
    print(f"Subject: Reset Your Password")
    print(f"Body: Click here to reset your password: http://localhost:5173/reset-password?token={token}")
    print("="*50)
    
    return {"message": "If the email exists, a reset link has been sent."}

@app.post("/negotiator/negotiate", response_model=schemas.NegotiatorResponse)
def negotiate_craving(request: schemas.NegotiatorRequest, current_user: models.User = Depends(auth.get_current_user)):
    return negotiator.negotiate_craving(request.craving, request.target_calories)

@app.get("/users/", response_model=list[schemas.User])
def read_users(skip: int = 0, limit: int = 100, db: Session = Depends(get_db), current_user: models.User = Depends(auth.get_current_user)):
    users = db.query(models.User).offset(skip).limit(limit).all()
    return users

@app.post("/shops/find", response_model=list[schemas.Shop])
def find_shops(request: schemas.ShopSearchRequest, current_user: models.User = Depends(auth.get_current_user)):
    if request.mode == "restaurant":
        # Search for restaurants matching the ingredients (which acts as term here)
        search_val = "restaurant"
        key = "amenity"
        # Use the first item as a search term (e.g. "Pizza", "Italiano")
        search_term = request.ingredients[0] if request.ingredients else None
        
        found_shops = shops.find_nearby_shops(
            search_val, 
            request.lat, 
            request.lon, 
            request.radius,
            key=key,
            search_term=search_term
        )
    else:
        # 1. Determine the shop type using OpenAI
        shop_tag = shops.get_shop_type(request.ingredients)
        
        if shop_tag == "invalid":
            raise HTTPException(status_code=400, detail="A pesquisa contém termos inválidos ou não relacionados com alimentação.")

        # 2. Find nearby shops using Overpass API
        # We don't filter by name here because we want any shop that sells the ingredients
        found_shops = shops.find_nearby_shops(
            shop_tag, 
            request.lat, 
            request.lon, 
            request.radius,
            key="shop"
        )
    
    return found_shops

@app.post("/items/", response_model=schemas.Item)
def create_item(item: schemas.ItemCreate, db: Session = Depends(get_db), current_user: models.User = Depends(auth.get_current_user)):
    db_item = models.Item(**item.model_dump())
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item

@app.get("/items/", response_model=list[schemas.Item])
def read_items(skip: int = 0, limit: int = 100, db: Session = Depends(get_db), current_user: models.User = Depends(auth.get_current_user)):
    items = db.query(models.Item).offset(skip).limit(limit).all()
    return items

@app.get("/items/{item_id}", response_model=schemas.Item)
def read_item(item_id: int, db: Session = Depends(get_db), current_user: models.User = Depends(auth.get_current_user)):
    item = db.query(models.Item).filter(models.Item.id == item_id).first()
    if item is None:
        raise HTTPException(status_code=404, detail="Item not found")
    return item

@app.get("/")
async def root():
    return {"message": "Welcome to the FastAPI Backend!"}