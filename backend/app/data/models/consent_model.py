from __future__ import annotations

from datetime import datetime
from sqlalchemy import String, Integer, ForeignKey, TIMESTAMP
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import func

from app.data.models.base import Base


class ConsentModel(Base):
    __tablename__ = "t_consentement"

    consent_id: Mapped[int] = mapped_column(primary_key=True)
    scope: Mapped[str] = mapped_column(String(50), nullable=False)
    status: Mapped[str] = mapped_column(String(20), nullable=False)
    consent_at: Mapped[datetime] = mapped_column(TIMESTAMP(timezone=False), nullable=False, server_default=func.now())
    expires_at: Mapped[datetime | None] = mapped_column(TIMESTAMP(timezone=False), nullable=True)
    withdrawn_at: Mapped[datetime | None] = mapped_column(TIMESTAMP(timezone=False), nullable=True)
    collected_by_user_id: Mapped[int] = mapped_column(Integer, ForeignKey("t_utilisateur.user_id"), nullable=False)
    patient_id: Mapped[int] = mapped_column(Integer, ForeignKey("t_patient.patient_id"), nullable=False)
