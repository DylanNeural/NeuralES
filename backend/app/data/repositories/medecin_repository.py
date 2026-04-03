from __future__ import annotations
from sqlalchemy.orm import Session
from sqlalchemy import select

from app.data.models.medecin_model import MedecinModel


class MedecinRepository:
    """Access DB for doctors (reference data)"""

    def __init__(self, db: Session):
        self.db = db

    def list_by_organisation(self, organisation_id: int) -> list[MedecinModel]:
        """List all doctors for an organisation (excluding deleted)"""
        stmt = (
            select(MedecinModel)
            .where(MedecinModel.organisation_id == organisation_id)
            .where(MedecinModel.deleted_at.is_(None))
            .order_by(MedecinModel.nom)
        )
        return self.db.execute(stmt).scalars().all()

    def get_by_id(self, medecin_id: int) -> MedecinModel | None:
        """Get doctor by ID"""
        stmt = (
            select(MedecinModel)
            .where(MedecinModel.medecin_id == medecin_id)
            .where(MedecinModel.deleted_at.is_(None))
        )
        return self.db.execute(stmt).scalar_one_or_none()

    def create(self, nom: str, organisation_id: int) -> MedecinModel:
        """Create a new doctor"""
        medecin = MedecinModel(nom=nom, organisation_id=organisation_id)
        self.db.add(medecin)
        self.db.commit()
        self.db.refresh(medecin)
        return medecin

    def soft_delete(self, medecin_id: int) -> bool:
        """Soft delete a doctor by setting deleted_at"""
        medecin = self.get_by_id(medecin_id)
        if not medecin:
            return False
        
        medecin.deleted_at = __import__('datetime').datetime.now()
        self.db.commit()
        return True
