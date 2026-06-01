use std::sync::Mutex;
use rusqlite::{params, Connection};

use crate::models::device::{CreateDeviceRequest, Device, UpdateDeviceRequest};
use crate::error::AppError;

pub trait DeviceRepository: Send + Sync {
    fn list(&self) -> Result<Vec<Device>, AppError>;
    fn get_by_id(&self, device_id: &str) -> Result<Option<Device>, AppError>;
    fn create(&self, payload: CreateDeviceRequest) -> Result<Device, AppError>;
    fn update(&self, device_id: &str, payload: UpdateDeviceRequest) -> Result<Option<Device>, AppError>;
    fn delete(&self, device_id: &str) -> Result<bool, AppError>;
    fn get_pending(&self) -> Result<Vec<Device>, AppError>;
    fn resolve_sync(&self, local_id: &str, remote_id: Option<String>, status: &str) -> Result<(), AppError>;
}

pub struct SqliteDeviceRepository {
    conn: Mutex<Connection>,
}

impl SqliteDeviceRepository {
    pub fn new(db_path: &str) -> Self {
        let conn = Connection::open(db_path).expect("Impossible d'ouvrir la base de données SQLite");
        
        conn.execute(
            "CREATE TABLE IF NOT EXISTS devices (
                device_id TEXT PRIMARY KEY,
                organisation_id INTEGER NOT NULL,
                marque_modele TEXT NOT NULL,
                serial_number TEXT,
                connection_type TEXT NOT NULL,
                etat TEXT NOT NULL,
                sync_status TEXT NOT NULL DEFAULT 'pending_insert',
                remote_id TEXT
            )",
            [],
        ).expect("Impossible de créer la table devices");

        Self {
            conn: Mutex::new(conn),
        }
    }
}

impl DeviceRepository for SqliteDeviceRepository {
    fn list(&self) -> Result<Vec<Device>, AppError> {
        let conn = self.conn.lock().map_err(|_| AppError::Internal("lock poisoned".into()))?;
        let mut stmt = conn.prepare("SELECT device_id, organisation_id, marque_modele, serial_number, connection_type, etat, sync_status, remote_id FROM devices WHERE sync_status != 'pending_delete'")?;
        
        let iter = stmt.query_map([], |row| {
            Ok(Device {
                device_id: row.get(0)?,
                organisation_id: row.get::<_, i64>(1)? as u64,
                marque_modele: row.get(2)?,
                serial_number: row.get(3)?,
                connection_type: row.get(4)?,
                etat: row.get(5)?,
                sync_status: row.get(6)?,
                remote_id: row.get(7)?,
            })
        })?;

        let mut items = Vec::new();
        for item in iter {
            items.push(item?);
        }
        Ok(items)
    }

    fn get_by_id(&self, device_id: &str) -> Result<Option<Device>, AppError> {
        let conn = self.conn.lock().map_err(|_| AppError::Internal("lock poisoned".into()))?;
        let mut stmt = conn.prepare("SELECT device_id, organisation_id, marque_modele, serial_number, connection_type, etat, sync_status, remote_id FROM devices WHERE device_id = ?1 AND sync_status != 'pending_delete'")?;
        
        let mut iter = stmt.query_map(params![device_id], |row| {
            Ok(Device {
                device_id: row.get(0)?,
                organisation_id: row.get::<_, i64>(1)? as u64,
                marque_modele: row.get(2)?,
                serial_number: row.get(3)?,
                connection_type: row.get(4)?,
                etat: row.get(5)?,
                sync_status: row.get(6)?,
                remote_id: row.get(7)?,
            })
        })?;

        if let Some(item) = iter.next() {
            Ok(Some(item?))
        } else {
            Ok(None)
        }
    }

