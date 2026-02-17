from sqlalchemy.orm import Session
from sqlalchemy import select, delete

from app.application.ports.organisation_repository import OrganisationRepository
from app.domain.entities.organisation import Organisation
from app.data.models.organisation_model import OrganisationModel


def _to_entity(m: OrganisationModel) -> Organisation:
    """Convertir ORM model vers domain entity"""
    return Organisation(
        organisation_id=m.organisation_id,
        nom=m.nom,
        org_type=m.org_type,
        adresse=m.adresse,
        created_at=m.created_at,
    )


class OrganisationRepositorySQLImpl(OrganisationRepository):
    """Implémentation SQL de OrganisationRepository"""

    def __init__(self, db: Session):
        self.db = db

    def create(self, org: Organisation) -> Organisation:
        m = OrganisationModel(
            nom=org.nom,
            org_type=org.org_type,
            adresse=org.adresse,
            created_at=org.created_at,
        )
        self.db.add(m)
        self.db.commit()
        self.db.refresh(m)
        return _to_entity(m)

    def get_by_id(self, organisation_id: int) -> Organisation | None:
        m = self.db.get(OrganisationModel, organisation_id)
        return _to_entity(m) if m else None

    def list(self, limit: int, offset: int) -> list[Organisation]:
        stmt = (
            select(OrganisationModel)
            .order_by(OrganisationModel.organisation_id)
            .limit(limit)
            .offset(offset)
        )
        rows = self.db.execute(stmt).scalars().all()
        return [_to_entity(r) for r in rows]

    def update(self, org: Organisation) -> Organisation:
        m = self.db.get(OrganisationModel, org.organisation_id)
        if not m:
            raise ValueError("Organisation not found")

        m.nom = org.nom
        m.org_type = org.org_type
        m.adresse = org.adresse

        self.db.commit()
        self.db.refresh(m)
        return _to_entity(m)

    def delete(self, organisation_id: int) -> bool:
        stmt = delete(OrganisationModel).where(
            OrganisationModel.organisation_id == organisation_id
        )
        res = self.db.execute(stmt)
        self.db.commit()
        return (res.rowcount or 0) > 0
