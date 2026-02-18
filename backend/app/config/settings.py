import os  # Read environment variables.
from pydantic_settings import BaseSettings  # Settings base class.


class Settings(BaseSettings):
    """Configuration centralisee de l'application."""
    
    # App
    app_name: str = "NeuralES API"  # Human-readable app name.
    app_version: str = "0.1.0"  # App version string.
    debug: bool = os.getenv("DEBUG", "False").lower() == "true"  # Toggle debug mode.
    
    # Database
    database_url: str = os.getenv(
        "DATABASE_URL",
        "postgresql+psycopg2://neurales_user:jp8GJIrdC7L7S55N@localhost:5432/neurales"
    )  # SQLAlchemy database DSN.
    database_echo: bool = False  # Log SQL statements if True.

    # Auth (basic admin user + JWT)
    auth_secret_key: str = os.getenv("AUTH_SECRET_KEY", "dev-secret-change-me")  # JWT signing key.
    auth_algorithm: str = os.getenv("AUTH_ALGORITHM", "HS256")  # JWT signing algorithm.
    auth_access_token_expire_minutes: int = int(os.getenv("AUTH_ACCESS_TOKEN_EXPIRE_MINUTES", "120"))  # Access token TTL.
    auth_refresh_token_expire_days: int = int(os.getenv("AUTH_REFRESH_TOKEN_EXPIRE_DAYS", "7"))  # Refresh token TTL.
    auth_issuer: str = os.getenv("AUTH_ISSUER", "neurales-api")  # JWT issuer claim.
    auth_audience: str = os.getenv("AUTH_AUDIENCE", "neurales-client")  # JWT audience claim.
    auth_refresh_cookie_name: str = os.getenv("AUTH_REFRESH_COOKIE_NAME", "refresh_token")  # Cookie name.
    auth_cookie_secure: bool = os.getenv("AUTH_COOKIE_SECURE", "False").lower() == "true"  # HTTPS-only cookie. **SET TO TRUE IN PROD**.
    auth_cookie_samesite: str = os.getenv("AUTH_COOKIE_SAMESITE", "lax")  # Cookie SameSite policy.

    cors_origins: str = os.getenv("CORS_ORIGINS", "http://localhost:5173")  # Allowed CORS origins.

    admin_email: str = os.getenv("ADMIN_EMAIL", "admin@neurales.com")  # Default admin email.
    admin_password: str = os.getenv("ADMIN_PASSWORD", "admin123")  # Default admin password.
    admin_password_hash: str = os.getenv("ADMIN_PASSWORD_HASH", "")  # Pre-hashed admin password.
    admin_first_name: str = os.getenv("ADMIN_FIRST_NAME", "Admin")  # Default admin first name.
    admin_last_name: str = os.getenv("ADMIN_LAST_NAME", "NeuralES")  # Default admin last name.
    admin_role: str = os.getenv("ADMIN_ROLE", "admin")  # Default admin role.
    admin_user_id: int = int(os.getenv("ADMIN_USER_ID", "1"))  # Default admin user id.
    
    # EEG
    chunk_seconds: float = 0.05  # 50ms chunks.
    fatigue_window_seconds: float = 10.0  # 10s sliding window.
    default_picks: list[str] = ["Fpz-Cz", "Pz-Oz"]  # Default channels.
    
    # EEG Fatigue Scoring
    theta_min: float = 4.0  # Theta band min.
    theta_max: float = 8.0  # Theta band max.
    alpha_min: float = 8.0  # Alpha band min.
    alpha_max: float = 12.0  # Alpha band max.
    fatigue_ratio_min: float = 0.5  # Min fatigue ratio.
    fatigue_ratio_max: float = 3.0  # Max fatigue ratio.
    
    class Config:
        env_file = ".env"  # Load env vars from .env if present.
        case_sensitive = False  # Env keys are case-insensitive.


settings = Settings()  # Instantiate settings singleton.
