import os
import sys
from sqlalchemy.orm import Session
from datetime import datetime, timedelta

# Ensure the backend directory is in the path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database import SessionLocal, engine
import models, auth

def seed_db():
    # Create tables if they don't exist
    models.Base.metadata.create_all(bind=engine)
    
    db = SessionLocal()
    
    try:
        # 1. Seed Allergens
        allergens = ["Glúten", "Laticínios", "Ovos", "Frutos de Casca Rija", "Peixe", "Marisco", "Soja", "Amendoim"]
        db_allergens = []
        for name in allergens:
            existing = db.query(models.Allergen).filter(models.Allergen.name == name).first()
            if not existing:
                a = models.Allergen(name=name)
                db.add(a)
                db_allergens.append(a)
            else:
                db_allergens.append(existing)
        db.commit()
        print(f"Seeded {len(db_allergens)} allergens.")

        # 2. Seed a Demo User
        test_user = db.query(models.User).filter(models.User.username == "demo").first()
        if not test_user:
            hashed_pw = auth.get_password_hash("demo1234")
            test_user = models.User(
                username="demo",
                full_name="Utilizador Demo",
                hashed_password=hashed_pw,
                peso=75.5,
                altura=1.75,
                sexo="M",
                idade=25,
                goal="Manter Peso",
                activity_level="Moderado",
                target_calories=2200
            )
            # Add some allergens to demo user
            test_user.allergens.append(db_allergens[0]) # Glúten
            test_user.allergens.append(db_allergens[1]) # Laticínios
            db.add(test_user)
            db.commit()
            db.refresh(test_user)
            print("Created demo user 'demo' with password 'demo1234'")
        
        # 3. Seed some Recipes
        recipes = [
            {
                "name": "Salada de Frango com Abacate",
                "ingredients": "Peito de frango, abacate, alface, tomate, azeite",
                "instructions": "Grelha o frango. Corta o abacate e o tomate. Mistura tudo com alface e tempera com azeite."
            },
            {
                "name": "Omelete de Espinafres",
                "ingredients": "2 ovos, espinafres frescos, sal, pimenta",
                "instructions": "Bate os ovos. Salteia os espinafres numa frigideira. Adiciona os ovos e cozinha até estar pronto."
            },
            {
                "name": "Arroz de Atum Saudável",
                "ingredients": "Arroz integral, atum ao natural, cebola, cenoura",
                "instructions": "Cozinha o arroz. Refoga a cebola e a cenoura picada. Adiciona o atum e mistura com o arroz."
            }
        ]
        
        for r_data in recipes:
            existing = db.query(models.Recipe).filter(models.Recipe.name == r_data["name"]).first()
            if not existing:
                r = models.Recipe(**r_data)
                db.add(r)
        db.commit()
        print("Seeded basic recipes.")

        # 4. Seed Weight History for demo user
        if test_user:
            today = datetime.now()
            for i in range(5):
                date_str = (today - timedelta(days=i*7)).strftime("%Y-%m-%d")
                existing = db.query(models.WeightEntry).filter(
                    models.WeightEntry.user_id == test_user.id, 
                    models.WeightEntry.date == date_str
                ).first()
                if not existing:
                    w = models.WeightEntry(
                        user_id=test_user.id,
                        weight=75.5 + (i * 0.5),
                        date=date_str
                    )
                    db.add(w)
            db.commit()
            print("Seeded weight history for demo user.")

        # 5. Seed Diary for today
        today_key = datetime.now().strftime("%Y-%m-%d")
        existing_day = db.query(models.DiaryDay).filter(
            models.DiaryDay.user_id == test_user.id,
            models.DiaryDay.date_key == today_key
        ).first()
        
        if not existing_day:
            day = models.DiaryDay(user_id=test_user.id, date_key=today_key, goal=2200, water_liters=1.5)
            db.add(day)
            db.flush()
            
            breakfast = models.DiaryMeal(
                day_id=day.id,
                section="breakfast",
                name="Pão Integral com Queijo",
                grams=100,
                calories=250,
                protein=12,
                carbs=35,
                fat=8
            )
            db.add(breakfast)
            db.commit()
            print("Seeded today's diary for demo user.")

        print("\nDatabase seeding completed successfully!")

    except Exception as e:
        db.rollback()
        print(f"Error seeding database: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    seed_db()
