from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.data.db import get_db
from app.data.repositories.patient_repository import PatientRepository

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
):
    """Créer un nouveau patient"""
    # Check if patient already exists by SSN
    existing = repo.get_by_secu(payload.numero_securite_sociale)
    if existing:
        raise HTTPException(status_code=409, detail="Patient with this SSN already exists")
    
    patient = repo.create(
        nom=payload.nom,
        prenom=payload.prenom,
        date_naissance=payload.date_naissance,
        numero_securite_sociale=payload.numero_securite_sociale,
        sexe=payload.sexe,
        service=payload.service,
        medecin_referent=payload.medecin_referent,
        remarque=payload.remarque,
    )
    return PatientResponse.model_validate(patient)


@router.get("/{patient_id}", response_model=PatientResponse)
def get_patient(
    patient_id: int,
    repo=Depends(get_repo),
):
    """Récupérer un patient par ID"""
    patient = repo.get_by_id(patient_id)
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")
    return PatientResponse.model_validate(patient)


@router.get("", response_model=list[PatientListResponse])
def list_patients(
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    repo=Depends(get_repo),
):
    """Lister tous les patients"""
    patients = repo.list(limit=limit, offset=offset)
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
