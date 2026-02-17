from datetime import datetime
from sqlalchemy import String, TIMESTAMP
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import func

from app.data.models.base import Base


class OrganisationModel(Base):
    __tablename__ = "organisation"

    organisation_id: Mapped[int] = mapped_column(primary_key=True)
    nom: Mapped[str] = mapped_column(String(100), nullable=False)

    # colonne SQL "type" => attribut Python org_type
    org_type: Mapped[str] = mapped_column("type", String(50), nullable=False)

    adresse: Mapped[str | None] = mapped_column(String(255), nullable=True)

    # ta table dit NOT NULL, mais sans default SQL.
    # On met server_default pour eviter les insert qui cassent si tu ne fournis pas created_at.
    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=False),
        nullable=False,
        server_default=func.now(),
    )
