import os
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

load_dotenv()

# Prioridade 1: Credenciais explícitas do Supabase
# Aceita variáveis antigas em minúsculas e novas em maiúsculas.
USER = os.getenv("DB_USER") or os.getenv("user")
PASSWORD = os.getenv("DB_PASSWORD") or os.getenv("password")
HOST = os.getenv("DB_HOST") or os.getenv("host")
DB_PORT = os.getenv("DB_PORT") or os.getenv("port")
DBNAME = os.getenv("DB_NAME") or os.getenv("dbname")

if USER and PASSWORD and HOST:
    SQLALCHEMY_DATABASE_URL = (
        f"postgresql+psycopg2://{USER}:{PASSWORD}@{HOST}:{DB_PORT or '5432'}/{DBNAME or 'postgres'}?sslmode=require"
    )
else:
    # Prioridade 2: DATABASE_URL (com conversão para postgresql:// se necessário)
    url = os.getenv("DATABASE_URL", "sqlite:///./sql_app.db")
    if url.startswith("postgres://"):
        url = url.replace("postgres://", "postgresql://", 1)
    # Em produção (Render/Supabase), garantir SSL se vier URL sem querystring.
    if url.startswith("postgresql") and "sslmode=" not in url:
        sep = "&" if "?" in url else "?"
        url = f"{url}{sep}sslmode=require"
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
    engine = create_engine(
        SQLALCHEMY_DATABASE_URL,
        poolclass=NullPool,
        pool_pre_ping=True,
        pool_recycle=300,
        connect_args={"connect_timeout": 10},
    )
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
