use std::sync::Mutex;
use rusqlite::{params, Connection};

use crate::models::patient::{CreatePatientRequest, Patient, UpdatePatientRequest};
use crate::error::AppError;

pub trait PatientRepository: Send + Sync {
    fn list(&self) -> Result<Vec<Patient>, AppError>;
    fn get_by_id(&self, patient_id: &str) -> Result<Option<Patient>, AppError>;
    fn create(&self, payload: CreatePatientRequest) -> Result<Patient, AppError>;
    fn update(&self, patient_id: &str, payload: UpdatePatientRequest) -> Result<Option<Patient>, AppError>;
    fn delete(&self, patient_id: &str) -> Result<bool, AppError>;
    fn get_pending(&self) -> Result<Vec<Patient>, AppError>;
    fn resolve_sync(&self, local_id: &str, remote_id: Option<String>, status: &str) -> Result<(), AppError>;
}

pub struct SqlitePatientRepository {
    conn: Mutex<Connection>,
}

impl SqlitePatientRepository {
    pub fn new(db_path: &str) -> Self {
        let conn = Connection::open(db_path).expect("Impossible d'ouvrir la base de données SQLite");
        
        conn.execute(
            "CREATE TABLE IF NOT EXISTS patients (
                patient_id TEXT PRIMARY KEY,
                identifiant_interne TEXT NOT NULL,
                nom TEXT NOT NULL,
                prenom TEXT NOT NULL,
                date_naissance TEXT,
                numero_securite_sociale TEXT,
                sexe TEXT,
                service TEXT,
                medecin_referent TEXT,
                remarque TEXT,
                notes TEXT,
                organisation_id INTEGER NOT NULL,
                sync_status TEXT NOT NULL DEFAULT 'pending_insert',
                remote_id TEXT
            )",
            [],
        ).expect("Impossible de créer la table patients");

        Self {
            conn: Mutex::new(conn),
        }
    }
}

impl PatientRepository for SqlitePatientRepository {
    fn list(&self) -> Result<Vec<Patient>, AppError> {
        let conn = self.conn.lock().map_err(|_| AppError::Internal("lock poisoned".into()))?;
        let mut stmt = conn.prepare("SELECT patient_id, identifiant_interne, nom, prenom, date_naissance, numero_securite_sociale, sexe, service, medecin_referent, remarque, notes, organisation_id, sync_status, remote_id FROM patients WHERE sync_status != 'pending_delete'")?;
        
        let iter = stmt.query_map([], |row| {
            Ok(Patient {
                patient_id: row.get(0)?,
                identifiant_interne: row.get(1)?,
                nom: row.get(2)?,
                prenom: row.get(3)?,
                date_naissance: row.get(4)?,
                numero_securite_sociale: row.get(5)?,
                sexe: row.get(6)?,
                service: row.get(7)?,
                medecin_referent: row.get(8)?,
                remarque: row.get(9)?,
                notes: row.get(10)?,
                organisation_id: row.get::<_, i64>(11)? as u64,
                sync_status: row.get(12)?,
                remote_id: row.get(13)?,
            })
        })?;

        let mut items = Vec::new();
        for item in iter {
            items.push(item?);
        }
        Ok(items)
    }

    fn get_by_id(&self, patient_id: &str) -> Result<Option<Patient>, AppError> {
        let conn = self.conn.lock().map_err(|_| AppError::Internal("lock poisoned".into()))?;
        let mut stmt = conn.prepare("SELECT patient_id, identifiant_interne, nom, prenom, date_naissance, numero_securite_sociale, sexe, service, medecin_referent, remarque, notes, organisation_id, sync_status, remote_id FROM patients WHERE patient_id = ?1 AND sync_status != 'pending_delete'")?;
        
        let mut iter = stmt.query_map(params![patient_id], |row| {
            Ok(Patient {
                patient_id: row.get(0)?,
                identifiant_interne: row.get(1)?,
                nom: row.get(2)?,
                prenom: row.get(3)?,
                date_naissance: row.get(4)?,
                numero_securite_sociale: row.get(5)?,
                sexe: row.get(6)?,
                service: row.get(7)?,
                medecin_referent: row.get(8)?,
                remarque: row.get(9)?,
                notes: row.get(10)?,
                organisation_id: row.get::<_, i64>(11)? as u64,
                sync_status: row.get(12)?,
                remote_id: row.get(13)?,
            })
        })?;

        if let Some(item) = iter.next() {
            Ok(Some(item?))
        } else {
            Ok(None)
        }
    }

