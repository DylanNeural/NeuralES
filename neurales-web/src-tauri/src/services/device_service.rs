use std::sync::Arc;

use crate::models::device::{CreateDeviceRequest, Device, UpdateDeviceRequest};
use crate::repositories::device_repository::DeviceRepository;

#[derive(Clone)]
pub struct DeviceService {
    repository: Arc<dyn DeviceRepository>,
}

impl DeviceService {
    pub fn new(repository: Arc<dyn DeviceRepository>) -> Self {
        Self { repository }
    }

    pub fn list_devices(&self) -> Result<Vec<Device>, String> {
        self.repository.list()
    }

    pub fn get_device(&self, device_id: u64) -> Result<Option<Device>, String> {
        self.repository.get_by_id(device_id)
    }

    pub fn create_device(&self, payload: CreateDeviceRequest) -> Result<Device, String> {
        if payload.marque_modele.trim().is_empty() {
            return Err("marque_modele is required".to_string());
        }
        if payload.connection_type.trim().is_empty() {
            return Err("connection_type is required".to_string());
        }
        if payload.etat.trim().is_empty() {
            return Err("etat is required".to_string());
        }

        self.repository.create(payload)
    }

    pub fn update_device(&self, device_id: u64, payload: UpdateDeviceRequest) -> Result<Option<Device>, String> {
        if let Some(ref marque_modele) = payload.marque_modele {
            if marque_modele.trim().is_empty() {
                return Err("marque_modele is required".to_string());
            }
        }
        if let Some(ref connection_type) = payload.connection_type {
            if connection_type.trim().is_empty() {
                return Err("connection_type is required".to_string());
            }
        }
        if let Some(ref etat) = payload.etat {
            if etat.trim().is_empty() {
                return Err("etat is required".to_string());
            }
        }

        self.repository.update(device_id, payload)
    }

    pub fn delete_device(&self, device_id: u64) -> Result<bool, String> {
        self.repository.delete(device_id)
    }
}
