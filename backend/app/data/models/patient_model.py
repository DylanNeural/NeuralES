from __future__ import annotations
from datetime import date, datetime
from sqlalchemy import String, TIMESTAMP, Integer, ForeignKey, Date
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from app.data.models.base import Base


class PatientModel(Base):
    __tablename__ = "t_patient"

    patient_id: Mapped[int] = mapped_column(primary_key=True)
    identifiant_interne: Mapped[str] = mapped_column(String(80), nullable=False)
    nom: Mapped[str] = mapped_column(String(100), nullable=False, default="")
    prenom: Mapped[str] = mapped_column(String(100), nullable=False, default="")
    date_naissance: Mapped[date | None] = mapped_column(Date, nullable=True)
    numero_securite_sociale: Mapped[str | None] = mapped_column(String(13), nullable=True, unique=True)
    sexe: Mapped[str | None] = mapped_column(String(10), nullable=True)
    
    # Service - can be referenced by FK or kept as string for flexibility
    service: Mapped[str | None] = mapped_column(String(100), nullable=True)
    service_id: Mapped[int | None] = mapped_column(Integer, ForeignKey("t_service.service_id", ondelete="SET NULL"), nullable=True)
    
    # Medecin referent - can be referenced by FK or kept as string for flexibility
    medecin_referent: Mapped[str | None] = mapped_column(String(100), nullable=True)
    medecin_referent_id: Mapped[int | None] = mapped_column(Integer, ForeignKey("t_medecin.medecin_id", ondelete="SET NULL"), nullable=True)
    
    remarque: Mapped[str | None] = mapped_column(String(500), nullable=True)
    notes: Mapped[str | None] = mapped_column(String(255), nullable=True)
    organisation_id: Mapped[int] = mapped_column(Integer, ForeignKey("t_organisation.organisation_id"), nullable=False)
    deleted_at: Mapped[datetime | None] = mapped_column(TIMESTAMP(timezone=False), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=False),
        nullable=False,
        server_default=func.now(),
    )

    # Relationships to reference tables
    service_ref: Mapped[ServiceModel | None] = relationship("ServiceModel", foreign_keys=[service_id], back_populates="patients")
    medecin_ref: Mapped[MedecinModel | None] = relationship("MedecinModel", foreign_keys=[medecin_referent_id], back_populates="patients")

import typing
if typing.TYPE_CHECKING:
    from app.data.models.service_model import ServiceModel
    from app.data.models.medecin_model import MedecinModel
