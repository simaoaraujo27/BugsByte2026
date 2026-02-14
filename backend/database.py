import os
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

load_dotenv()

# Prioridade 1: Credenciais explícitas do Supabase
USER = os.getenv("user")
PASSWORD = os.getenv("password")
HOST = os.getenv("host")
PORT = os.getenv("port")
DBNAME = os.getenv("dbname")

if USER and PASSWORD and HOST:
    SQLALCHEMY_DATABASE_URL = f"postgresql+psycopg2://{USER}:{PASSWORD}@{HOST}:{PORT or '5432'}/{DBNAME or 'postgres'}?sslmode=require"
else:
    # Prioridade 2: DATABASE_URL (com conversão para postgresql:// se necessário)
    url = os.getenv("DATABASE_URL", "sqlite:///./sql_app.db")
    if url.startswith("postgres://"):
        url = url.replace("postgres://", "postgresql://", 1)
    SQLALCHEMY_DATABASE_URL = url

# Configuração do Engine
if SQLALCHEMY_DATABASE_URL.startswith("sqlite"):
    engine = create_engine(
        SQLALCHEMY_DATABASE_URL, 
        connect_args={"check_same_thread": False} # Necessário para SQLite
    )
    print(f"DATABASE: Using SQLite ({SQLALCHEMY_DATABASE_URL})")
else:
    from sqlalchemy.pool import NullPool
    engine = create_engine(SQLALCHEMY_DATABASE_URL, poolclass=NullPool)
    # Don't print the whole URL to avoid leaking passwords in logs
    print(f"DATABASE: Using PostgreSQL/Supabase ({HOST or 'remote'})")

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
