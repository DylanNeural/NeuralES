from app.application.ports.organisation_repository import OrganisationRepository
from app.domain.entities.organisation import Organisation

class ListOrganisations:
    def __init__(self, repo: OrganisationRepository):
        self.repo = repo

    def execute(self, limit: int = 50, offset: int = 0) -> list[Organisation]:
        limit = max(1, min(limit, 200))
        offset = max(0, offset)
        return self.repo.list(limit=limit, offset=offset)
