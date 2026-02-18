import base64
import hashlib
import secrets
import sys


def _b64encode(raw: bytes) -> str:
    return base64.urlsafe_b64encode(raw).decode("utf-8")


def hash_password(password: str, iterations: int = 260000) -> str:
    salt = secrets.token_bytes(16)
    dk = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, iterations)
    return f"pbkdf2_sha256${iterations}${_b64encode(salt)}${_b64encode(dk)}"


if len(sys.argv) < 2:
    raise SystemExit("Usage: python generate_password_hash.py <password>")

print(hash_password(sys.argv[1]))
