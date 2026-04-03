from datetime import datetime
from sqlalchemy import String, TIMESTAMP, Integer, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import func

from app.data.models.base import Base


class SessionModel(Base):
    """Maps to t_session_mesure table - measurement sessions for EEG acquisition"""
    __tablename__ = "t_session_mesure"

    session_id: Mapped[int] = mapped_column(primary_key=True)
    mode: Mapped[str] = mapped_column(String(20), nullable=False)  # acquisition mode
    started_at: Mapped[datetime] = mapped_column(TIMESTAMP(timezone=False), nullable=False, server_default=func.now())
    ended_at: Mapped[datetime | None] = mapped_column(TIMESTAMP(timezone=False), nullable=True)
    notes: Mapped[str | None] = mapped_column(String(255), nullable=True)
    app_version: Mapped[str | None] = mapped_column(String(50), nullable=True)
    
    # Foreign keys
    device_id: Mapped[int | None] = mapped_column(Integer, ForeignKey("t_dispositif.device_id"), nullable=True)
    consent_id: Mapped[int | None] = mapped_column(Integer, ForeignKey("t_consentement.consent_id"), nullable=True)
    patient_id: Mapped[int | None] = mapped_column(Integer, ForeignKey("t_patient.patient_id"), nullable=True)
    created_by_user_id: Mapped[int] = mapped_column(Integer, ForeignKey("t_utilisateur.user_id"), nullable=False)
    organisation_id: Mapped[int] = mapped_column(Integer, ForeignKey("t_organisation.organisation_id"), nullable=False)
