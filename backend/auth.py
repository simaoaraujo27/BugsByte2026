import os
import hashlib
import bcrypt
from datetime import datetime, timedelta, timezone
from typing import Annotated
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from sqlalchemy.orm import Session
import models, schemas
from database import get_db

# Configuration
SECRET_KEY = os.getenv("SECRET_KEY", "09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 43200 # 30 days
PASSWORD_RESET_EXPIRE_MINUTES = int(os.getenv("PASSWORD_RESET_EXPIRE_MINUTES", "30"))

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verifies a password against a hash using bcrypt directly.
    We still use SHA256 pre-hashing to ensure we never hit the 72-byte bcrypt limit.
    """
    try:
        password_bytes = plain_password.encode("utf-8")
        password_hash = hashlib.sha256(password_bytes).hexdigest().encode("utf-8")
        return bcrypt.checkpw(password_hash, hashed_password.encode("utf-8"))
    except Exception:
        return False

def get_password_hash(password: str) -> str:
    """
    Hashes a password using bcrypt directly.
    """
    password_bytes = password.encode("utf-8")
    # SHA256 pre-hash to avoid bcrypt 72-character limit
    password_hash = hashlib.sha256(password_bytes).hexdigest().encode("utf-8")
    
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password_hash, salt)
    return hashed.decode("utf-8")

def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def create_password_reset_token(username: str) -> str:
    expire = datetime.now(timezone.utc) + timedelta(minutes=PASSWORD_RESET_EXPIRE_MINUTES)
    payload = {"sub": username, "scope": "password_reset", "exp": expire}
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)

def verify_password_reset_token(token: str) -> str | None:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        if payload.get("scope") != "password_reset":
            return None
        username = payload.get("sub")
        if not username:
            return None
        return username
    except JWTError:
        return None

async def get_current_user(token: Annotated[str, Depends(oauth2_scheme)], db: Session = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            print("DEBUG AUTH: Token payload missing 'sub'")
            raise credentials_exception
        token_data = schemas.TokenData(username=username)
    except JWTError as e:
        print(f"DEBUG AUTH: JWT Decode Error: {e}")
        raise credentials_exception
    except Exception as e:
        print(f"DEBUG AUTH: Unexpected Auth Error: {e}")
        raise credentials_exception
        
    user = db.query(models.User).filter(models.User.username == token_data.username).first()
    if user is None:
        print(f"DEBUG AUTH: User '{token_data.username}' not found in database")
        raise credentials_exception
    return user
