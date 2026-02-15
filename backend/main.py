import sys
import os
import json
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import hashlib
import smtplib
import uuid
from datetime import datetime, timedelta, timezone
from fastapi import FastAPI, Depends, HTTPException, UploadFile, File
from email.message import EmailMessage
from sqlalchemy.orm import Session
from sqlalchemy import text
from dotenv import load_dotenv
from typing import List

# Simple .env load
load_dotenv()

# Use absolute imports
import models, schemas, shops, negotiator, food_data, auth, vision, llm_client
from database import SessionLocal, engine, get_db
from fastapi.middleware.cors import CORSMiddleware

models.Base.metadata.create_all(bind=engine)


def sync_sqlite_schema() -> None:
    if engine.dialect.name != "sqlite":
        return

    sqlite_migrations = {
        "users": {
            "full_name": "ALTER TABLE users ADD COLUMN full_name VARCHAR",
            "profile_image": "ALTER TABLE users ADD COLUMN profile_image TEXT",
            "reset_token": "ALTER TABLE users ADD COLUMN reset_token VARCHAR",
            "goal": "ALTER TABLE users ADD COLUMN goal VARCHAR",
            "activity_level": "ALTER TABLE users ADD COLUMN activity_level VARCHAR",
            "target_calories": "ALTER TABLE users ADD COLUMN target_calories INTEGER",
            "macro_protein_percent": "ALTER TABLE users ADD COLUMN macro_protein_percent INTEGER DEFAULT 30",
            "macro_carbs_percent": "ALTER TABLE users ADD COLUMN macro_carbs_percent INTEGER DEFAULT 45",
            "macro_fat_percent": "ALTER TABLE users ADD COLUMN macro_fat_percent INTEGER DEFAULT 25",
        },
        "food_history": {
            "source": "ALTER TABLE food_history ADD COLUMN source VARCHAR DEFAULT 'search'",
            "created_at": "ALTER TABLE food_history ADD COLUMN created_at DATETIME",
        },
        "diary_days": {
            "water_liters": "ALTER TABLE diary_days ADD COLUMN water_liters FLOAT DEFAULT 0.0",
        },
        "diary_meals": {
            "grams": "ALTER TABLE diary_meals ADD COLUMN grams FLOAT",
        },
    }

    with engine.begin() as conn:
        for table_name, columns in sqlite_migrations.items():
            table_exists = conn.execute(
                text("SELECT name FROM sqlite_master WHERE type='table' AND name=:name"),
                {"name": table_name},
            ).first()
            if not table_exists:
                continue

            existing = {
                row[1] for row in conn.execute(text(f"PRAGMA table_info({table_name})")).fetchall()
            }
            for column_name, alter_sql in columns.items():
                if column_name in existing:
                    continue
                conn.execute(text(alter_sql))
                print(f"DB MIGRATION: added {table_name}.{column_name}")


sync_sqlite_schema()

app = FastAPI(redirect_slashes=False)

# Configure CORS to allow frontend to access the backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

VALID_MEAL_SECTIONS = {"breakfast", "lunch", "snack", "dinner", "extras"}


