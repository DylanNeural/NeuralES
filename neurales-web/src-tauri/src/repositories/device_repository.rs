use std::sync::atomic::{AtomicU64, Ordering};
use std::sync::Mutex;

use crate::models::device::{CreateDeviceRequest, Device, UpdateDeviceRequest};
use crate::storage::json_store::{load_items, save_items};

const DEVICES_FILE: &str = "devices.json";

pub trait DeviceRepository: Send + Sync {
    fn list(&self) -> Result<Vec<Device>, String>;
    fn get_by_id(&self, device_id: u64) -> Result<Option<Device>, String>;
    fn create(&self, payload: CreateDeviceRequest) -> Result<Device, String>;
    fn update(&self, device_id: u64, payload: UpdateDeviceRequest) -> Result<Option<Device>, String>;
    fn delete(&self, device_id: u64) -> Result<bool, String>;
}

pub struct InMemoryDeviceRepository {
    next_id: AtomicU64,
    items: Mutex<Vec<Device>>,
}

impl InMemoryDeviceRepository {
    pub fn new() -> Self {
        let items = load_items::<Device>(DEVICES_FILE).unwrap_or_default();
        let next_id = items.iter().map(|item| item.device_id).max().unwrap_or(0) + 1;

        Self {
            next_id: AtomicU64::new(next_id),
            items: Mutex::new(items),
        }
    }
}

impl DeviceRepository for InMemoryDeviceRepository {
    fn list(&self) -> Result<Vec<Device>, String> {
        let items = self
            .items
            .lock()
            .map_err(|_| "device repository lock poisoned".to_string())?;
        Ok(items.clone())
    }

    fn get_by_id(&self, device_id: u64) -> Result<Option<Device>, String> {
        let items = self
            .items
            .lock()
            .map_err(|_| "device repository lock poisoned".to_string())?;
        Ok(items.iter().find(|d| d.device_id == device_id).cloned())
    }

    fn create(&self, payload: CreateDeviceRequest) -> Result<Device, String> {
        let mut items = self
            .items
            .lock()
            .map_err(|_| "device repository lock poisoned".to_string())?;

        let device = Device {
            device_id: self.next_id.fetch_add(1, Ordering::Relaxed),
            organisation_id: 1,
            marque_modele: payload.marque_modele,
            serial_number: payload.serial_number,
            connection_type: payload.connection_type,
            etat: payload.etat,
        };

        items.push(device.clone());
        save_items(DEVICES_FILE, &items)?;
        Ok(device)
    }

    fn update(&self, device_id: u64, payload: UpdateDeviceRequest) -> Result<Option<Device>, String> {
        let mut items = self
            .items
            .lock()
            .map_err(|_| "device repository lock poisoned".to_string())?;

        let updated = items.iter_mut().find(|d| d.device_id == device_id).map(|device| {
            if let Some(value) = payload.marque_modele {
                device.marque_modele = value;
            }
            if let Some(value) = payload.serial_number {
                device.serial_number = Some(value);
            }
            if let Some(value) = payload.connection_type {
                device.connection_type = value;
            }
            if let Some(value) = payload.etat {
                device.etat = value;
            }
            device.clone()
        });

        if updated.is_some() {
            save_items(DEVICES_FILE, &items)?;
        }

        Ok(updated)
    }

    fn delete(&self, device_id: u64) -> Result<bool, String> {
        let mut items = self
            .items
            .lock()
            .map_err(|_| "device repository lock poisoned".to_string())?;

        let before = items.len();
        items.retain(|d| d.device_id != device_id);
        let deleted = items.len() != before;
        if deleted {
            save_items(DEVICES_FILE, &items)?;
        }
        Ok(deleted)
    }
}
