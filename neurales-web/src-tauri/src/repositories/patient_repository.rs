use std::sync::atomic::{AtomicU64, Ordering};
use std::sync::Mutex;

use crate::models::patient::{CreatePatientRequest, Patient, UpdatePatientRequest};
use crate::storage::json_store::{load_items, save_items};

const PATIENTS_FILE: &str = "patients.json";

pub trait PatientRepository: Send + Sync {
    fn list(&self) -> Result<Vec<Patient>, String>;
    fn get_by_id(&self, patient_id: u64) -> Result<Option<Patient>, String>;
    fn create(&self, payload: CreatePatientRequest) -> Result<Patient, String>;
    fn update(&self, patient_id: u64, payload: UpdatePatientRequest) -> Result<Option<Patient>, String>;
    fn delete(&self, patient_id: u64) -> Result<bool, String>;
}

pub struct InMemoryPatientRepository {
    next_id: AtomicU64,
    items: Mutex<Vec<Patient>>,
}

impl InMemoryPatientRepository {
    pub fn new() -> Self {
        let items = load_items::<Patient>(PATIENTS_FILE).unwrap_or_default();
        let next_id = items.iter().map(|item| item.patient_id).max().unwrap_or(0) + 1;

        Self {
            next_id: AtomicU64::new(next_id),
            items: Mutex::new(items),
        }
    }
}

impl PatientRepository for InMemoryPatientRepository {
    fn list(&self) -> Result<Vec<Patient>, String> {
        let items = self
            .items
            .lock()
            .map_err(|_| "patient repository lock poisoned".to_string())?;
        Ok(items.clone())
    }

    fn get_by_id(&self, patient_id: u64) -> Result<Option<Patient>, String> {
        let items = self
            .items
            .lock()
            .map_err(|_| "patient repository lock poisoned".to_string())?;
        Ok(items.iter().find(|p| p.patient_id == patient_id).cloned())
    }

    fn create(&self, payload: CreatePatientRequest) -> Result<Patient, String> {
        let mut items = self
            .items
            .lock()
            .map_err(|_| "patient repository lock poisoned".to_string())?;

        let patient = Patient {
            patient_id: self.next_id.fetch_add(1, Ordering::Relaxed),
            organisation_id: 1,
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
            created_at: "2026-04-20T00:00:00Z".to_string(),
        };

        items.push(patient.clone());
        save_items(PATIENTS_FILE, &items)?;
        Ok(patient)
    }

    fn update(&self, patient_id: u64, payload: UpdatePatientRequest) -> Result<Option<Patient>, String> {
        let mut items = self
            .items
            .lock()
            .map_err(|_| "patient repository lock poisoned".to_string())?;

        let updated = items.iter_mut().find(|p| p.patient_id == patient_id).map(|patient| {
            if let Some(value) = payload.identifiant_interne {
                patient.identifiant_interne = value;
            }
            if let Some(value) = payload.nom {
                patient.nom = value;
            }
            if let Some(value) = payload.prenom {
                patient.prenom = value;
            }
            if let Some(value) = payload.date_naissance {
                patient.date_naissance = Some(value);
            }
            if let Some(value) = payload.numero_securite_sociale {
                patient.numero_securite_sociale = Some(value);
            }
            if let Some(value) = payload.sexe {
                patient.sexe = Some(value);
            }
            if let Some(value) = payload.service {
                patient.service = Some(value);
            }
            if let Some(value) = payload.medecin_referent {
                patient.medecin_referent = Some(value);
            }
            if let Some(value) = payload.remarque {
                patient.remarque = Some(value);
            }
            if let Some(value) = payload.notes {
                patient.notes = Some(value);
            }
            patient.clone()
        });

        if updated.is_some() {
            save_items(PATIENTS_FILE, &items)?;
        }

        Ok(updated)
    }

    fn delete(&self, patient_id: u64) -> Result<bool, String> {
        let mut items = self
            .items
            .lock()
            .map_err(|_| "patient repository lock poisoned".to_string())?;

        let before = items.len();
        items.retain(|p| p.patient_id != patient_id);
        let deleted = items.len() != before;
        if deleted {
            save_items(PATIENTS_FILE, &items)?;
        }
        Ok(deleted)
    }
}