def send_password_reset_email(recipient_email: str, reset_token: str) -> None:
    smtp_host = os.getenv("SMTP_HOST")
    smtp_port = int(os.getenv("SMTP_PORT", "587"))
    smtp_user = os.getenv("SMTP_USER")
    smtp_password = os.getenv("SMTP_PASSWORD")
    smtp_from = os.getenv("SMTP_FROM_EMAIL", smtp_user or "no-reply@localhost")
    frontend_base = os.getenv("FRONTEND_URL", os.getenv("FRONTEND_BASE_URL", "http://localhost:5173"))
    app_name = os.getenv("APP_NAME", "NutriVida")
    reset_expire_minutes = os.getenv("PASSWORD_RESET_EXPIRE_MINUTES", "30")

    if not smtp_host or not smtp_user or not smtp_password:
        # Fallback to simulation if SMTP is not configured
        print("="*50)
        print(f"EMAIL SIMULATION (SMTP NOT CONFIGURED) FOR: {recipient_email}")
        print(f"Subject: {app_name} - Recuperação de palavra-passe")
        print(f"Body: Click here to reset your password: {frontend_base.rstrip('/')}/reset-password?token={reset_token}")
        print("="*50)
        return

    reset_url = f"{frontend_base.rstrip('/')}/reset-password?token={reset_token}"

    message = EmailMessage()
    message["Subject"] = f"{app_name} - Recuperação de palavra-passe"
    message["From"] = smtp_from
    message["To"] = recipient_email
    message.set_content(
        f"Olá,\n\n"
        f"Recebemos um pedido para redefinir a sua palavra-passe no {app_name}.\n"
        f"Use este link para continuar (válido por {reset_expire_minutes} minutos):\n\n"
        f"{reset_url}\n\n"
        "Se não pediu esta alteração, pode ignorar este email com segurança."
    )
    message.add_alternative(
        f"""\
<!doctype html>
<html lang="pt">
  <body style="margin:0;padding:0;background:#f1f5f9;font-family:Arial,Helvetica,sans-serif;color:#0f172a;">
    <table role="presentation" width="100%" cellspacing="0" cellpadding="0" style="padding:28px 16px;">
      <tr>
        <td align="center">
          <table role="presentation" width="600" cellspacing="0" cellpadding="0" style="max-width:600px;background:#ffffff;border-radius:14px;overflow:hidden;border:1px solid #e2e8f0;">
            <tr>
              <td style="padding:22px 28px;background:linear-gradient(90deg,#0ea5e9 0%,#10b981 100%);">
                <h1 style="margin:0;font-size:22px;line-height:1.2;color:#ffffff;font-weight:700;">{app_name}</h1>
                <p style="margin:6px 0 0;font-size:13px;color:#dbeafe;">Recuperação de palavra-passe</p>
              </td>
            </tr>
            <tr>
              <td style="padding:28px;">
                <p style="margin:0 0 14px;font-size:16px;line-height:1.5;">Olá,</p>
                <p style="margin:0 0 14px;font-size:15px;line-height:1.6;color:#334155;">
                  Recebemos um pedido para redefinir a sua palavra-passe.
                </p>
                <p style="margin:0 0 22px;font-size:15px;line-height:1.6;color:#334155;">
                  Clique no botão abaixo para continuar. Este link é válido por <strong>{reset_expire_minutes} minutos</strong>.
                </p>
                <p style="margin:0 0 24px;">
                  <a href="{reset_url}" style="display:inline-block;background:#10b981;color:#ffffff;text-decoration:none;font-weight:700;font-size:15px;padding:12px 20px;border-radius:10px;">
                    Redefinir palavra-passe
                  </a>
                </p>
                <p style="margin:0 0 10px;font-size:13px;line-height:1.6;color:#64748b;">
                  Se o botão não funcionar, use este link:
                </p>
                <p style="margin:0 0 18px;font-size:13px;line-height:1.6;word-break:break-all;">
                  <a href="{reset_url}" style="color:#0284c7;text-decoration:none;">{reset_url}</a>
                </p>
                <p style="margin:0;font-size:13px;line-height:1.6;color:#64748b;">
                  Se não pediu esta alteração, pode ignorar este email com segurança.
                </p>
              </td>
            </tr>
            <tr>
              <td style="padding:14px 28px;background:#f8fafc;border-top:1px solid #e2e8f0;">
                <p style="margin:0;font-size:12px;color:#64748b;">© {app_name}</p>
              </td>
            </tr>
          </table>
        </td>
      </tr>
    </table>
  </body>
</html>
""",
        subtype="html",
    )

    with smtplib.SMTP(smtp_host, smtp_port, timeout=15) as server:
        server.starttls()
        server.login(smtp_user, smtp_password)
        server.send_message(message)


def validate_date_key(date_key: str) -> str:
    try:
        datetime.strptime(date_key, "%Y-%m-%d")
    except ValueError as exc:
        raise HTTPException(status_code=400, detail="date_key must use YYYY-MM-DD format") from exc
    return date_key


