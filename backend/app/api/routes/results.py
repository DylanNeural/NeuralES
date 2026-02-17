from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.data.db import get_db
from app.data.repositories.result_repository import ResultRepository

from app.api.schemas.result import (
    ResultCreateRequest,
    ResultUpdateRequest,
    ResultResponse,
    ResultListResponse,
)

router = APIRouter(prefix="/results", tags=["results"])


def get_repo(db: Session = Depends(get_db)) -> ResultRepository:
    return ResultRepository(db)


@router.post("", response_model=ResultResponse, status_code=201)
def create_result(
    payload: ResultCreateRequest,
    repo=Depends(get_repo),
):
    """Créer un nouveau résultat d'acquisition"""
    # Check if session_id already exists
    existing = repo.get_by_session_id(payload.session_id)
    if existing:
        raise HTTPException(status_code=409, detail="Result with this session_id already exists")
    
    result = repo.create(
        session_id=payload.session_id,
        patient_id=payload.patient_id,
        acquisition_date=payload.acquisition_date,
        fatigue_score=payload.fatigue_score,
        quality=payload.quality,
        notes=payload.notes,
    )
    return ResultResponse.model_validate(result)


@router.get("/{result_id}", response_model=ResultResponse)
def get_result(
    result_id: int,
    repo=Depends(get_repo),
):
    """Récupérer un résultat par ID"""
    result = repo.get_by_id(result_id)
    if not result:
        raise HTTPException(status_code=404, detail="Result not found")
    return ResultResponse.model_validate(result)


@router.get("", response_model=list[ResultListResponse])
def list_results(
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    repo=Depends(get_repo),
):
    """Lister tous les résultats"""
    results = repo.list(limit=limit, offset=offset)
    return [ResultListResponse.model_validate(r) for r in results]


@router.get("/patient/{patient_id}", response_model=list[ResultListResponse])
def list_results_by_patient(
    patient_id: int,
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    repo=Depends(get_repo),
):
    """Lister les résultats d'un patient"""
    results = repo.list_by_patient(patient_id, limit=limit, offset=offset)
    return [ResultListResponse.model_validate(r) for r in results]


@router.put("/{result_id}", response_model=ResultResponse)
def update_result(
    result_id: int,
    payload: ResultUpdateRequest,
    repo=Depends(get_repo),
):
    """Mettre à jour un résultat"""
    fields = payload.model_dump(exclude_unset=True)
    result = repo.update(result_id, **fields)
    if not result:
        raise HTTPException(status_code=404, detail="Result not found")
    return ResultResponse.model_validate(result)


@router.delete("/{result_id}", status_code=204)
def delete_result(
    result_id: int,
    repo=Depends(get_repo),
):
    """Supprimer un résultat"""
    success = repo.delete(result_id)
    if not success:
        raise HTTPException(status_code=404, detail="Result not found")
