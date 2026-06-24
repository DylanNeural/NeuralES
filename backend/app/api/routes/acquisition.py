from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from datetime import datetime
from sqlalchemy.orm import Session

from app.data.db import get_db
from app.data.repositories.result_repository import SessionRepository
from app.api.routes.auth import get_current_user

router = APIRouter(prefix="/acquisition", tags=["Acquisition"])

# Runtime state for active streaming sessions (fatigue score, quality, status).
# This dict is intentionally in-memory — it holds ephemeral real-time metrics
# that don't need to survive a restart. Durable session records are in t_session_mesure.
active_sessions: dict[str, dict] = {}


class StartAcqResponse(BaseModel):
    session_id: str


class StopAcqRequest(BaseModel):
    session_id: str


class LiveMetrics(BaseModel):
    fatigue_score: float
    quality: float
    timestamp: str


@router.post("/start", response_model=StartAcqResponse)
async def start_acquisition(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """Démarrer une nouvelle session d'acquisition EEG"""
    repo = SessionRepository(db)
    db_session = repo.create(
        mode="live",
        created_by_user_id=current_user["user_id"],
        organisation_id=current_user["organisation_id"],
        started_at=datetime.now(),
    )
    session_id = str(db_session.session_id)
    active_sessions[session_id] = {
        "started_at": datetime.now(),
        "status": "running",
        "fatigue_score": 0.0,
        "quality": 85.0,
    }
    return StartAcqResponse(session_id=session_id)


@router.post("/stop")
async def stop_acquisition(
    body: StopAcqRequest,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """Arrêter une session d'acquisition"""
    session_id = body.session_id
    stopped_at = datetime.now()

    if session_id in active_sessions:
        active_sessions[session_id]["status"] = "stopped"
        active_sessions[session_id]["stopped_at"] = stopped_at

    try:
        repo = SessionRepository(db)
        db_session = repo.get_by_id(int(session_id))
        if db_session and db_session.organisation_id == current_user["organisation_id"]:
            repo.update(int(session_id), ended_at=stopped_at)
    except ValueError:
        pass

    return {"status": "success", "session_id": session_id}


@router.get("/{session_id}/live", response_model=LiveMetrics)
async def get_live_metrics(
    session_id: str,
    current_user: dict = Depends(get_current_user),
):
    """Récupérer les métriques en temps réel d'une session"""
    if session_id not in active_sessions:
        raise HTTPException(status_code=404, detail="Session not found")

    session = active_sessions[session_id]
    return LiveMetrics(
        fatigue_score=session.get("fatigue_score", 0.0),
        quality=session.get("quality", 85.0),
        timestamp=datetime.now().isoformat(),
    )
