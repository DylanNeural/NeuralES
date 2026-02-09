from app.application.ports.organisation_repository import OrganisationRepository


class DeleteOrganisation:
    def __init__(self, repo: OrganisationRepository):
        self.repo = repo

    def execute(self, organisation_id: int) -> bool:
        """Supprimer une organisation. Retourne True si suppresssion, False otherwise."""
        return self.repo.delete(organisation_id)

