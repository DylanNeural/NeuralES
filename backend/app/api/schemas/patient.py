from datetime import date, datetime
from pydantic import BaseModel, Field


class PatientCreateRequest(BaseModel):
    """Schéma pour créer un patient"""
    identifiant_interne: str = Field(min_length=1, max_length=80)
    nom: str = Field(min_length=1, max_length=100)
    prenom: str = Field(min_length=1, max_length=100)
    date_naissance: date | None = None
    numero_securite_sociale: str | None = Field(default=None, min_length=13, max_length=13, pattern=r"^\d{13}$")
    sexe: str | None = Field(default=None, pattern=r"^(homme|femme)$")
    service: str | None = Field(default=None, max_length=100)
    medecin_referent: str | None = Field(default=None, max_length=100)
    remarque: str | None = Field(default=None, max_length=500)
    notes: str | None = Field(default=None, max_length=255)


class PatientUpdateRequest(BaseModel):
    """Schéma pour mettre à jour un patient"""
    nom: str | None = Field(default=None, min_length=1, max_length=100)
    prenom: str | None = Field(default=None, min_length=1, max_length=100)
    date_naissance: date | None = None
    numero_securite_sociale: str | None = Field(default=None, min_length=13, max_length=13, pattern=r"^\d{13}$")
    sexe: str | None = Field(default=None, pattern=r"^(homme|femme)$")
    service: str | None = Field(default=None, max_length=100)
    medecin_referent: str | None = Field(default=None, max_length=100)
    remarque: str | None = Field(default=None, max_length=500)
    notes: str | None = Field(default=None, max_length=255)


class PatientResponse(BaseModel):
    """Schéma de réponse pour un patient"""
    patient_id: int
    organisation_id: int
    identifiant_interne: str
    nom: str
    prenom: str
    date_naissance: date | None
    numero_securite_sociale: str | None
    sexe: str | None
    service: str | None
    medecin_referent: str | None
    remarque: str | None
    notes: str | None
    created_at: datetime

    class Config:
        from_attributes = True


class PatientListResponse(BaseModel):
    """Schéma simplifié pour liste de patients"""
    patient_id: int
    organisation_id: int
    identifiant_interne: str
    nom: str
    prenom: str
    date_naissance: date | None
    numero_securite_sociale: str | None

    class Config:
        from_attributes = True
