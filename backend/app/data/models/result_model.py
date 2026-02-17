from datetime import datetime
from sqlalchemy import String, TIMESTAMP, Integer, Float, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import func

from app.data.models.base import Base


class ResultModel(Base):
    __tablename__ = "result"

    result_id: Mapped[int] = mapped_column(primary_key=True)
    session_id: Mapped[str] = mapped_column(String(100), nullable=False, unique=True)
    patient_id: Mapped[int] = mapped_column(Integer, ForeignKey("patient.patient_id"), nullable=False)
    acquisition_date: Mapped[datetime] = mapped_column(TIMESTAMP(timezone=False), nullable=False)
    fatigue_score: Mapped[float] = mapped_column(Float, nullable=False)  # 0-100
    quality: Mapped[str] = mapped_column(String(50), nullable=False)  # "Good", "Fair", "Poor"
    notes: Mapped[str | None] = mapped_column(String(500), nullable=True)
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
