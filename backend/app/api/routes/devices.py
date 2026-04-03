from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel

from app.data.db import get_db
from app.data.repositories.device_repository import DeviceRepository
from app.api.routes.auth import get_current_user

router = APIRouter(prefix="/devices", tags=["devices"])


class DeviceBase(BaseModel):
    marque_modele: str
    serial_number: str | None = None
    connection_type: str
    etat: str


class DeviceCreate(DeviceBase):
    pass


class DeviceResponse(DeviceBase):
    device_id: int
    organisation_id: int

    class Config:
        from_attributes = True


class DeviceListResponse(BaseModel):
    items: list[DeviceResponse]
    total: int
    limit: int
    offset: int


def get_repo(db: Session = Depends(get_db)) -> DeviceRepository:
    return DeviceRepository(db)


@router.post("", response_model=DeviceResponse, status_code=201)
def create_device(
    payload: DeviceCreate,
    repo=Depends(get_repo),
    current_user: dict = Depends(get_current_user),
):
    """Create a new device"""
    device = repo.create(
        marque_modele=payload.marque_modele,
        organisation_id=current_user["organisation_id"],
        connection_type=payload.connection_type,
        etat=payload.etat,
        serial_number=payload.serial_number,
    )
    return DeviceResponse.model_validate(device)


@router.get("", response_model=list[DeviceResponse])
def list_devices(
    limit: int = 50,
    offset: int = 0,
    repo=Depends(get_repo),
    current_user: dict = Depends(get_current_user),
):
    """List all devices for the organisation"""
    devices = repo.list_by_organisation(
        organisation_id=current_user["organisation_id"],
        limit=limit,
        offset=offset
    )
    return [DeviceResponse.model_validate(d) for d in devices]


@router.get("/{device_id}", response_model=DeviceResponse)
def get_device(
    device_id: int,
    repo=Depends(get_repo),
    current_user: dict = Depends(get_current_user),
):
    """Get device by ID"""
    device = repo.get_by_id(device_id)
    if not device or device.organisation_id != current_user["organisation_id"]:
        raise HTTPException(status_code=404, detail="Device not found")
    return DeviceResponse.model_validate(device)


@router.put("/{device_id}", response_model=DeviceResponse)
def update_device(
    device_id: int,
    payload: DeviceCreate,
    repo=Depends(get_repo),
    current_user: dict = Depends(get_current_user),
):
    """Update a device"""
    device = repo.get_by_id(device_id)
    if not device or device.organisation_id != current_user["organisation_id"]:
        raise HTTPException(status_code=404, detail="Device not found")
    
    fields = payload.model_dump(exclude_unset=True)
    device = repo.update(device_id, **fields)
    if not device:
        raise HTTPException(status_code=404, detail="Device not found")
    return DeviceResponse.model_validate(device)


@router.delete("/{device_id}", status_code=204)
def delete_device(
    device_id: int,
    repo=Depends(get_repo),
    current_user: dict = Depends(get_current_user),
):
    """Delete a device (soft delete)"""
    device = repo.get_by_id(device_id)
    if not device or device.organisation_id != current_user["organisation_id"]:
        raise HTTPException(status_code=404, detail="Device not found")
    
    success = repo.soft_delete(device_id)
    if not success:
        raise HTTPException(status_code=404, detail="Device not found")
