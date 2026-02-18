from __future__ import annotations
from datetime import datetime
from sqlalchemy import String, Integer, ForeignKey, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from app.data.models.base import Base


class DeviceModel(Base):
    __tablename__ = "t_dispositif"

    device_id: Mapped[int] = mapped_column(primary_key=True)
    marque_modele: Mapped[str] = mapped_column(String(120), nullable=False)
    serial_number: Mapped[str | None] = mapped_column(String(120), nullable=True, unique=True)
    connection_type: Mapped[str] = mapped_column(String(30), nullable=False)
    etat: Mapped[str] = mapped_column(String(30), nullable=False)
    organisation_id: Mapped[int] = mapped_column(Integer, ForeignKey("t_organisation.organisation_id"), nullable=False)
    deleted_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        server_default=func.now(),
    )

    def __repr__(self):
        return f"<DeviceModel(device_id={self.device_id}, marque_modele={self.marque_modele}, serial={self.serial_number}, etat={self.etat})>"
