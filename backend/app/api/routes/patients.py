from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.data.db import get_db
from app.data.repositories.patient_repository import PatientRepository
from app.data.repositories.service_repository import ServiceRepository
from app.data.repositories.medecin_repository import MedecinRepository
from app.api.routes.auth import get_current_user

from app.api.schemas.patient import (
    PatientCreateRequest,
    PatientUpdateRequest,
    PatientResponse,
    PatientListResponse,
)

router = APIRouter(prefix="/patients", tags=["patients"])


def get_repo(db: Session = Depends(get_db)) -> PatientRepository:
    return PatientRepository(db)


@router.post("", response_model=PatientResponse, status_code=201)
def create_patient(
    payload: PatientCreateRequest,
    repo=Depends(get_repo),
    current_user: dict = Depends(get_current_user),
):
    """Créer un nouveau patient"""
    # Check if patient already exists by SSN
    if payload.numero_securite_sociale:
        existing = repo.get_by_secu(payload.numero_securite_sociale)
        if existing:
            raise HTTPException(status_code=409, detail="Patient with this SSN already exists")
    
    patient = repo.create(
        organisation_id=current_user["organisation_id"],
        identifiant_interne=payload.identifiant_interne,
        nom=payload.nom,
        prenom=payload.prenom,
        date_naissance=payload.date_naissance,
        numero_securite_sociale=payload.numero_securite_sociale,
        sexe=payload.sexe,
        service=payload.service,
        medecin_referent=payload.medecin_referent,
        remarque=payload.remarque,
        notes=payload.notes,
    )
    return PatientResponse.model_validate(patient)


@router.get("/meta/services", response_model=list[str])
def list_services(
    repo=Depends(get_repo),
    current_user: dict = Depends(get_current_user),
):
    """Lister les services existants pour l'organisation"""
    return repo.list_services(current_user["organisation_id"])


@router.get("/meta/medecins", response_model=list[str])
def list_medecins(
    repo=Depends(get_repo),
    current_user: dict = Depends(get_current_user),
):
    """Lister les medecins referents existants pour l'organisation"""
    return repo.list_medecins(current_user["organisation_id"])


@router.get("/{patient_id}", response_model=PatientResponse)
def get_patient(
    patient_id: int,
    repo=Depends(get_repo),
    current_user: dict = Depends(get_current_user),
):
    """Récupérer un patient par ID"""
    patient = repo.get_by_id(patient_id)
    if not patient or patient.organisation_id != current_user["organisation_id"]:
        raise HTTPException(status_code=404, detail="Patient not found")
    return PatientResponse.model_validate(patient)


@router.get("", response_model=list[PatientListResponse])
def list_patients(
    limit: int = 50,
    offset: int = 0,
    repo=Depends(get_repo),
    current_user: dict = Depends(get_current_user),
):
    """Lister tous les patients"""
    patients = repo.list(organisation_id=current_user["organisation_id"], limit=limit, offset=offset)
    return [PatientListResponse.model_validate(p) for p in patients]


@router.put("/{patient_id}", response_model=PatientResponse)
def update_patient(
    patient_id: int,
    payload: PatientUpdateRequest,
    repo=Depends(get_repo),
):
    """Mettre à jour un patient"""
    fields = payload.model_dump(exclude_unset=True)
    patient = repo.update(patient_id, **fields)
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")
    return PatientResponse.model_validate(patient)


@router.delete("/{patient_id}", status_code=204)
def delete_patient(
    patient_id: int,
    repo=Depends(get_repo),
):
    """Supprimer un patient"""
    success = repo.delete(patient_id)
    if not success:
        raise HTTPException(status_code=404, detail="Patient not found")


# ============ REFERENCE DATA ENDPOINTS ============

@router.get("/meta/services", response_model=list[str])
def list_services(
    repo=Depends(get_repo),
    current_user: dict = Depends(get_current_user),
):
    """List all distinct services available in the organization"""
    return repo.list_services(current_user["organisation_id"])


@router.get("/meta/medecins", response_model=list[str])
def list_medecins(
    repo=Depends(get_repo),
    current_user: dict = Depends(get_current_user),
):
    """List all distinct doctors available in the organization"""
    return repo.list_medecins(current_user["organisation_id"])
