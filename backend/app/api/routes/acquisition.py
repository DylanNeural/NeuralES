from fastapi import APIRouter
from pydantic import BaseModel
from datetime import datetime
import uuid

router = APIRouter(prefix="/acquisition", tags=["Acquisition"])

# Store en mémoire pour les sessions (en prod => base de données)
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
async def start_acquisition():
    """Démarrer une nouvelle session d'acquisition EEG"""
    session_id = str(uuid.uuid4())
    active_sessions[session_id] = {
        "started_at": datetime.now(),
        "status": "running",
        "fatigue_score": 0.0,
        "quality": 85.0,
    }
    return StartAcqResponse(session_id=session_id)


@router.post("/stop")
async def stop_acquisition(body: StopAcqRequest):
    """Arrêter une session d'acquisition"""
    session_id = body.session_id
    if session_id in active_sessions:
        active_sessions[session_id]["status"] = "stopped"
        active_sessions[session_id]["stopped_at"] = datetime.now()
    return {"status": "success", "session_id": session_id}


@router.get("/{session_id}/live", response_model=LiveMetrics)
async def get_live_metrics(session_id: str):
    """Récupérer les métriques en temps réel d'une session"""
    if session_id not in active_sessions:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Session not found")
    
    session = active_sessions[session_id]
    return LiveMetrics(
        fatigue_score=session.get("fatigue_score", 0.0),
        quality=session.get("quality", 85.0),
        timestamp=datetime.now().isoformat(),
    )
