from datetime import datetime
from pydantic import BaseModel, Field

class OrganisationCreateIn(BaseModel):
    nom: str = Field(min_length=1, max_length=100)
    type: str = Field(min_length=1, max_length=50)  # alias API
    adresse: str | None = Field(default=None, max_length=255)

class OrganisationUpdateIn(BaseModel):
    nom: str | None = Field(default=None, min_length=1, max_length=100)
    type: str | None = Field(default=None, min_length=1, max_length=50)  # alias API
    adresse: str | None = Field(default=None, max_length=255)

class OrganisationOut(BaseModel):
    organisation_id: int
    nom: str
    type: str
    adresse: str | None
    created_at: datetime

    class Config:
        from_attributes = True