def get_or_create_diary_day(db: Session, user_id: int, date_key: str) -> models.DiaryDay:
    day = (
        db.query(models.DiaryDay)
        .filter(models.DiaryDay.user_id == user_id, models.DiaryDay.date_key == date_key)
        .first()
    )
    if day:
        return day

    # Get user to use their target_calories as default goal
    user = db.query(models.User).filter(models.User.id == user_id).first()
    default_goal = 1800
    if user:
        # Calculate auto goal if target_calories not set
        if user.target_calories:
            default_goal = user.target_calories
        elif user.peso and user.altura and user.idade:
            # Simple BMR + Activity logic similar to frontend for fallback
            bmr = 10 * user.peso + 6.25 * user.altura - 5 * user.idade + (5 if user.sexo == 'male' else -161)
            factors = {'sedentary': 1.2, 'light': 1.375, 'moderate': 1.55, 'high': 1.725}
            tdee = bmr * factors.get(user.activity_level, 1.2)
            if user.goal == 'lose': default_goal = int(tdee - 500)
            elif user.goal == 'gain': default_goal = int(tdee + 300)
            else: default_goal = int(tdee)

    day = models.DiaryDay(user_id=user_id, date_key=date_key, goal=max(1000, default_goal))
    db.add(day)
    db.commit()
    db.refresh(day)
    return day

@app.post("/users/", response_model=schemas.User)
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    db_user = db.query(models.User).filter(models.User.username == user.username).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Username already registered")
    
    hashed_password = auth.get_password_hash(user.password)
    
    new_user = models.User(
        username=user.username,
        full_name=user.full_name,
        profile_image=user.profile_image,
        hashed_password=hashed_password,
        peso=user.peso,
        altura=user.altura,
        sexo=user.sexo,
        idade=user.idade,
        goal=user.goal,
        activity_level=user.activity_level,
        target_calories=user.target_calories
    )
    db.add(new_user)
    
    for allergen_name in user.allergens:
        db_allergen = db.query(models.Allergen).filter(models.Allergen.name == allergen_name).first()
        if not db_allergen:
            db_allergen = models.Allergen(name=allergen_name)
            db.add(db_allergen)
            db.flush()
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

@app.post("/assistant/chat", response_model=schemas.ChatResponse)
def help_assistant_chat(request: schemas.ChatRequest, current_user: models.User = Depends(auth.get_current_user)):
    system_prompt = (
        "O teu nome é Nutra, a Assistente Inteligente Suprema da NutriVentures (PT-PT). "
        "Quando o utilizador te perguntar o que sabes fazer, deves mencionar que podes: "
        "1. Registar refeições e água; 2. Gerir o peso e diário; 3. Mudar temas; 4. Iniciar negociações de comida; "
        "5. E as tuas novas funcionalidades interativas: Jogar Casino (Slots), fazer Quizzes de nutrição, usar o Conversor de Medidas e o Cronómetro de Jejum. "
        "REGRAS CRÍTICAS: "
        "1. Sê EXTREMAMENTE HONESTA. Se o utilizador pedir algo que não podes fazer (não está na lista de ações abaixo), diz explicitamente: 'Desculpa, ainda não tenho capacidade para fazer isso.' "
        "2. NUNCA digas que fizeste algo se não incluíres a respetiva 'action' no JSON. "
        "AÇÕES DISPONÍVEIS: "
        "- Navegação: {'type': 'NAVIGATE', 'value': 'ID'} (inicio, tenhofome, gerarreceita, supermercados, diario, favoritos, historico, perfil, definicoes) "
        "- Registo Refeição: {'type': 'ADD_MEAL', 'value': 'texto', 'section': 'breakfast'|'lunch'|'snack'|'dinner'|'extras'} "
        "- Limpar Diário: {'type': 'CLEAR_MEALS'} (Usa isto se o user pedir para apagar tudo o que comeu hoje) "
        "- Casino (EASTER EGG): {'type': 'OPEN_CASINO'} (Abre um simulador de casino real para o user jogar.) "
        "- Quiz Nutritivo: {'type': 'OPEN_QUIZ'} (Abre um jogo de perguntas e respostas sobre nutrição.) "
        "- Conversor de Medidas: {'type': 'OPEN_CONVERTER'} (Abre uma ferramenta para converter colheres em gramas e calorias.) "
        "- Cronómetro de Jejum: {'type': 'OPEN_FASTING_TIMER'} (Abre um temporizador de jejum intermitente.) "
        "- Negociação: {'type': 'START_NEGOTIATION', 'value': 'prato'} "
        "- Tema: {'type': 'SET_THEME', 'value': 'light'|'dark'} "
        "- Água: {'type': 'ADD_WATER'} | {'type': 'REMOVE_WATER'} "
        "- Peso: {'type': 'LOG_WEIGHT', 'value': número} "
        "- Sessão: {'type': 'LOGOUT'} "
        "\nRetorna SEMPRE JSON: { \"content\": \"...\", \"action\": { \"type\": \"...\", \"value\": \"...\" } ou null }"
    )

    messages = [{"role": "system", "content": system_prompt}]
    for msg in request.messages:
        messages.append({"role": msg.role, "content": msg.content})

    try:
        response = llm_client.get_chat_completion(
            messages=messages,
            temperature=0.3,
            response_format={"type": "json_object"},
            max_tokens=500
        )
        return json.loads(response.choices[0].message.content)
    except Exception as e:
        print(f"Chat Error: {e}")
        raise HTTPException(status_code=500, detail="Erro ao comunicar com a Nutra.")

