from __future__ import annotations
from datetime import datetime
from sqlalchemy import String, TIMESTAMP
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from app.data.models.base import Base


class OrganisationModel(Base):
    __tablename__ = "t_organisation"

    organisation_id: Mapped[int] = mapped_column(primary_key=True)
    nom: Mapped[str] = mapped_column(String(100), nullable=False)

    # colonne SQL "type" => attribut Python org_type
    org_type: Mapped[str] = mapped_column("type", String(50), nullable=False)

    adresse: Mapped[str | None] = mapped_column(String(255), nullable=True)

    deleted_at: Mapped[datetime | None] = mapped_column(TIMESTAMP(timezone=False), nullable=True)

    # ta table dit NOT NULL, mais sans default SQL.
    # On met server_default pour eviter les insert qui cassent si tu ne fournis pas created_at.
    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=False),
        nullable=False,
        server_default=func.now(),
    )

    # Relationships
    services: Mapped[list[ServiceModel]] = relationship("ServiceModel", back_populates="organisation", foreign_keys="ServiceModel.organisation_id")
    medecins: Mapped[list[MedecinModel]] = relationship("MedecinModel", back_populates="organisation", foreign_keys="MedecinModel.organisation_id")

import typing
if typing.TYPE_CHECKING:
    from app.data.models.service_model import ServiceModel
    from app.data.models.medecin_model import MedecinModel
