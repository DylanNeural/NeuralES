from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import select, delete

from app.data.models.result_model import ResultModel


class ResultRepository:
    """Accès DB pour les résultats d'acquisition"""

    def __init__(self, db: Session):
        self.db = db

    def create(self, session_id: str, patient_id: int, acquisition_date: datetime,
               fatigue_score: float, quality: str, notes: str | None = None) -> ResultModel:
        result = ResultModel(
            session_id=session_id,
            patient_id=patient_id,
            acquisition_date=acquisition_date,
            fatigue_score=fatigue_score,
            quality=quality,
            notes=notes,
        )
        self.db.add(result)
        self.db.commit()
        self.db.refresh(result)
        return result

    def get_by_id(self, result_id: int) -> ResultModel | None:
        return self.db.get(ResultModel, result_id)

    def get_by_session_id(self, session_id: str) -> ResultModel | None:
        stmt = select(ResultModel).where(ResultModel.session_id == session_id)
        return self.db.execute(stmt).scalar_one_or_none()

    def list_by_patient(self, patient_id: int, limit: int = 50, offset: int = 0) -> list[ResultModel]:
        stmt = (
            select(ResultModel)
            .where(ResultModel.patient_id == patient_id)
            .order_by(ResultModel.result_id.desc())
            .limit(limit)
            .offset(offset)
        )
        return self.db.execute(stmt).scalars().all()

    def list(self, limit: int = 50, offset: int = 0) -> list[ResultModel]:
        stmt = (
            select(ResultModel)
            .order_by(ResultModel.result_id.desc())
            .limit(limit)
            .offset(offset)
        )
        return self.db.execute(stmt).scalars().all()

    def update(self, result_id: int, **fields) -> ResultModel | None:
        result = self.get_by_id(result_id)
        if not result:
            return None
        for key, value in fields.items():
            if hasattr(result, key) and key not in ["result_id", "created_at"]:
                setattr(result, key, value)
        self.db.commit()
        self.db.refresh(result)
        return result

    def delete(self, result_id: int) -> bool:
        stmt = delete(ResultModel).where(ResultModel.result_id == result_id)
        res = self.db.execute(stmt)
        self.db.commit()
        return (res.rowcount or 0) > 0