    fn create(&self, payload: CreatePatientRequest) -> Result<Patient, AppError> {
        let conn = self.conn.lock().map_err(|_| AppError::Internal("lock poisoned".into()))?;
        let organisation_id: i64 = 1;
        let patient_id = uuid::Uuid::new_v4().to_string();

        conn.execute(
            "INSERT INTO patients (patient_id, identifiant_interne, nom, prenom, date_naissance, numero_securite_sociale, sexe, service, medecin_referent, remarque, notes, organisation_id, sync_status, remote_id) VALUES (?1, ?2, ?3, ?4, ?5, ?6, ?7, ?8, ?9, ?10, ?11, ?12, ?13, ?14)",
            params![
                patient_id, payload.identifiant_interne, payload.nom, payload.prenom, payload.date_naissance,
                payload.numero_securite_sociale, payload.sexe, payload.service, payload.medecin_referent,
                payload.remarque, payload.notes, organisation_id, "pending_insert", None::<String>
            ],
        )?;

        Ok(Patient {
            patient_id,
            organisation_id: organisation_id as u64,
            identifiant_interne: payload.identifiant_interne,
            nom: payload.nom,
            prenom: payload.prenom,
            date_naissance: payload.date_naissance,
            numero_securite_sociale: payload.numero_securite_sociale,
            sexe: payload.sexe,
            service: payload.service,
            medecin_referent: payload.medecin_referent,
            remarque: payload.remarque,
            notes: payload.notes,
            sync_status: "pending_insert".to_string(),
            remote_id: None,
        })
    }

    fn update(&self, patient_id: &str, payload: UpdatePatientRequest) -> Result<Option<Patient>, AppError> {
        let mut patient = match self.get_by_id(patient_id)? {
            Some(p) => p,
            None => return Ok(None),
        };

        if let Some(val) = payload.identifiant_interne { patient.identifiant_interne = val; }
        if let Some(val) = payload.nom { patient.nom = val; }
        if let Some(val) = payload.prenom { patient.prenom = val; }
        if let Some(val) = payload.date_naissance { patient.date_naissance = Some(val); }
        if let Some(val) = payload.numero_securite_sociale { patient.numero_securite_sociale = Some(val); }
        if let Some(val) = payload.sexe { patient.sexe = Some(val); }
        if let Some(val) = payload.service { patient.service = Some(val); }
        if let Some(val) = payload.medecin_referent { patient.medecin_referent = Some(val); }
        if let Some(val) = payload.remarque { patient.remarque = Some(val); }
        if let Some(val) = payload.notes { patient.notes = Some(val); }

        if patient.sync_status != "pending_insert" {
            patient.sync_status = "pending_update".to_string();
        }

        let conn = self.conn.lock().map_err(|_| AppError::Internal("lock poisoned".into()))?;
        conn.execute(
            "UPDATE patients SET
                identifiant_interne = ?1, nom = ?2, prenom = ?3, date_naissance = ?4,
                numero_securite_sociale = ?5, sexe = ?6, service = ?7, medecin_referent = ?8,
                remarque = ?9, notes = ?10, sync_status = ?11
            WHERE patient_id = ?12",
            params![
                patient.identifiant_interne, patient.nom, patient.prenom, patient.date_naissance,
                patient.numero_securite_sociale, patient.sexe, patient.service, patient.medecin_referent,
                patient.remarque, patient.notes, patient.sync_status, patient_id
            ],
        )?;

        Ok(Some(patient))
    }

    fn delete(&self, patient_id: &str) -> Result<bool, AppError> {
        let conn = self.conn.lock().map_err(|_| AppError::Internal("lock poisoned".into()))?;
        
        let mut stmt = conn.prepare("SELECT sync_status FROM patients WHERE patient_id = ?1")?;
        let status: Option<String> = stmt.query_row(params![patient_id], |row| row.get(0)).ok();
        
        let changes = if let Some(st) = status {
            if st == "pending_insert" {
                conn.execute("DELETE FROM patients WHERE patient_id = ?1", params![patient_id])?
            } else {
                conn.execute("UPDATE patients SET sync_status = 'pending_delete' WHERE patient_id = ?1", params![patient_id])?
            }
        } else {
            0
        };
        Ok(changes > 0)
    }

    fn get_pending(&self) -> Result<Vec<Patient>, AppError> {
        let conn = self.conn.lock().map_err(|_| AppError::Internal("lock poisoned".into()))?;
        let mut stmt = conn.prepare("SELECT patient_id, identifiant_interne, nom, prenom, date_naissance, numero_securite_sociale, sexe, service, medecin_referent, remarque, notes, organisation_id, sync_status, remote_id FROM patients WHERE sync_status != 'synced'")?;
        
        let iter = stmt.query_map([], |row| {
            Ok(Patient {
                patient_id: row.get(0)?,
                identifiant_interne: row.get(1)?,
                nom: row.get(2)?,
                prenom: row.get(3)?,
                date_naissance: row.get(4)?,
                numero_securite_sociale: row.get(5)?,
                sexe: row.get(6)?,
                service: row.get(7)?,
                medecin_referent: row.get(8)?,
                remarque: row.get(9)?,
                notes: row.get(10)?,
                organisation_id: row.get::<_, i64>(11)? as u64,
                sync_status: row.get(12)?,
                remote_id: row.get(13)?,
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
            conn.execute("DELETE FROM patients WHERE patient_id = ?1", params![local_id])?;
        } else {
            conn.execute(
                "UPDATE patients SET sync_status = ?1, remote_id = ?2 WHERE patient_id = ?3",
                params![status, remote_id, local_id],
            )?;
        }
        Ok(())
    }
}