    fn create(&self, payload: CreateDeviceRequest) -> Result<Device, AppError> {
        let conn = self.conn.lock().map_err(|_| AppError::Internal("lock poisoned".into()))?;
        let organisation_id: i64 = 1; // Fixé pour le desktop pour l'instant
        let device_id = uuid::Uuid::new_v4().to_string();

        conn.execute(
            "INSERT INTO devices (device_id, organisation_id, marque_modele, serial_number, connection_type, etat, sync_status, remote_id) VALUES (?1, ?2, ?3, ?4, ?5, ?6, ?7, ?8)",
            params![device_id, organisation_id, payload.marque_modele, payload.serial_number, payload.connection_type, payload.etat, "pending_insert", None::<String>],
        )?;

        Ok(Device {
            device_id,
            organisation_id: organisation_id as u64,
            marque_modele: payload.marque_modele,
            serial_number: payload.serial_number,
            connection_type: payload.connection_type,
            etat: payload.etat,
            sync_status: "pending_insert".to_string(),
            remote_id: None,
        })
    }

    fn update(&self, device_id: &str, payload: UpdateDeviceRequest) -> Result<Option<Device>, AppError> {
        let mut device = match self.get_by_id(device_id)? {
            Some(d) => d,
            None => return Ok(None),
        };

        if let Some(val) = payload.marque_modele { device.marque_modele = val; }
        if let Some(val) = payload.serial_number { device.serial_number = Some(val); }
        if let Some(val) = payload.connection_type { device.connection_type = val; }
        if let Some(val) = payload.etat { device.etat = val; }

        if device.sync_status != "pending_insert" {
            device.sync_status = "pending_update".to_string();
        }

        let conn = self.conn.lock().map_err(|_| AppError::Internal("lock poisoned".into()))?;
        conn.execute(
            "UPDATE devices SET marque_modele = ?1, serial_number = ?2, connection_type = ?3, etat = ?4, sync_status = ?5 WHERE device_id = ?6",
            params![device.marque_modele, device.serial_number, device.connection_type, device.etat, device.sync_status, device_id],
        )?;

        Ok(Some(device))
    }

    fn delete(&self, device_id: &str) -> Result<bool, AppError> {
        let conn = self.conn.lock().map_err(|_| AppError::Internal("lock poisoned".into()))?;
        
        let mut stmt = conn.prepare("SELECT sync_status FROM devices WHERE device_id = ?1")?;
        let status: Option<String> = stmt.query_row(params![device_id], |row| row.get(0)).ok();
        
        let changes = if let Some(st) = status {
            if st == "pending_insert" {
                conn.execute("DELETE FROM devices WHERE device_id = ?1", params![device_id])?
            } else {
                conn.execute("UPDATE devices SET sync_status = 'pending_delete' WHERE device_id = ?1", params![device_id])?
            }
        } else {
            0
        };
        Ok(changes > 0)
    }

    fn get_pending(&self) -> Result<Vec<Device>, AppError> {
        let conn = self.conn.lock().map_err(|_| AppError::Internal("lock poisoned".into()))?;
        let mut stmt = conn.prepare("SELECT device_id, organisation_id, marque_modele, serial_number, connection_type, etat, sync_status, remote_id FROM devices WHERE sync_status != 'synced'")?;
        
        let iter = stmt.query_map([], |row| {
            Ok(Device {
                device_id: row.get(0)?,
                organisation_id: row.get::<_, i64>(1)? as u64,
                marque_modele: row.get(2)?,
                serial_number: row.get(3)?,
                connection_type: row.get(4)?,
                etat: row.get(5)?,
                sync_status: row.get(6)?,
                remote_id: row.get(7)?,
            })
        })?;

        let mut items = Vec::new();
        for item in iter {
            items.push(item?);
        }
        Ok(items)
    }

    fn resolve_sync(&self, local_id: &str, remote_id: Option<String>, status: &str) -> Result<(), AppError> {
        let conn = self.conn.lock().map_err(|_| AppError::Internal("lock poisoned".into()))?;
        if status == "deleted" {
            conn.execute("DELETE FROM devices WHERE device_id = ?1", params![local_id])?;
        } else {
            conn.execute(
                "UPDATE devices SET sync_status = ?1, remote_id = ?2 WHERE device_id = ?3",
                params![status, remote_id, local_id],
            )?;
        }
        Ok(())
    }
}