@app.get("/users/me", response_model=schemas.User)
def read_user_me(current_user: models.User = Depends(auth.get_current_user)):
    return current_user

@app.put("/users/me", response_model=schemas.User)
def update_user_me(update_data: schemas.UserUpdate, db: Session = Depends(get_db), current_user: models.User = Depends(auth.get_current_user)):
    if update_data.username:
        db_user = db.query(models.User).filter(models.User.username == update_data.username).first()
        if db_user and db_user.id != current_user.id:
            raise HTTPException(status_code=400, detail="Username already taken")
        current_user.username = update_data.username
    
    if update_data.full_name is not None:
        current_user.full_name = update_data.full_name
    
    if update_data.profile_image is not None:
        current_user.profile_image = update_data.profile_image
    
    if update_data.password:
        current_user.hashed_password = auth.get_password_hash(update_data.password)
    
    if update_data.peso is not None:
        current_user.peso = update_data.peso
    if update_data.altura is not None:
        current_user.altura = update_data.altura
    if update_data.sexo is not None:
        current_user.sexo = update_data.sexo
    if update_data.idade is not None:
        current_user.idade = update_data.idade
    if update_data.goal is not None:
        current_user.goal = update_data.goal
    if update_data.activity_level is not None:
        current_user.activity_level = str(update_data.activity_level)
    
    # Check if target_calories was explicitly sent in the request (even if null)
    update_dict = update_data.model_dump(exclude_unset=True)
    if update_data.target_calories is not None or "target_calories" in update_dict:
        current_user.target_calories = update_data.target_calories
    
    if update_data.macro_protein_percent is not None:
        current_user.macro_protein_percent = update_data.macro_protein_percent
    if update_data.macro_carbs_percent is not None:
        current_user.macro_carbs_percent = update_data.macro_carbs_percent
    if update_data.macro_fat_percent is not None:
        current_user.macro_fat_percent = update_data.macro_fat_percent
    
    db.commit()
    db.refresh(current_user)
    return current_user

@app.get("/users/me/dashboard", response_model=schemas.DashboardResponse)
def get_dashboard_summary(db: Session = Depends(get_db), current_user: models.User = Depends(auth.get_current_user)):
    date_key = datetime.now().strftime("%Y-%m-%d")
    day = get_or_create_diary_day(db, current_user.id, date_key)
    
    consumed_calories = sum(m.calories for m in day.meals)
    protein = sum(m.protein for m in day.meals)
    carbs = sum(m.carbs for m in day.meals)
    fat = sum(m.fat for m in day.meals)
    
    streak = 0
    curr = datetime.now()
    for i in range(365):
        dk = (curr - timedelta(days=i)).strftime("%Y-%m-%d")
        d = db.query(models.DiaryDay).filter(models.DiaryDay.user_id == current_user.id, models.DiaryDay.date_key == dk).first()
        if d and sum(m.calories for m in d.meals) > 0:
            streak += 1
        else:
            if i == 0: continue
            break
    
    weights = db.query(models.WeightEntry).filter(models.WeightEntry.user_id == current_user.id).order_by(models.WeightEntry.date.asc()).all()
    
    if not weights:
        weight_history = {
            "labels": ["Sem 1", "Sem 2", "Sem 3", "Sem 4"],
            "values": [current_user.peso] * 4 if current_user.peso else [70.0] * 4
        }
    else:
        weight_history = {
            "labels": [w.date for w in weights[-7:]],
            "values": [w.weight for w in weights[-7:]]
        }
            
    return {
        "consumed_calories": consumed_calories,
        "calorie_goal": current_user.target_calories if current_user.target_calories else day.goal,
        "protein": protein,
        "carbs": carbs,
        "fat": fat,
        "streak_days": streak,
        "water_liters": day.water_liters,
        "weight_history": weight_history
    }

