import hashlib
from sqlalchemy.orm import Session
from database import SessionLocal, engine
import models
import auth

def seed_db():
    print("A inicializar tabelas no Supabase...")
    models.Base.metadata.create_all(bind=engine)
    
    db = SessionLocal()
    try:
        test_username = "hackathon_tester"
        existing_user = db.query(models.User).filter(models.User.username == test_username).first()
        
        if not existing_user:
            print(f"A criar utilizador de teste: {test_username}")
            new_user = models.User(
                username=test_username,
                hashed_password=auth.get_password_hash("test1234"),
                peso=75.5,
                altura=175.0,
                sexo="Masculino",
                idade=25,
                goal="Manter Peso",
                activity_level="Moderado"
            )
            db.add(new_user)
            db.commit()
            print("Utilizador criado com sucesso!")
        else:
            print("Utilizador já existe.")

        print("\nSupabase configurado e pronto a usar! 🚀")
    except Exception as e:
        print(f"ERRO CRÍTICO: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    seed_db()
