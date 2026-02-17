from sqlalchemy.orm import Session
from sqlalchemy import select, delete

from app.data.models.patient_model import PatientModel


class PatientRepository:
    """Accès DB pour les patients"""

    def __init__(self, db: Session):
        self.db = db

    def create(self, nom: str, prenom: str, date_naissance: str, numero_securite_sociale: str, 
               sexe: str, service: str | None = None, medecin_referent: str | None = None, 
               remarque: str | None = None) -> PatientModel:
        patient = PatientModel(
            nom=nom,
            prenom=prenom,
            date_naissance=date_naissance,
            numero_securite_sociale=numero_securite_sociale,
            sexe=sexe,
            service=service,
            medecin_referent=medecin_referent,
            remarque=remarque,
        )
        self.db.add(patient)
        self.db.commit()
        self.db.refresh(patient)
        return patient

    def get_by_id(self, patient_id: int) -> PatientModel | None:
        return self.db.get(PatientModel, patient_id)

    def get_by_secu(self, numero_securite_sociale: str) -> PatientModel | None:
        stmt = select(PatientModel).where(PatientModel.numero_securite_sociale == numero_securite_sociale)
        return self.db.execute(stmt).scalar_one_or_none()

    def list(self, limit: int = 50, offset: int = 0) -> list[PatientModel]:
        stmt = (
            select(PatientModel)
            .order_by(PatientModel.patient_id.desc())
            .limit(limit)
            .offset(offset)
        )
        return self.db.execute(stmt).scalars().all()

    def update(self, patient_id: int, **fields) -> PatientModel | None:
        patient = self.get_by_id(patient_id)
        if not patient:
            return None
        for key, value in fields.items():
            if hasattr(patient, key) and key not in ["patient_id", "created_at"]:
                setattr(patient, key, value)
        self.db.commit()
        self.db.refresh(patient)
        return patient

    def delete(self, patient_id: int) -> bool:
        stmt = delete(PatientModel).where(PatientModel.patient_id == patient_id)
        res = self.db.execute(stmt)
        self.db.commit()
        return (res.rowcount or 0) > 0
