from datetime import datetime, timedelta, timezone
from typing import Optional
import base64
import hashlib
import hmac
import secrets

from fastapi import APIRouter, Depends, HTTPException, Request, Response, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError, jwt
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.config import settings
from app.data.db import get_db
from app.data.repositories.user_repository import UserRepository

router = APIRouter(prefix="/auth", tags=["auth"])
security = HTTPBearer(auto_error=False)


class LoginIn(BaseModel):
    email: str
    password: str


class TokenOut(BaseModel):
    access_token: str
    token_type: str = "bearer"


class UserOut(BaseModel):
    user_id: int
    prenom: str
    nom: str
    email: str
    organisation_id: int
    role: Optional[str] = None


def _b64encode(raw: bytes) -> str:
    return base64.urlsafe_b64encode(raw).decode("utf-8")


def _b64decode(raw: str) -> bytes:
    return base64.urlsafe_b64decode(raw.encode("utf-8"))


def hash_password(password: str, iterations: int = 260000) -> str:
    salt = secrets.token_bytes(16)
    dk = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, iterations)
    return f"pbkdf2_sha256${iterations}${_b64encode(salt)}${_b64encode(dk)}"


def verify_password(password: str, password_hash: str) -> bool:
    try:
        scheme, iter_s, salt_b64, hash_b64 = password_hash.split("$", 3)
        if scheme != "pbkdf2_sha256":
            return False
        iterations = int(iter_s)
        salt = _b64decode(salt_b64)
        expected = _b64decode(hash_b64)
    except Exception:
        return False

    dk = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, iterations)
    return hmac.compare_digest(dk, expected)


def create_access_token(payload: dict) -> str:
    expires = datetime.now(timezone.utc) + timedelta(minutes=settings.auth_access_token_expire_minutes)
    to_encode = {**payload, "exp": expires}
    return jwt.encode(to_encode, settings.auth_secret_key, algorithm=settings.auth_algorithm)


def create_refresh_token(payload: dict) -> str:
    expires = datetime.now(timezone.utc) + timedelta(days=settings.auth_refresh_token_expire_days)
    to_encode = {**payload, "exp": expires, "type": "refresh"}
    return jwt.encode(to_encode, settings.auth_secret_key, algorithm=settings.auth_algorithm)


def decode_token(token: str) -> dict:
    return jwt.decode(token, settings.auth_secret_key, algorithms=[settings.auth_algorithm])


def set_refresh_cookie(response: Response, token: str) -> None:
    max_age = settings.auth_refresh_token_expire_days * 24 * 60 * 60
    response.set_cookie(
        key=settings.auth_refresh_cookie_name,
        value=token,
        httponly=True,
        secure=settings.auth_cookie_secure,
        samesite=settings.auth_cookie_samesite,
        max_age=max_age,
        path="/",
    )


def clear_refresh_cookie(response: Response) -> None:
    response.delete_cookie(
        key=settings.auth_refresh_cookie_name,
        path="/",
    )


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db),
) -> dict:
    if not credentials or not credentials.credentials:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Missing token")
    try:
        payload = decode_token(credentials.credentials)
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")

    user_id = payload.get("user_id")
    if not user_id:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid user")

    repo = UserRepository(db)
    user = repo.get_by_id(user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid user")

    return {
        "user_id": user.user_id,
        "prenom": user.prenom,
        "nom": user.nom,
        "email": user.email,
        "organisation_id": user.organisation_id,
        "role": None,
    }


@router.post("/login", response_model=TokenOut)
def login(payload: LoginIn, response: Response, db: Session = Depends(get_db)):
    repo = UserRepository(db)
    user = repo.get_by_email(payload.email)
    if not user or not user.password_hash:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
    if not verify_password(payload.password, user.password_hash):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")

    access_token = create_access_token({
        "sub": user.email,
        "user_id": user.user_id,
    })
    refresh_token = create_refresh_token({
        "sub": user.email,
        "user_id": user.user_id,
    })
    set_refresh_cookie(response, refresh_token)
    repo.update_last_login(user)
    return TokenOut(access_token=access_token)


@router.post("/refresh", response_model=TokenOut)
def refresh(request: Request, response: Response, db: Session = Depends(get_db)):
    raw_token = request.cookies.get(settings.auth_refresh_cookie_name)
    if not raw_token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Missing refresh token")
    try:
        payload = decode_token(raw_token)
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token")

    if payload.get("type") != "refresh":
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token")

    user_id = payload.get("user_id")
    if not user_id:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid user")

    repo = UserRepository(db)
    user = repo.get_by_id(user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid user")

    access_token = create_access_token({
        "sub": user.email,
        "user_id": user.user_id,
    })
    refresh_token = create_refresh_token({
        "sub": user.email,
        "user_id": user.user_id,
    })
    set_refresh_cookie(response, refresh_token)
    return TokenOut(access_token=access_token)


@router.post("/logout")
def logout(response: Response):
    clear_refresh_cookie(response)
    return {"ok": True}


@router.get("/me", response_model=UserOut)
def me(current_user: dict = Depends(get_current_user)):
    return current_user
