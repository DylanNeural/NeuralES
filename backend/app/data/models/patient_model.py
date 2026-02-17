from datetime import datetime
from sqlalchemy import String, TIMESTAMP, Integer
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import func

from app.data.models.base import Base


class PatientModel(Base):
    __tablename__ = "patient"

    patient_id: Mapped[int] = mapped_column(primary_key=True)
    nom: Mapped[str] = mapped_column(String(100), nullable=False)
    prenom: Mapped[str] = mapped_column(String(100), nullable=False)
    date_naissance: Mapped[str] = mapped_column(String(10), nullable=False)  # YYYY-MM-DD
    numero_securite_sociale: Mapped[str] = mapped_column(String(13), nullable=False, unique=True)
    sexe: Mapped[str] = mapped_column(String(10), nullable=False)  # "homme" ou "femme"
    service: Mapped[str | None] = mapped_column(String(100), nullable=True)
    medecin_referent: Mapped[str | None] = mapped_column(String(100), nullable=True)
    remarque: Mapped[str | None] = mapped_column(String(500), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=False),
        nullable=False,
        server_default=func.now(),
    )
    updated_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=False),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
    )
