import os
import sys
from sqlalchemy import text
from database import engine, Base
import models

def run_migrations():
    print(f"Iniciando migrações no motor: {engine.dialect.name}")
    
    # 1. Criar tabelas que não existam
    print("Verificando/Criando tabelas...")
    Base.metadata.create_all(bind=engine)
    
    # 2. Adicionar colunas em falta (Lógica idêntica ao main.py)
    migrations = {
        "users": {
            "full_name": "ALTER TABLE users ADD COLUMN full_name VARCHAR",
            "profile_image": "ALTER TABLE users ADD COLUMN profile_image TEXT",
            "reset_token": "ALTER TABLE users ADD COLUMN reset_token VARCHAR",
            "goal": "ALTER TABLE users ADD COLUMN goal VARCHAR",
            "activity_level": "ALTER TABLE users ADD COLUMN activity_level VARCHAR",
        },
        "food_history": {
            "source": "ALTER TABLE food_history ADD COLUMN source VARCHAR DEFAULT 'search'",
            "created_at": "ALTER TABLE food_history ADD COLUMN created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP",
        },
        "diary_meals": {
            "grams": "ALTER TABLE diary_meals ADD COLUMN grams FLOAT",
        },
    }

    with engine.begin() as conn:
        for table_name, columns in migrations.items():
            # Verificar se a tabela existe
            if engine.dialect.name == "sqlite":
                check_sql = "SELECT name FROM sqlite_master WHERE type='table' AND name=:name"
            else:
                check_sql = "SELECT tablename FROM pg_catalog.pg_tables WHERE tablename=:name"
            
            if not conn.execute(text(check_sql), {"name": table_name}).first():
                print(f"Tabela {table_name} ainda não existe, saltando colunas.")
                continue

            # Obter colunas atuais
            if engine.dialect.name == "sqlite":
                existing = {row[1] for row in conn.execute(text(f"PRAGMA table_info({table_name})")).fetchall()}
            else:
                existing = {row[0] for row in conn.execute(
                    text("SELECT column_name FROM information_schema.columns WHERE table_name=:name"),
                    {"name": table_name}
                ).fetchall()}

            for col, sql in columns.items():
                if col not in existing:
                    try:
                        # Ajuste para SQLite
                        if engine.dialect.name == "sqlite" and "TIMESTAMP" in sql:
                            sql = sql.replace("TIMESTAMP", "DATETIME")
                        
                        conn.execute(text(sql))
                        print(f"SUCESSO: Coluna '{col}' adicionada à tabela '{table_name}'.")
                    except Exception as e:
                        print(f"ERRO ao adicionar '{col}': {e}")
                else:
                    print(f"OK: Coluna '{col}' já existe em '{table_name}'.")

    print("Migrações concluídas!")

if __name__ == "__main__":
    run_migrations()
