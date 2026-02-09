from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session

from app.config import settings

engine = create_engine(
    settings.database_url,
    pool_pre_ping=True,
    echo=settings.database_echo,
)

SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)


def get_db() -> Session:
    """Dépendance FastAPI pour injecter une session DB"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

