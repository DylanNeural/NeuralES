from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import uuid
from typing import Dict, Any

router = APIRouter(prefix="/acquisition", tags=["Acquisition"])

# Stockage temporaire des sessions (à remplacer par une vraie BDD)
active_sessions: Dict[str, Dict[str, Any]] = {}

class StartAcquisitionRequest(BaseModel):
    patient_id: str = "default_patient"
    device_id: str = "default_device"

class StartAcquisitionResponse(BaseModel):
    session_id: str

class StopAcquisitionRequest(BaseModel):
    session_id: str

class LiveMetrics(BaseModel):
    fatigue_score: float
    quality: str
    timestamp: str

@router.post("/start", response_model=StartAcquisitionResponse)
async def start_acquisition(request: StartAcquisitionRequest = None):
    if request is None:
        request = StartAcquisitionRequest()
    session_id = str(uuid.uuid4())
    active_sessions[session_id] = {
        "patient_id": request.patient_id,
        "device_id": request.device_id,
        "status": "active",
        "start_time": "2024-01-01T00:00:00Z"  # À remplacer par datetime.now()
    }
    return StartAcquisitionResponse(session_id=session_id)

@router.post("/stop")
async def stop_acquisition(request: StopAcquisitionRequest):
    if request.session_id not in active_sessions:
        raise HTTPException(status_code=404, detail="Session not found")
    
    active_sessions[request.session_id]["status"] = "stopped"
    return {"message": "Acquisition stopped"}

@router.get("/{session_id}/live", response_model=LiveMetrics)
async def get_live_metrics(session_id: str):
    if session_id not in active_sessions:
        raise HTTPException(status_code=404, detail="Session not found")
    
    # Données mockées pour le développement
    import random
    return LiveMetrics(
        fatigue_score=random.uniform(0, 1),
        quality="Bonne",
        timestamp="2024-01-01T00:00:00Z"
    )