from app.application.ports.organisation_repository import OrganisationRepository
from app.domain.entities.organisation import Organisation

class GetOrganisation:
    def __init__(self, repo: OrganisationRepository):
        self.repo = repo

    def execute(self, organisation_id: int) -> Organisation | None:
        return self.repo.get_by_id(organisation_id)
