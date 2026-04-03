from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import select, delete

from app.data.models.result_model import SessionModel


class SessionRepository:
    """Accès DB pour les sessions de mesure"""

    def __init__(self, db: Session):
        self.db = db

    def create(
        self,
        mode: str,
        created_by_user_id: int,
        organisation_id: int,
        patient_id: int | None = None,
        device_id: int | None = None,
        consent_id: int | None = None,
        started_at: datetime | None = None,
        ended_at: datetime | None = None,
        notes: str | None = None,
        app_version: str | None = None,
    ) -> SessionModel:
        session = SessionModel(
            mode=mode,
            created_by_user_id=created_by_user_id,
            organisation_id=organisation_id,
            patient_id=patient_id,
            device_id=device_id,
            consent_id=consent_id,
            started_at=started_at,
            ended_at=ended_at,
            notes=notes,
            app_version=app_version,
        )
        self.db.add(session)
        self.db.commit()
        self.db.refresh(session)
        return session

    def get_by_id(self, session_id: int) -> SessionModel | None:
        return self.db.get(SessionModel, session_id)

    def list_by_patient(self, patient_id: int, limit: int = 50, offset: int = 0) -> list[SessionModel]:
        stmt = (
            select(SessionModel)
            .where(SessionModel.patient_id == patient_id)
            .order_by(SessionModel.session_id.desc())
            .limit(limit)
            .offset(offset)
        )
        return self.db.execute(stmt).scalars().all()

    def list(self, limit: int = 50, offset: int = 0) -> list[SessionModel]:
        stmt = (
            select(SessionModel)
            .order_by(SessionModel.session_id.desc())
            .limit(limit)
            .offset(offset)
        )
        return self.db.execute(stmt).scalars().all()

    def update(self, session_id: int, **fields) -> SessionModel | None:
        session = self.get_by_id(session_id)
        if not session:
            return None
        for key, value in fields.items():
            if hasattr(session, key) and key not in ["session_id", "created_by_user_id", "organisation_id"]:
                setattr(session, key, value)
        self.db.commit()
        self.db.refresh(session)
        return session

    def delete(self, session_id: int) -> bool:
        stmt = delete(SessionModel).where(SessionModel.session_id == session_id)
        res = self.db.execute(stmt)
        self.db.commit()
        return (res.rowcount or 0) > 0
