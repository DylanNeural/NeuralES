"""Routes d'analytics et de données pour le dashboard."""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.dependencies import get_db, get_current_user
from app.data.models.user_model import UserModel
from app.data.models.result_model import SessionModel

router = APIRouter(prefix="/analytics", tags=["analytics"])


@router.get("/sessions/{session_id}/quality")
async def get_session_quality(
    session_id: int,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user),
):
    """Récupère la qualité du signal pour une session."""
    session = db.query(SessionModel).filter(
        SessionModel.session_id == session_id,
        SessionModel.organisation_id == current_user.organisation_id,
        SessionModel.deleted_at.is_(None),
    ).first()
    
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    # Calcul simplifié de la qualité basée sur la durée et présence de données
    # En prod, ce serait un calcul complexe basé sur les données EEG
    base_quality = 75
    
    # Bonus si la session est complète (has ended_at)
    if session.ended_at:
        base_quality += 10
    
    # Bonus si a des notes (indice que le data est bon)
    if session.notes:
        base_quality += 5
    
    # Cap à 100
    quality_score = min(100, base_quality)
    
    # Détermine la qualité textuelle
    if quality_score >= 85:
        quality_text = "Excellent"
    elif quality_score >= 70:
        quality_text = "Bon"
    else:
        quality_text = "Moyen"
    
    return {
        "session_id": session_id,
        "quality_score": quality_score,
        "quality_text": quality_text,
    }


@router.get("/sessions/{session_id}/eeg")
async def get_session_eeg_data(
    session_id: int,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user),
):
    """Récupère les données EEG simulées pour une session.
    
    En prod, ce serait les vraies données EEG stockées.
    """
    session = db.query(SessionModel).filter(
        SessionModel.session_id == session_id,
        SessionModel.organisation_id == current_user.organisation_id,
        SessionModel.deleted_at.is_(None),
    ).first()
    
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    # Génère des données EEG simulées (en prod ce serait des vraies données)
    import random
    
    # 8 électrodes EEG
    channels = ["Fp1", "Fp2", "F3", "F4", "T3", "T4", "O1", "O2"]
    
    # Génère 100 points de données pour chaque canal
    eeg_data = {
        channel: [random.gauss(50, 10) for _ in range(100)]
        for channel in channels
    }
    
    return {
        "session_id": session_id,
        "channels": channels,
        "data": eeg_data,
        "sampling_rate": 256,  # Hz
        "duration": 100,  # points
    }


@router.get("/sessions/{session_id}/fatigue-score")
async def get_session_fatigue_score(
    session_id: int,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user),
):
    """Récupère le score de fatigue estimé pour une session."""
    session = db.query(SessionModel).filter(
        SessionModel.session_id == session_id,
        SessionModel.organisation_id == current_user.organisation_id,
        SessionModel.deleted_at.is_(None),
    ).first()
    
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    # Calcul simplifié du score de fatigue basé sur le mode et l'heure
    import random
    from datetime import datetime
    
    base_fatigue = 50
    
    # Varie selon le mode
    mode_fatigue_map = {
        "fatigue": 75,
        "moteur": 45,
        "attention": 55,
        "relax": 30,
    }
    
    if session.mode:
        base_fatigue = mode_fatigue_map.get(session.mode.lower(), 50)
    
    # Ajoute un peu d'aléatoire
    fatigue_score = max(0, min(100, base_fatigue + random.randint(-10, 10)))
    
    return {
        "session_id": session_id,
        "fatigue_score": fatigue_score,
        "mode": session.mode,
    }
