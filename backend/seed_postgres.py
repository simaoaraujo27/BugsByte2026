import os
import sys
import random
from sqlalchemy.orm import Session
from datetime import datetime, timedelta

# Ensure the backend directory is in the path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database import SessionLocal, engine
import models, auth

def seed_db():
    print("Starting massive database seeding...")
    # Create tables if they don't exist
    models.Base.metadata.create_all(bind=engine)
    
    db = SessionLocal()
    
    try:
        # 1. Seed Allergens (~15)
        allergen_names = [
            "Glúten", "Laticínios", "Ovos", "Frutos de Casca Rija", "Peixe", 
            "Marisco", "Soja", "Amendoim", "Sésamo", "Mostarda", 
            "Aipo", "Dióxido de Enxofre", "Tremoço", "Moluscos", "Milho"
        ]
        db_allergens = []
        for name in allergen_names:
            existing = db.query(models.Allergen).filter(models.Allergen.name == name).first()
            if not existing:
                a = models.Allergen(name=name)
                db.add(a)
                db_allergens.append(a)
            else:
                db_allergens.append(existing)
        db.commit()
        print(f"Total Allergens: {len(db_allergens)}")

        # 2. Seed Users (10 users)
        users = []
        hashed_pw = auth.get_password_hash("password123")
        goals = ["Perder Peso", "Ganhar Massa", "Manter Peso", "Melhorar Performance"]
        activity_levels = ["Sedentário", "Ligeiro", "Moderado", "Ativo", "Muito Ativo"]
        
        for i in range(1, 11):
            username = f"user{i}"
            existing = db.query(models.User).filter(models.User.username == username).first()
            if not existing:
                u = models.User(
                    username=username,
                    full_name=f"Utilizador Teste {i}",
                    hashed_password=hashed_pw,
                    peso=random.uniform(60.0, 95.0),
                    altura=random.uniform(1.55, 1.95),
                    sexo=random.choice(["M", "F"]),
                    idade=random.randint(18, 60),
                    goal=random.choice(goals),
                    activity_level=random.choice(activity_levels),
                    target_calories=random.randint(1800, 3000)
                )
                # Assign 0-2 random allergens
                assigned_allergens = random.sample(db_allergens, k=random.randint(0, 2))
                for alg in assigned_allergens:
                    u.allergens.append(alg)
                db.add(u)
                users.append(u)
            else:
                users.append(existing)
        db.commit()
        print(f"Total Users: {len(users)}")

        # 3. Seed Recipes (50 recipes)
        recipe_bases = ["Frango", "Salmão", "Atum", "Tofu", "Ovos", "Peru", "Grão", "Feijão", "Massa", "Arroz"]
        recipe_styles = ["Grelhado", "ao Forno", "Salteado", "Cozido", "em Salada", "Estufado"]
        
        for i in range(50):
            base = random.choice(recipe_bases)
            style = random.choice(recipe_styles)
            name = f"{base} {style} Saudável {i+1}"
            existing = db.query(models.Recipe).filter(models.Recipe.name == name).first()
            if not existing:
                r = models.Recipe(
                    name=name,
                    ingredients=f"Base de {base}, legumes variados, temperos naturais, azeite.",
                    instructions=f"1. Preparar a base de {base}. 2. {style} os ingredientes. 3. Servir com acompanhamento saudável."
                )
                db.add(r)
        db.commit()
        print("Seeded 50 Recipes.")

        # 4. Seed Restaurants (20 entries)
        restaurant_names = ["Bio Sabor", "Horta no Prato", "Puro Verde", "Saúde na Mesa", "Fit Food", "Natural Gourmet", "The Green Leaf"]
        for i in range(20):
            name = f"{random.choice(restaurant_names)} {i+1}"
            r = models.Restaurant(
                name=name,
                address=f"Rua das Flores, {random.randint(1, 200)}, Cidade",
                phone=f"912345{i:03d}"
            )
            db.add(r)
        db.commit()
        print("Seeded 20 Restaurants.")

        # 5. Seed Weight History (200 entries: 20 per user)
        for u in users:
            start_weight = u.peso
            today = datetime.now()
            for i in range(20):
                date_str = (today - timedelta(days=i*7)).strftime("%Y-%m-%d")
                # Simulate slight weight fluctuation
                w = models.WeightEntry(
                    user_id=u.id,
                    weight=start_weight + random.uniform(-2.0, 2.0),
                    date=date_str
                )
                db.add(w)
        db.commit()
        print("Seeded 200 Weight Entries.")

        # 6. Seed Diary Days and Meals (~600 entries)
        # 15 days per user, 4 meals per day
        meal_names = {
            "breakfast": ["Pão Integral", "Iogurte com Aveia", "Omelete de Claras", "Batido de Fruta"],
            "lunch": ["Frango com Arroz", "Salada de Atum", "Peixe Grelhado", "Massa Integral com Tofu"],
            "snack": ["Fruta", "Frutos Secos", "Gelatina", "Queijo Fresco"],
            "dinner": ["Sopa de Legumes", "Omelete de Espinafres", "Peru com Brócolos", "Salmão ao Forno"],
            "extras": ["Chocolate Negro", "Biscoito de Arroz", "Infusão"]
        }

        for u in users:
            for d in range(15):
                date_key = (datetime.now() - timedelta(days=d)).strftime("%Y-%m-%d")
                # Create or get day
                day = db.query(models.DiaryDay).filter(
                    models.DiaryDay.user_id == u.id, 
                    models.DiaryDay.date_key == date_key
                ).first()
                if not day:
                    day = models.DiaryDay(
                        user_id=u.id,
                        date_key=date_key,
                        goal=u.target_calories or 2000,
                        water_liters=random.uniform(1.0, 3.0)
                    )
                    db.add(day)
                    db.flush()
                
                # Add 3-5 meals per day
                sections = ["breakfast", "lunch", "snack", "dinner"]
                if random.random() > 0.5: sections.append("extras")
                
                for section in sections:
                    m = models.DiaryMeal(
                        day_id=day.id,
                        section=section,
                        name=random.choice(meal_names[section]),
                        grams=random.uniform(50, 400),
                        calories=random.randint(100, 700),
                        protein=random.uniform(5, 40),
                        carbs=random.uniform(10, 60),
                        fat=random.uniform(2, 25)
                    )
                    db.add(m)
        db.commit()
        print("Seeded ~600 Diary Meals across 150 Diary Days.")

        # 7. Seed Food History (100 entries: 10 per user)
        common_foods = [
            ("Ovo", 155, 13, 1, 11), ("Banana", 89, 1, 23, 0), ("Frango", 165, 31, 0, 3),
            ("Arroz", 130, 2, 28, 0), ("Abacate", 160, 2, 9, 15), ("Maçã", 52, 0, 14, 0),
            ("Nozes", 654, 15, 14, 65), ("Iogurte", 59, 10, 4, 0)
        ]
        for u in users:
            for i in range(10):
                food = random.choice(common_foods)
                fh = models.FoodHistory(
                    user_id=u.id,
                    name=f"{food[0]} {i+1}",
                    calories_per_100g=food[1],
                    protein_per_100g=food[2],
                    carbs_per_100g=food[3],
                    fat_per_100g=food[4],
                    source="search"
                )
                db.add(fh)
        db.commit()
        print("Seeded 100 Food History entries.")

        print("\nSUCCESS: Seeding completed with over 1000 entries total!")

    except Exception as e:
        db.rollback()
        print(f"FATAL ERROR during seeding: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    seed_db()
