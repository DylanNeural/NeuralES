from app.application.ports.organisation_repository import OrganisationRepository
from app.domain.entities.organisation import Organisation

class UpdateOrganisation:
    def __init__(self, repo: OrganisationRepository):
        self.repo = repo

    def execute(
        self,
        organisation_id: int,
        nom: str | None,
        org_type: str | None,
        adresse: str | None,
    ) -> Organisation | None:
        existing = self.repo.get_by_id(organisation_id)
        if not existing:
            return None

        updated = Organisation(
            organisation_id=existing.organisation_id,
            nom=nom if nom is not None else existing.nom,
            org_type=org_type if org_type is not None else existing.org_type,
            adresse=adresse if adresse is not None else existing.adresse,
            created_at=existing.created_at,
        )
        return self.repo.update(updated)
