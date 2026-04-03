from __future__ import annotations
from sqlalchemy.orm import Session
from sqlalchemy import select, delete
from datetime import date, datetime

from app.data.models.patient_model import PatientModel


class PatientRepository:
    """Accès DB pour les patients"""

    def __init__(self, db: Session):
        self.db = db

    def create(self, nom: str, prenom: str, organisation_id: int, identifiant_interne: str,
               numero_securite_sociale: str | None = None, date_naissance: date | None = None,
               sexe: str | None = None, service: str | None = None, medecin_referent: str | None = None, 
               remarque: str | None = None, notes: str | None = None,
               service_id: int | None = None, medecin_referent_id: int | None = None) -> PatientModel:
        patient = PatientModel(
            nom=nom,
            prenom=prenom,
            organisation_id=organisation_id,
            identifiant_interne=identifiant_interne,
            numero_securite_sociale=numero_securite_sociale,
            date_naissance=date_naissance,
            sexe=sexe,
            service=service,
            medecin_referent=medecin_referent,
            remarque=remarque,
            notes=notes,
            service_id=service_id,
            medecin_referent_id=medecin_referent_id,
        )
        self.db.add(patient)
        self.db.commit()
        self.db.refresh(patient)
        return patient

    def get_by_id(self, patient_id: int) -> PatientModel | None:
        stmt = select(PatientModel).where(
            PatientModel.patient_id == patient_id, 
            PatientModel.deleted_at.is_(None)
        )
        return self.db.execute(stmt).scalar_one_or_none()

    def get_by_secu(self, numero_securite_sociale: str) -> PatientModel | None:
        stmt = select(PatientModel).where(
            PatientModel.numero_securite_sociale == numero_securite_sociale,
            PatientModel.deleted_at.is_(None)
        )
        return self.db.execute(stmt).scalar_one_or_none()

    def list(self, organisation_id: int | None = None, limit: int = 50, offset: int = 0) -> list[PatientModel]:
        stmt = select(PatientModel).where(PatientModel.deleted_at.is_(None))
        if organisation_id:
            stmt = stmt.where(PatientModel.organisation_id == organisation_id)
        stmt = stmt.order_by(PatientModel.patient_id.desc()).limit(limit).offset(offset)
        return self.db.execute(stmt).scalars().all()

    def list_services(self, organisation_id: int) -> list[str]:
        """Get distinct services from both string and FK references"""
        stmt = (
            select(PatientModel.service)
            .where(PatientModel.organisation_id == organisation_id)
            .where(PatientModel.deleted_at.is_(None))
            .where(PatientModel.service.isnot(None))
            .where(PatientModel.service != "")
            .distinct()
            .order_by(PatientModel.service)
        )
        rows = self.db.execute(stmt).scalars().all()
        return [r for r in rows if r]

    def list_medecins(self, organisation_id: int) -> list[str]:
        """Get distinct doctors from both string and FK references"""
        stmt = (
            select(PatientModel.medecin_referent)
            .where(PatientModel.organisation_id == organisation_id)
            .where(PatientModel.deleted_at.is_(None))
            .where(PatientModel.medecin_referent.isnot(None))
            .where(PatientModel.medecin_referent != "")
            .distinct()
            .order_by(PatientModel.medecin_referent)
        )
        rows = self.db.execute(stmt).scalars().all()
        return [r for r in rows if r]

    def update(self, patient_id: int, **fields) -> PatientModel | None:
        stmt = select(PatientModel).where(
            PatientModel.patient_id == patient_id,
            PatientModel.deleted_at.is_(None)
        )
        patient = self.db.execute(stmt).scalar_one_or_none()
        if not patient:
            return None
        
        # Only allow updating non-pk fields and preserve created_at
        protected_fields = ["patient_id", "created_at", "organisation_id", "identifiant_interne", "deleted_at"]
        for key, value in fields.items():
            if hasattr(patient, key) and key not in protected_fields:
                setattr(patient, key, value)
        self.db.commit()
        self.db.refresh(patient)
        return patient

    def soft_delete(self, patient_id: int) -> bool:
        """Soft delete a patient by setting deleted_at"""
        stmt = select(PatientModel).where(
            PatientModel.patient_id == patient_id,
            PatientModel.deleted_at.is_(None)
        )
        patient = self.db.execute(stmt).scalar_one_or_none()
        if not patient:
            return False
        
        patient.deleted_at = datetime.now()
        self.db.commit()
        return True

    def delete(self, patient_id: int) -> bool:
        """Hard delete (use soft_delete for soft deletes)"""
        stmt = delete(PatientModel).where(PatientModel.patient_id == patient_id)
        res = self.db.execute(stmt)
        self.db.commit()
        return (res.rowcount or 0) > 0
