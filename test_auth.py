import hashlib
import bcrypt

def get_password_hash(password: str) -> str:
    password_bytes = password.encode("utf-8")
    password_hash = hashlib.sha256(password_bytes).hexdigest().encode("utf-8")
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password_hash, salt)
    return hashed.decode("utf-8")

def verify_password(plain_password: str, hashed_password: str) -> bool:
    password_bytes = plain_password.encode("utf-8")
    password_hash = hashlib.sha256(password_bytes).hexdigest().encode("utf-8")
    return bcrypt.checkpw(password_hash, hashed_password.encode("utf-8"))

password = "test1234"
h = get_password_hash(password)
print(f"Hash: {h}")
v = verify_password(password, h)
print(f"Verify: {v}")
