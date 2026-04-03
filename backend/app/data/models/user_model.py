from datetime import datetime
from sqlalchemy import String, TIMESTAMP, Integer, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import func

from app.data.models.base import Base


class UserModel(Base):
    __tablename__ = "t_utilisateur"

    user_id: Mapped[int] = mapped_column(primary_key=True)
    nom: Mapped[str] = mapped_column(String(80), nullable=False)
    prenom: Mapped[str] = mapped_column(String(80), nullable=False)
    email: Mapped[str] = mapped_column(String(150), nullable=False, unique=True)
    etat_compte: Mapped[str] = mapped_column(String(20), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=False),
        nullable=False,
        server_default=func.now(),
    )
    last_login_at: Mapped[datetime | None] = mapped_column(TIMESTAMP(timezone=False), nullable=True)
    organisation_id: Mapped[int] = mapped_column(Integer, ForeignKey("t_organisation.organisation_id"), nullable=False)

    # Ajoute dans la BDD via migration: ALTER TABLE t_utilisateur ADD COLUMN password_hash VARCHAR(255);
    password_hash: Mapped[str | None] = mapped_column(String(255), nullable=True)
