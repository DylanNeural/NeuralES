use std::sync::Arc;

use crate::models::patient::{CreatePatientRequest, Patient, UpdatePatientRequest};
use crate::repositories::patient_repository::PatientRepository;

#[derive(Clone)]
pub struct PatientService {
    repository: Arc<dyn PatientRepository>,
}

impl PatientService {
    pub fn new(repository: Arc<dyn PatientRepository>) -> Self {
        Self { repository }
    }

    pub fn list_patients(&self) -> Result<Vec<Patient>, String> {
        self.repository.list()
    }

    pub fn get_patient(&self, patient_id: u64) -> Result<Option<Patient>, String> {
        self.repository.get_by_id(patient_id)
    }

    pub fn create_patient(&self, payload: CreatePatientRequest) -> Result<Patient, String> {
        if payload.identifiant_interne.trim().is_empty() {
            return Err("identifiant_interne is required".to_string());
        }
        if payload.nom.trim().is_empty() {
            return Err("nom is required".to_string());
        }
        if payload.prenom.trim().is_empty() {
            return Err("prenom is required".to_string());
        }

        self.repository.create(payload)
    }

    pub fn update_patient(
        &self,
        patient_id: u64,
        payload: UpdatePatientRequest,
    ) -> Result<Option<Patient>, String> {
        if let Some(ref identifiant_interne) = payload.identifiant_interne {
            if identifiant_interne.trim().is_empty() {
                return Err("identifiant_interne is required".to_string());
            }
        }
        if let Some(ref nom) = payload.nom {
            if nom.trim().is_empty() {
                return Err("nom is required".to_string());
            }
        }
        if let Some(ref prenom) = payload.prenom {
            if prenom.trim().is_empty() {
                return Err("prenom is required".to_string());
            }
        }

        self.repository.update(patient_id, payload)
    }

    pub fn delete_patient(&self, patient_id: u64) -> Result<bool, String> {
        self.repository.delete(patient_id)
    }

    pub fn list_services(&self) -> Vec<String> {
        vec![
            "Neurologie".to_string(),
            "Sommeil".to_string(),
            "Réanimation".to_string(),
            "Exploration fonctionnelle".to_string(),
        ]
    }

    pub fn list_medecins(&self) -> Vec<String> {
        vec![
            "Dr Martin".to_string(),
            "Dr Dupont".to_string(),
            "Dr Bernard".to_string(),
            "Dr Leroy".to_string(),
        ]
    }
}
