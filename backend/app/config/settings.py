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
