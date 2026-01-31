from datetime import datetime, timedelta
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError, jwt
from passlib.context import CryptContext
from pydantic import BaseModel

# Configuration JWT
SECRET_KEY = "your-secret-key-change-this-in-production"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# Contexte de hashage des mots de passe
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Schémas Pydantic
class User(BaseModel):
    user_id: int
    email: str
    prenom: str
    nom: str
    role: Optional[str] = None

class UserInDB(User):
    password: str

class LoginRequest(BaseModel):
    email: str
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str

# Base de données utilisateurs en mémoire (à remplacer par une vraie BDD)
fake_users_db = {
    "admin@neurales.com": {
        "user_id": 1,
        "email": "admin@neurales.com",
        "prenom": "Admin",
        "nom": "NeuralES",
        "role": "admin",
        "password": "admin123"  # Mot de passe en clair pour le développement
    },
    "user@neurales.com": {
        "user_id": 2,
        "email": "user@neurales.com",
        "prenom": "Jean",
        "nom": "Dupont",
        "role": "user",
        "password": "user123"  # Mot de passe en clair pour le développement
    }
}

# Utilitaires
def verify_password(plain_password: str, stored_password: str) -> bool:
    return plain_password == stored_password

def get_user(email: str) -> Optional[UserInDB]:
    if email in fake_users_db:
        user_dict = fake_users_db[email]
        return UserInDB(**user_dict)
    return None

def authenticate_user(email: str, password: str) -> Optional[User]:
    user = get_user(email)
    if not user:
        return None
    if not verify_password(password, user.password):
        return None
    return User(user_id=user.user_id, email=user.email, prenom=user.prenom, nom=user.nom, role=user.role)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

# Sécurité
security = HTTPBearer()

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(credentials.credentials, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    user = get_user(email)
    if user is None:
        raise credentials_exception
    return User(user_id=user.user_id, email=user.email, prenom=user.prenom, nom=user.nom, role=user.role)

# Router
router = APIRouter(prefix="/auth", tags=["Authentication"])

@router.post("/login", response_model=Token)
async def login(login_data: LoginRequest):
    user = authenticate_user(login_data.email, login_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.email}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

@router.get("/me", response_model=User)
async def read_users_me(current_user: User = Depends(get_current_user)):
    return current_user