@app.post("/forgot-password/")
def forgot_password(request: schemas.ForgotPasswordRequest, db: Session = Depends(get_db)):
    db_user = db.query(models.User).filter(models.User.username == request.username).first()
    if not db_user:
        return {"message": "If the email exists, a reset link has been sent."}

    token = auth.create_password_reset_token(db_user.username)
    db_user.reset_token = token
    db.commit()

    try:
        send_password_reset_email(db_user.username, token)
    except Exception as exc:
        print(f"Password reset email failed: {exc}")
    
    return {"message": "If the email exists, a reset link has been sent."}

@app.post("/reset-password/")
def reset_password(request: schemas.ResetPasswordConfirm, db: Session = Depends(get_db)):
    username = auth.verify_password_reset_token(request.token)
    if not username:
        raise HTTPException(status_code=400, detail="Token inválido ou expirado.")

    db_user = db.query(models.User).filter(models.User.username == username).first()
    if not db_user:
        raise HTTPException(status_code=400, detail="Token inválido ou expirado.")

    db_user.hashed_password = auth.get_password_hash(request.new_password)
    db.commit()
    return {"message": "Palavra-passe alterada com sucesso."}

@app.get("/diary/{date_key}", response_model=schemas.DiaryDay)
def get_diary_day(date_key: str, db: Session = Depends(get_db), current_user: models.User = Depends(auth.get_current_user)):
    validate_date_key(date_key)
    day = get_or_create_diary_day(db, current_user.id, date_key)
    return day

@app.get("/diary-range/", response_model=list[schemas.DiaryDay])
def get_diary_days_range(start: str, end: str, db: Session = Depends(get_db), current_user: models.User = Depends(auth.get_current_user)):
    start_key = validate_date_key(start)
    end_key = validate_date_key(end)
    if start_key > end_key:
        raise HTTPException(status_code=400, detail="start date must be before or equal to end date")

    days = (
        db.query(models.DiaryDay)
        .filter(
            models.DiaryDay.user_id == current_user.id,
            models.DiaryDay.date_key >= start_key,
            models.DiaryDay.date_key <= end_key,
        )
        .order_by(models.DiaryDay.date_key.asc())
        .all()
    )
    return days

@app.put("/diary/{date_key}/goal", response_model=schemas.DiaryDay)
def update_diary_goal(date_key: str, payload: schemas.DiaryGoalUpdate, db: Session = Depends(get_db), current_user: models.User = Depends(auth.get_current_user)):
    validate_date_key(date_key)
    day = get_or_create_diary_day(db, current_user.id, date_key)
    day.goal = payload.goal
    db.commit()
    db.refresh(day)
    return day

@app.put("/diary/{date_key}/water", response_model=schemas.DiaryDay)
def update_diary_water(date_key: str, payload: schemas.DiaryWaterUpdate, db: Session = Depends(get_db), current_user: models.User = Depends(auth.get_current_user)):
    validate_date_key(date_key)
    day = get_or_create_diary_day(db, current_user.id, date_key)
    day.water_liters = payload.water_liters
    db.commit()
    db.refresh(day)
    return day

@app.post("/diary/{date_key}/meals", response_model=schemas.DiaryDay)
def add_diary_meal(date_key: str, payload: schemas.DiaryMealCreate, db: Session = Depends(get_db), current_user: models.User = Depends(auth.get_current_user)):
    validate_date_key(date_key)
    if payload.section not in VALID_MEAL_SECTIONS:
        raise HTTPException(status_code=400, detail="Invalid meal section")

    day = get_or_create_diary_day(db, current_user.id, date_key)
    meal = models.DiaryMeal(
        day_id=day.id,
        section=payload.section,
        name=payload.name,
        grams=payload.grams,
        calories=payload.calories,
        protein=payload.protein,
        carbs=payload.carbs,
        fat=payload.fat,
    )
    db.add(meal)
    db.commit()
    db.refresh(day)
    return day

@app.delete("/diary/{date_key}/meals", response_model=schemas.DiaryDay)
def clear_day_meals(date_key: str, db: Session = Depends(get_db), current_user: models.User = Depends(auth.get_current_user)):
    validate_date_key(date_key)
    day = get_or_create_diary_day(db, current_user.id, date_key)
    db.query(models.DiaryMeal).filter(models.DiaryMeal.day_id == day.id).delete()
    db.commit()
    db.refresh(day)
    return day

