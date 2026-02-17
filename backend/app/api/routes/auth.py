from datetime import datetime, timedelta, timezone
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Request, Response, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError, jwt
from passlib.context import CryptContext
from pydantic import BaseModel

from app.config import settings

router = APIRouter(prefix="/auth", tags=["auth"])
security = HTTPBearer(auto_error=False)

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


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
    role: Optional[str] = None


def build_admin_user():
    return {
        "user_id": settings.admin_user_id,
        "prenom": settings.admin_first_name,
        "nom": settings.admin_last_name,
        "email": settings.admin_email,
        "role": settings.admin_role,
    }


def verify_admin_password(password: str) -> bool:
    if settings.admin_password_hash:
        return pwd_context.verify(password, settings.admin_password_hash)
    return password == settings.admin_password


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


def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> dict:
    if not credentials or not credentials.credentials:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Missing token")
    try:
        payload = decode_token(credentials.credentials)
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")

    subject = payload.get("sub")
    if subject != settings.admin_email:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid user")

    return build_admin_user()


@router.post("/login", response_model=TokenOut)
def login(payload: LoginIn, response: Response):
    if payload.email != settings.admin_email or not verify_admin_password(payload.password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")

    user = build_admin_user()
    access_token = create_access_token({
        "sub": user["email"],
        "user_id": user["user_id"],
        "role": user.get("role"),
    })
    refresh_token = create_refresh_token({
        "sub": user["email"],
        "user_id": user["user_id"],
        "role": user.get("role"),
    })
    set_refresh_cookie(response, refresh_token)
    return TokenOut(access_token=access_token)


@router.post("/refresh", response_model=TokenOut)
def refresh(request: Request, response: Response):
    raw_token = request.cookies.get(settings.auth_refresh_cookie_name)
    if not raw_token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Missing refresh token")
    try:
        payload = decode_token(raw_token)
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token")

    if payload.get("type") != "refresh":
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token")

    subject = payload.get("sub")
    if subject != settings.admin_email:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid user")

    user = build_admin_user()
    access_token = create_access_token({
        "sub": user["email"],
        "user_id": user["user_id"],
        "role": user.get("role"),
    })
    refresh_token = create_refresh_token({
        "sub": user["email"],
        "user_id": user["user_id"],
        "role": user.get("role"),
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
