from datetime import datetime, timezone
from app.application.ports.organisation_repository import OrganisationRepository
from app.domain.entities.organisation import Organisation

class CreateOrganisation:
    def __init__(self, repo: OrganisationRepository):
        self.repo = repo

    def execute(self, nom: str, org_type: str, adresse: str | None) -> Organisation:
        org = Organisation(
            organisation_id=None,
            nom=nom,
            org_type=org_type,
            adresse=adresse,
            created_at=datetime.now(timezone.utc),
        )
        return self.repo.create(org)
