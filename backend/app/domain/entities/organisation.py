from dataclasses import dataclass
from datetime import datetime

@dataclass(frozen=True)
class Organisation:
    organisation_id: int | None
    nom: str
    org_type: str
    adresse: str | None
    created_at: datetime
