from datetime import datetime
from pydantic import BaseModel, Field


class SessionCreateRequest(BaseModel):
    """Schéma pour créer une session de mesure"""
    mode: str = Field(min_length=1, max_length=20)
    created_by_user_id: int = Field(gt=0)
    organisation_id: int = Field(gt=0)
    patient_id: int | None = Field(default=None, gt=0)
    device_id: int | None = Field(default=None, gt=0)
    consent_id: int | None = Field(default=None, gt=0)
    started_at: datetime | None = None
    ended_at: datetime | None = None
    notes: str | None = Field(default=None, max_length=255)
    app_version: str | None = Field(default=None, max_length=50)


class SessionUpdateRequest(BaseModel):
    """Schéma pour mettre à jour une session de mesure"""
    mode: str | None = Field(default=None, min_length=1, max_length=20)
    patient_id: int | None = Field(default=None, gt=0)
    device_id: int | None = Field(default=None, gt=0)
    consent_id: int | None = Field(default=None, gt=0)
    started_at: datetime | None = None
    ended_at: datetime | None = None
    notes: str | None = Field(default=None, max_length=255)
    app_version: str | None = Field(default=None, max_length=50)


class SessionResponse(BaseModel):
    """Schéma de réponse pour une session de mesure"""
    session_id: int
    mode: str
    started_at: datetime
    ended_at: datetime | None
    notes: str | None
    app_version: str | None
    device_id: int | None
    consent_id: int | None
    patient_id: int | None
    created_by_user_id: int
    organisation_id: int

    class Config:
        from_attributes = True


class SessionListResponse(BaseModel):
    """Schéma simplifié pour liste de sessions"""
    session_id: int
    mode: str
    started_at: datetime
    ended_at: datetime | None
    patient_id: int | None
    device_id: int | None

    class Config:
        from_attributes = True
