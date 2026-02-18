from __future__ import annotations
from sqlalchemy.orm import Session
from sqlalchemy import select

from app.data.models.service_model import ServiceModel


class ServiceRepository:
    """Access DB for services (reference data)"""

    def __init__(self, db: Session):
        self.db = db

    def list_by_organisation(self, organisation_id: int) -> list[ServiceModel]:
        """List all services for an organisation (excluding deleted)"""
        stmt = (
            select(ServiceModel)
            .where(ServiceModel.organisation_id == organisation_id)
            .where(ServiceModel.deleted_at.is_(None))
            .order_by(ServiceModel.nom)
        )
        return self.db.execute(stmt).scalars().all()

    def get_by_id(self, service_id: int) -> ServiceModel | None:
        """Get service by ID"""
        stmt = (
            select(ServiceModel)
            .where(ServiceModel.service_id == service_id)
            .where(ServiceModel.deleted_at.is_(None))
        )
        return self.db.execute(stmt).scalar_one_or_none()

    def create(self, nom: str, organisation_id: int) -> ServiceModel:
        """Create a new service"""
        service = ServiceModel(nom=nom, organisation_id=organisation_id)
        self.db.add(service)
        self.db.commit()
        self.db.refresh(service)
        return service

    def soft_delete(self, service_id: int) -> bool:
        """Soft delete a service by setting deleted_at"""
        service = self.get_by_id(service_id)
        if not service:
            return False
        
        service.deleted_at = __import__('datetime').datetime.now()
        self.db.commit()
        return True
