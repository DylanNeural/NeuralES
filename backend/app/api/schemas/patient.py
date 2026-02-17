from datetime import datetime
from pydantic import BaseModel, Field


class PatientCreateRequest(BaseModel):
    """Schéma pour créer un patient"""
    nom: str = Field(min_length=1, max_length=100)
    prenom: str = Field(min_length=1, max_length=100)
    date_naissance: str = Field(pattern=r"^\d{4}-\d{2}-\d{2}$")  # YYYY-MM-DD
    numero_securite_sociale: str = Field(min_length=13, max_length=13, pattern=r"^\d{13}$")
    sexe: str = Field(pattern=r"^(homme|femme)$")
    service: str | None = Field(default=None, max_length=100)
    medecin_referent: str | None = Field(default=None, max_length=100)
    remarque: str | None = Field(default=None, max_length=500)


class PatientUpdateRequest(BaseModel):
    """Schéma pour mettre à jour un patient"""
    nom: str | None = Field(default=None, min_length=1, max_length=100)
    prenom: str | None = Field(default=None, min_length=1, max_length=100)
    service: str | None = Field(default=None, max_length=100)
    medecin_referent: str | None = Field(default=None, max_length=100)
    remarque: str | None = Field(default=None, max_length=500)


class PatientResponse(BaseModel):
    """Schéma de réponse pour un patient"""
    patient_id: int
    nom: str
    prenom: str
    date_naissance: str
    numero_securite_sociale: str
    sexe: str
    service: str | None
    medecin_referent: str | None
    remarque: str | None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class PatientListResponse(BaseModel):
    """Schéma simplifié pour liste de patients"""
    patient_id: int
    nom: str
    prenom: str
    date_naissance: str
    numero_securite_sociale: str

    class Config:
        from_attributes = True