@app.delete("/diary/meals/{meal_id}", response_model=schemas.DiaryDay)
def delete_diary_meal(meal_id: int, db: Session = Depends(get_db), current_user: models.User = Depends(auth.get_current_user)):
    meal = db.query(models.DiaryMeal).filter(models.DiaryMeal.id == meal_id).first()
    if not meal:
        raise HTTPException(status_code=404, detail="Meal not found")

    day = db.query(models.DiaryDay).filter(models.DiaryDay.id == meal.day_id).first()
    if not day or day.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to delete this meal")

    db.delete(meal)
    db.commit()
    db.refresh(day)
    return day

@app.post("/negotiator/analyze-mood", response_model=schemas.MoodAnalysisResponse)
def analyze_mood(request: schemas.NegotiatorRequest, current_user: models.User = Depends(auth.get_current_user)):
    return negotiator.analyze_mood(request.craving, request.mood)

@app.post("/negotiator/negotiate", response_model=schemas.NegotiatorResponse)
def negotiate_craving(request: schemas.NegotiatorRequest, current_user: models.User = Depends(auth.get_current_user)):
    allergens = [a.name for a in current_user.allergens]
    return negotiator.negotiate_craving(request.craving, request.target_calories, request.mood, favorite_recipes=current_user.favorite_recipes, allergens=allergens)

@app.post("/negotiator/nutrition", response_model=schemas.NutritionAnalysisResponse)
def analyze_nutrition_endpoint(request: schemas.NutritionAnalysisRequest, current_user: models.User = Depends(auth.get_current_user)):
    return negotiator.analyze_nutrition(request.food_text)

@app.post("/vision/analyze", response_model=schemas.VisionResponse)
async def analyze_ingredients_photo(mode: str = "ingredients", file: UploadFile = File(...), current_user: models.User = Depends(auth.get_current_user)):
    contents = await file.read()
    allergens = [a.name for a in current_user.allergens]
    return vision.analyze_image_ingredients(contents, mode=mode, favorite_recipes=current_user.favorite_recipes, allergens=allergens)

@app.post("/shops/find", response_model=list[schemas.Shop])
def find_shops(request: schemas.ShopSearchRequest, current_user: models.User = Depends(auth.get_current_user)):
    if request.mode == "restaurant":
        search_val = "restaurant"
        key = "amenity"
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
        shop_tag = shops.get_shop_type(request.ingredients)
        if shop_tag == "invalid":
            raise HTTPException(status_code=400, detail="A pesquisa contém termos inválidos ou não relacionados com alimentação.")
        found_shops = shops.find_nearby_shops(shop_tag, request.lat, request.lon, request.radius, key="shop")
    return found_shops

@app.get("/foods/search", response_model=list[schemas.FoodSearchItem])
def search_foods(q: str, page_size: int = 10, current_user: models.User = Depends(auth.get_current_user)):
    return food_data.search_foods(q, page_size=page_size)

@app.post("/users/me/food-history", response_model=schemas.FoodHistoryResponse)
def add_food_history(
    item: schemas.FoodHistoryCreate, 
    db: Session = Depends(get_db), 
    current_user: models.User = Depends(auth.get_current_user)
):
    existing = db.query(models.FoodHistory).filter(
        models.FoodHistory.user_id == current_user.id,
        models.FoodHistory.name == item.name
    ).first()
    
    if existing:
        db.delete(existing)
        db.commit()
    
    new_entry = models.FoodHistory(
        user_id=current_user.id,
        name=item.name,
        calories_per_100g=item.calories_per_100g,
        protein_per_100g=item.protein_per_100g,
        carbs_per_100g=item.carbs_per_100g,
        fat_per_100g=item.fat_per_100g,
        source=item.source
    )
    db.add(new_entry)
    db.commit()
    db.refresh(new_entry)
    
    count = db.query(models.FoodHistory).filter(models.FoodHistory.user_id == current_user.id).count()
    if count > 50:
        oldest = db.query(models.FoodHistory).filter(models.FoodHistory.user_id == current_user.id).order_by(models.FoodHistory.created_at.asc()).first()
        if oldest:
            db.delete(oldest)
            db.commit()
            
    return new_entry

