import hashlib
from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from dotenv import load_dotenv
from . import models, schemas, shops, negotiator
from .database import SessionLocal, engine, get_db
from fastapi.middleware.cors import CORSMiddleware

load_dotenv()

models.Base.metadata.create_all(bind=engine)

app = FastAPI()

def get_password_hash(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()

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
    
    hashed_password = get_password_hash(user.password)
    
    # Create user instance without allergens first
    new_user = models.User(
        username=user.username,
        hashed_password=hashed_password,
        peso=user.peso,
        altura=user.altura,
        sexo=user.sexo,
        idade=user.idade
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

class LoginRequest(schemas.BaseModel):
    username: str
    password: str

@app.post("/login/")
def login(request: LoginRequest, db: Session = Depends(get_db)):
    db_user = db.query(models.User).filter(models.User.username == request.username).first()
    if not db_user or db_user.hashed_password != get_password_hash(request.password):
        raise HTTPException(status_code=401, detail="Invalid username or password")
    
    return {"message": "Login successful", "user_id": db_user.id}

@app.post("/negotiator/negotiate", response_model=schemas.NegotiatorResponse)
def negotiate_craving(request: schemas.NegotiatorRequest):
    return negotiator.negotiate_craving(request.craving, request.target_calories)

@app.get("/users/", response_model=list[schemas.User])
def read_users(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    users = db.query(models.User).offset(skip).limit(limit).all()
    return users

@app.post("/shops/find", response_model=list[schemas.Shop])
def find_shops(request: schemas.ShopSearchRequest):
    if request.mode == "restaurant":
        # Search for restaurants
        # We can search for amenity=restaurant, or cuisine=request.ingredients[0] if provided
        # For simplicity, we search for amenity=restaurant (or fast_food)
        # But if the user provides a term like "pizza", we might want cuisine=pizza
        # Let's keep it simple: search for all restaurants for now, or use the first 'ingredient' as a keyword?
        # The 'ingredients' field in the request might contain the search term if mode is restaurant.
        
        # If specific search term is passed in ingredients
        search_val = "restaurant"
        key = "amenity"
        
        found_shops = shops.find_nearby_shops(
            search_val, 
            request.lat, 
            request.lon, 
            request.radius,
            key=key
        )
    else:
        # 1. Determine the shop type using OpenAI
        shop_tag = shops.get_shop_type(request.ingredients)
        
        # 2. Find nearby shops using Overpass API
        found_shops = shops.find_nearby_shops(
            shop_tag, 
            request.lat, 
            request.lon, 
            request.radius,
            key="shop"
        )
    
    return found_shops

@app.post("/items/", response_model=schemas.Item)
def create_item(item: schemas.ItemCreate, db: Session = Depends(get_db)):
    db_item = models.Item(**item.model_dump())
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item

@app.get("/items/", response_model=list[schemas.Item])
def read_items(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    items = db.query(models.Item).offset(skip).limit(limit).all()
    return items

@app.get("/items/{item_id}", response_model=schemas.Item)
def read_item(item_id: int, db: Session = Depends(get_db)):
    item = db.query(models.Item).filter(models.Item.id == item_id).first()
    if item is None:
        raise HTTPException(status_code=404, detail="Item not found")
    return item

@app.get("/")
async def root():
    return {"message": "Welcome to the FastAPI Backend!"}