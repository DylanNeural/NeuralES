from datetime import datetime
from pydantic import BaseModel, Field


class OrganisationCreateRequest(BaseModel):
    """Schéma pour créer une organisation (API)"""
    nom: str = Field(min_length=1, max_length=100)
    type: str = Field(min_length=1, max_length=50)
    adresse: str | None = Field(default=None, max_length=255)


class OrganisationUpdateRequest(BaseModel):
    """Schéma pour mettre à jour une organisation (API)"""
    nom: str | None = Field(default=None, min_length=1, max_length=100)
    type: str | None = Field(default=None, min_length=1, max_length=50)
    adresse: str | None = Field(default=None, max_length=255)


class OrganisationResponse(BaseModel):
    """Schéma de réponse pour une organisation"""
    organisation_id: int
    nom: str
    type: str
    adresse: str | None
    created_at: datetime

    class Config:
        from_attributes = True
