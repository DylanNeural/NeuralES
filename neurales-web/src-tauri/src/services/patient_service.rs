use std::sync::Arc;

use crate::models::patient::{CreatePatientRequest, Patient, UpdatePatientRequest};
use crate::repositories::patient_repository::PatientRepository;
use crate::error::AppError;

#[derive(Clone)]
pub struct PatientService {
    repository: Arc<dyn PatientRepository>,
}

impl PatientService {
    pub fn new(repository: Arc<dyn PatientRepository>) -> Self {
        Self { repository }
    }

    pub fn list_patients(&self) -> Result<Vec<Patient>, AppError> {
        self.repository.list()
    }

    pub fn get_patient(&self, patient_id: String) -> Result<Option<Patient>, AppError> {
        self.repository.get_by_id(&patient_id)
    }

    pub fn create_patient(&self, payload: CreatePatientRequest) -> Result<Patient, AppError> {
        if payload.nom.trim().is_empty() { return Err(AppError::BadRequest("Le nom est obligatoire".to_string())); }
        if payload.prenom.trim().is_empty() { return Err(AppError::BadRequest("Le prénom est obligatoire".to_string())); }
        if payload.identifiant_interne.trim().is_empty() { return Err(AppError::BadRequest("L'identifiant interne est obligatoire".to_string())); }

        self.repository.create(payload)
    }

    pub fn update_patient(&self, patient_id: String, payload: UpdatePatientRequest) -> Result<Option<Patient>, AppError> {
        if let Some(ref nom) = payload.nom {
            if nom.trim().is_empty() { return Err(AppError::BadRequest("Le nom est obligatoire".to_string())); }
        }
        if let Some(ref prenom) = payload.prenom {
            if prenom.trim().is_empty() { return Err(AppError::BadRequest("Le prénom est obligatoire".to_string())); }
        }
        if let Some(ref id_interne) = payload.identifiant_interne {
            if id_interne.trim().is_empty() { return Err(AppError::BadRequest("L'identifiant interne est obligatoire".to_string())); }
        }

        self.repository.update(&patient_id, payload)
    }

    pub fn delete_patient(&self, patient_id: String) -> Result<bool, AppError> {
        self.repository.delete(&patient_id)
    }

    pub fn list_services(&self) -> Result<Vec<String>, AppError> {
        let patients = self.repository.list()?;
        let mut items: Vec<String> = patients.into_iter().filter_map(|p| p.service).filter(|s| !s.trim().is_empty()).collect();
        items.sort();
        items.dedup();
        Ok(items)
    }

    pub fn list_medecins(&self) -> Result<Vec<String>, AppError> {
        let patients = self.repository.list()?;
        let mut items: Vec<String> = patients.into_iter().filter_map(|p| p.medecin_referent).filter(|m| !m.trim().is_empty()).collect();
        items.sort();
        items.dedup();
        Ok(items)
    }

    pub fn get_pending(&self) -> Result<Vec<Patient>, AppError> {
        self.repository.get_pending()
    }

    pub fn resolve_sync(&self, local_id: String, remote_id: Option<String>, status: String) -> Result<(), AppError> {
        self.repository.resolve_sync(&local_id, remote_id, &status)
    }
}