from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.data.db import get_db
from app.data.repositories.result_repository import SessionRepository
from app.api.routes.auth import get_current_user

from app.api.schemas.result import (
    SessionCreateRequest,
    SessionUpdateRequest,
    SessionResponse,
    SessionListResponse,
)

router = APIRouter(prefix="/results", tags=["results"])


def get_repo(db: Session = Depends(get_db)) -> SessionRepository:
    return SessionRepository(db)


@router.post("", response_model=SessionResponse, status_code=201)
def create_result(
    payload: SessionCreateRequest,
    repo=Depends(get_repo),
    current_user: dict = Depends(get_current_user),
):
    """Créer une nouvelle session de mesure"""
    session = repo.create(
        mode=payload.mode,
        created_by_user_id=current_user["user_id"],
        organisation_id=current_user["organisation_id"],
        patient_id=payload.patient_id,
        device_id=payload.device_id,
        consent_id=payload.consent_id,
        started_at=payload.started_at,
        ended_at=payload.ended_at,
        notes=payload.notes,
        app_version=payload.app_version,
    )
    return SessionResponse.model_validate(session)


@router.get("/{session_id}", response_model=SessionResponse)
def get_result(
    session_id: int,
    repo=Depends(get_repo),
    current_user: dict = Depends(get_current_user),
):
    """Récupérer une session par ID"""
    session = repo.get_by_id(session_id)
    if not session or session.organisation_id != current_user["organisation_id"]:
        raise HTTPException(status_code=404, detail="Session not found")
    return SessionResponse.model_validate(session)


@router.get("", response_model=list[SessionListResponse])
def list_results(
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    repo=Depends(get_repo),
    current_user: dict = Depends(get_current_user),
):
    """Lister toutes les sessions de l'organisation"""
    sessions = repo.list_by_organisation(
        organisation_id=current_user["organisation_id"],
        limit=limit,
        offset=offset,
    )
    return [SessionListResponse.model_validate(s) for s in sessions]


@router.get("/patient/{patient_id}", response_model=list[SessionListResponse])
def list_results_by_patient(
    patient_id: int,
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    repo=Depends(get_repo),
    current_user: dict = Depends(get_current_user),
):
    """Lister les sessions d'un patient"""
    sessions = repo.list_by_patient(patient_id, limit=limit, offset=offset)
    sessions = [s for s in sessions if s.organisation_id == current_user["organisation_id"]]
    return [SessionListResponse.model_validate(s) for s in sessions]


@router.put("/{session_id}", response_model=SessionResponse)
def update_result(
    session_id: int,
    payload: SessionUpdateRequest,
    repo=Depends(get_repo),
    current_user: dict = Depends(get_current_user),
):
    """Mettre à jour une session"""
    session = repo.get_by_id(session_id)
    if not session or session.organisation_id != current_user["organisation_id"]:
        raise HTTPException(status_code=404, detail="Session not found")
    fields = payload.model_dump(exclude_unset=True)
    session = repo.update(session_id, **fields)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    return SessionResponse.model_validate(session)


@router.delete("/{session_id}", status_code=204)
def delete_result(
    session_id: int,
    repo=Depends(get_repo),
    current_user: dict = Depends(get_current_user),
):
    """Supprimer une session"""
    session = repo.get_by_id(session_id)
    if not session or session.organisation_id != current_user["organisation_id"]:
        raise HTTPException(status_code=404, detail="Session not found")
    repo.delete(session_id)
