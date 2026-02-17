from datetime import datetime
from pydantic import BaseModel, Field


class ResultCreateRequest(BaseModel):
    """Schéma pour créer un résultat"""
    session_id: str = Field(min_length=1, max_length=100)
    patient_id: int = Field(gt=0)
    acquisition_date: datetime
    fatigue_score: float = Field(ge=0, le=100)
    quality: str = Field(pattern=r"^(Good|Fair|Poor)$")
    notes: str | None = Field(default=None, max_length=500)


class ResultUpdateRequest(BaseModel):
    """Schéma pour mettre à jour un résultat"""
    fatigue_score: float | None = Field(default=None, ge=0, le=100)
    quality: str | None = Field(default=None, pattern=r"^(Good|Fair|Poor)$")
    notes: str | None = Field(default=None, max_length=500)


class ResultResponse(BaseModel):
    """Schéma de réponse pour un résultat"""
    result_id: int
    session_id: str
    patient_id: int
    acquisition_date: datetime
    fatigue_score: float
    quality: str
    notes: str | None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ResultListResponse(BaseModel):
    """Schéma simplifié pour liste de résultats"""
    result_id: int
    session_id: str
    patient_id: int
    acquisition_date: datetime
    fatigue_score: float
    quality: str

    class Config:
        from_attributes = True
