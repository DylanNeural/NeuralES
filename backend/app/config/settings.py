import os
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Configuration centralisée de l'application"""
    
    # App
    app_name: str = "NeuralES API"
    app_version: str = "0.1.0"
    debug: bool = os.getenv("DEBUG", "False").lower() == "true"
    
    # Database
    database_url: str = os.getenv(
        "DATABASE_URL",
        "postgresql+psycopg2://user:pass@localhost:5432/neurales"
    )
    database_echo: bool = False

    # Auth (basic admin user + JWT)
    auth_secret_key: str = os.getenv("AUTH_SECRET_KEY", "dev-secret-change-me")
    auth_algorithm: str = os.getenv("AUTH_ALGORITHM", "HS256")
    auth_access_token_expire_minutes: int = int(os.getenv("AUTH_ACCESS_TOKEN_EXPIRE_MINUTES", "120"))
    auth_refresh_token_expire_days: int = int(os.getenv("AUTH_REFRESH_TOKEN_EXPIRE_DAYS", "7"))
    auth_refresh_cookie_name: str = os.getenv("AUTH_REFRESH_COOKIE_NAME", "refresh_token")
    auth_cookie_secure: bool = os.getenv("AUTH_COOKIE_SECURE", "False").lower() == "true"
    auth_cookie_samesite: str = os.getenv("AUTH_COOKIE_SAMESITE", "lax")

    cors_origins: str = os.getenv("CORS_ORIGINS", "http://localhost:5173")

    admin_email: str = os.getenv("ADMIN_EMAIL", "admin@neurales.com")
    admin_password: str = os.getenv("ADMIN_PASSWORD", "admin123")
    admin_password_hash: str = os.getenv("ADMIN_PASSWORD_HASH", "")
    admin_first_name: str = os.getenv("ADMIN_FIRST_NAME", "Admin")
    admin_last_name: str = os.getenv("ADMIN_LAST_NAME", "NeuralES")
    admin_role: str = os.getenv("ADMIN_ROLE", "admin")
    admin_user_id: int = int(os.getenv("ADMIN_USER_ID", "1"))
    
    # EEG
    chunk_seconds: float = 0.05  # 50ms chunks
    fatigue_window_seconds: float = 10.0  # 10s sliding window
    default_picks: list[str] = ["Fpz-Cz", "Pz-Oz"]
    
    # EEG Fatigue Scoring
    theta_min: float = 4.0
    theta_max: float = 8.0
    alpha_min: float = 8.0
    alpha_max: float = 12.0
    fatigue_ratio_min: float = 0.5
    fatigue_ratio_max: float = 3.0
    
    class Config:
        env_file = ".env"
        case_sensitive = False


settings = Settings()
