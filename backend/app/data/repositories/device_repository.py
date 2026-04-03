from __future__ import annotations
from sqlalchemy.orm import Session
from sqlalchemy import select
from datetime import datetime

from app.data.models.device_model import DeviceModel


class DeviceRepository:
    """Access DB for devices"""

    def __init__(self, db: Session):
        self.db = db

    def create(self, marque_modele: str, organisation_id: int, connection_type: str, etat: str,
               serial_number: str | None = None) -> DeviceModel:
        """Create a new device"""
        device = DeviceModel(
            marque_modele=marque_modele,
            serial_number=serial_number,
            connection_type=connection_type,
            etat=etat,
            organisation_id=organisation_id,
        )
        self.db.add(device)
        self.db.commit()
        self.db.refresh(device)
        return device

    def get_by_id(self, device_id: int) -> DeviceModel | None:
        """Get device by ID"""
        stmt = select(DeviceModel).where(
            DeviceModel.device_id == device_id,
            DeviceModel.deleted_at.is_(None)
        )
        return self.db.execute(stmt).scalar_one_or_none()

    def list_by_organisation(self, organisation_id: int, limit: int = 50, offset: int = 0) -> list[DeviceModel]:
        """List all devices for an organisation"""
        stmt = select(DeviceModel).where(
            DeviceModel.organisation_id == organisation_id,
            DeviceModel.deleted_at.is_(None)
        ).order_by(DeviceModel.device_id.desc()).limit(limit).offset(offset)
        return self.db.execute(stmt).scalars().all()

    def update(self, device_id: int, **fields) -> DeviceModel | None:
        """Update a device"""
        stmt = select(DeviceModel).where(
            DeviceModel.device_id == device_id,
            DeviceModel.deleted_at.is_(None)
        )
        device = self.db.execute(stmt).scalar_one_or_none()
        if not device:
            return None
        
        protected_fields = ["device_id", "created_at", "organisation_id", "serial_number", "deleted_at"]
        for key, value in fields.items():
            if hasattr(device, key) and key not in protected_fields:
                setattr(device, key, value)
        
        self.db.commit()
        self.db.refresh(device)
        return device

    def soft_delete(self, device_id: int) -> bool:
        """Soft delete a device"""
        stmt = select(DeviceModel).where(
            DeviceModel.device_id == device_id,
            DeviceModel.deleted_at.is_(None)
        )
        device = self.db.execute(stmt).scalar_one_or_none()
        if not device:
            return False
        
        device.deleted_at = datetime.now()
        self.db.commit()
        return True
