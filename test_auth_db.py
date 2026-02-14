import hashlib
import bcrypt

def verify_password(plain_password: str, hashed_password: str) -> bool:
    password_bytes = plain_password.encode("utf-8")
    password_hash = hashlib.sha256(password_bytes).hexdigest().encode("utf-8")
    return bcrypt.checkpw(password_hash, hashed_password.encode("utf-8"))

h = "$2b$12$UdjnxOROduZuhxi.P7f.CuH6CWzO22jnH8JNgrf4awm0ZBHLOSaU."
print(f"Verify hackathon_tester: {verify_password('test1234', h)}")