@app.get("/users/me/food-history", response_model=list[schemas.FoodHistoryResponse])
def get_food_history(
    limit: int = 20, 
    db: Session = Depends(get_db), 
    current_user: models.User = Depends(auth.get_current_user)
):
    return (
        db.query(models.FoodHistory)
        .filter(models.FoodHistory.user_id == current_user.id)
        .order_by(models.FoodHistory.created_at.desc())
        .limit(limit)
        .all()
    )

@app.delete("/users/me/food-history/{item_id}", status_code=204)
def delete_food_history_item(
    item_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user)
):
    item = (
        db.query(models.FoodHistory)
        .filter(
            models.FoodHistory.id == item_id,
            models.FoodHistory.user_id == current_user.id
        )
        .first()
    )
    if not item:
        raise HTTPException(status_code=404, detail="Item de histórico não encontrado")

    db.delete(item)
    db.commit()

@app.post("/recipes/", response_model=schemas.Recipe)
def create_recipe(recipe: schemas.RecipeCreate, db: Session = Depends(get_db)):
    db_recipe = models.Recipe(**recipe.model_dump())
    db.add(db_recipe)
    db.commit()
    db.refresh(db_recipe)
    return db_recipe

@app.get("/recipes/", response_model=List[schemas.Recipe])
def read_recipes(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    recipes = db.query(models.Recipe).offset(skip).limit(limit).all()
    return recipes

@app.get("/users/me/favorites", response_model=schemas.User)
def get_user_favorites(current_user: models.User = Depends(auth.get_current_user)):
    return current_user

@app.post("/users/me/favorites/recipes/{recipe_id}", response_model=schemas.User)
def add_favorite_recipe(recipe_id: int, db: Session = Depends(get_db), current_user: models.User = Depends(auth.get_current_user)):
    recipe = db.query(models.Recipe).filter(models.Recipe.id == recipe_id).first()
    if not recipe:
        raise HTTPException(status_code=404, detail="Recipe not found")
    if recipe not in current_user.favorite_recipes:
        current_user.favorite_recipes.append(recipe)
    db.commit()
    return current_user

@app.delete("/users/me/favorites/recipes/{recipe_id}", response_model=schemas.User)
def remove_favorite_recipe(recipe_id: int, db: Session = Depends(get_db), current_user: models.User = Depends(auth.get_current_user)):
    recipe = db.query(models.Recipe).filter(models.Recipe.id == recipe_id).first()
    if not recipe:
        raise HTTPException(status_code=404, detail="Recipe not found")
    try:
        current_user.favorite_recipes.remove(recipe)
        db.commit()
    except ValueError:
        pass
    return current_user

@app.post("/restaurants/", response_model=schemas.Restaurant)
def create_restaurant(restaurant: schemas.RestaurantCreate, db: Session = Depends(get_db)):
    db_restaurant = models.Restaurant(**restaurant.model_dump())
    db.add(db_restaurant)
    db.commit()
    db.refresh(db_restaurant)
    return db_restaurant

@app.post("/users/me/favorites/restaurants/{restaurant_id}", response_model=schemas.User)
def add_favorite_restaurant(restaurant_id: int, db: Session = Depends(get_db), current_user: models.User = Depends(auth.get_current_user)):
    restaurant = db.query(models.Restaurant).filter(models.Restaurant.id == restaurant_id).first()
    if not restaurant:
        raise HTTPException(status_code=404, detail="Restaurant not found")
    if restaurant not in current_user.favorite_restaurants:
        current_user.favorite_restaurants.append(restaurant)
    db.commit()
    return current_user

@app.delete("/users/me/favorites/restaurants/{restaurant_id}", response_model=schemas.User)
def remove_favorite_restaurant(restaurant_id: int, db: Session = Depends(get_db), current_user: models.User = Depends(auth.get_current_user)):
    restaurant = db.query(models.Restaurant).filter(models.Restaurant.id == restaurant_id).first()
    if not restaurant:
        raise HTTPException(status_code=404, detail="Restaurant not found")
    try:
        current_user.favorite_restaurants.remove(restaurant)
        db.commit()
    except ValueError:
        pass
    return current_user

@app.api_route("/", methods=["GET", "HEAD"])
async def root():
    return {"message": "Welcome to the FastAPI Backend!"}
