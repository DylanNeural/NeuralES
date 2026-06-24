"""Routes d'analytics et de données pour le dashboard."""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import text

from app.data.db import get_db
from app.api.routes.auth import get_current_user
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
        SessionModel.organisation_id == current_user["organisation_id"],
    ).first()

    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

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
        SessionModel.organisation_id == current_user["organisation_id"],
    ).first()

    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

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
        SessionModel.organisation_id == current_user["organisation_id"],
    ).first()

    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    import random

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


@router.get("/patients/{patient_id}/history")
async def get_patient_history(
    patient_id: int,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user),
):
    """Retourne l'historique des sessions d'un patient avec indicateurs de fatigue."""
    sessions = (
        db.query(SessionModel)
        .filter(
            SessionModel.patient_id == patient_id,
            SessionModel.organisation_id == current_user["organisation_id"],
        )
        .order_by(SessionModel.started_at.desc())
        .limit(20)
        .all()
    )

    result = []
    for s in sessions:
        fatigue_score = None
        try:
            row = db.execute(
                text(
                    "SELECT AVG(valeur) AS avg_fatigue FROM t_indicateur "
                    "WHERE session_id = :sid AND nom = 'fatigue_ratio'"
                ),
                {"sid": s.session_id},
            ).first()
            if row and row.avg_fatigue is not None:
                fatigue_score = round(float(row.avg_fatigue) * 100, 1)
        except Exception:
            pass

        result.append(
            {
                "session_id": s.session_id,
                "mode": s.mode,
                "started_at": s.started_at.isoformat() if s.started_at else None,
                "ended_at": s.ended_at.isoformat() if s.ended_at else None,
                "fatigue_score": fatigue_score,
            }
        )

    return {"patient_id": patient_id, "sessions": result}


@router.get("/sessions/{session_id}/alerts")
async def get_session_alerts(
    session_id: int,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user),
):
    """Retourne les alertes déclenchées pendant une session."""
    session = (
        db.query(SessionModel)
        .filter(
            SessionModel.session_id == session_id,
            SessionModel.organisation_id == current_user["organisation_id"],
        )
        .first()
    )
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    alerts = []
    try:
        rows = db.execute(
            text(
                "SELECT alert_type, message, severity, triggered_at FROM t_alerte "
                "WHERE session_id = :sid ORDER BY triggered_at"
            ),
            {"sid": session_id},
        ).fetchall()
        alerts = [
            {
                "type": r.alert_type,
                "message": r.message,
                "severity": r.severity,
                "triggered_at": r.triggered_at.isoformat() if r.triggered_at else None,
            }
            for r in rows
        ]
    except Exception:
        pass

    return {"session_id": session_id, "alerts": alerts}
