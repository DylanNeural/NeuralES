use tauri::State;

use crate::app_state::AppState;
use crate::models::patient::{CreatePatientRequest, Patient, UpdatePatientRequest};
use crate::error::AppError;

#[tauri::command]
pub fn list_patients(state: State<'_, AppState>) -> Result<Vec<Patient>, AppError> {
    state.patient_service.list_patients()
}

#[tauri::command]
pub fn get_patient_by_id(state: State<'_, AppState>, patient_id: String) -> Result<Option<Patient>, AppError> {
    state.patient_service.get_patient(patient_id)
}

#[tauri::command]
pub fn create_patient(
    state: State<'_, AppState>,
    payload: CreatePatientRequest,
) -> Result<Patient, AppError> {
    state.patient_service.create_patient(payload)
}

#[tauri::command]
pub fn update_patient(
    state: State<'_, AppState>,
    patient_id: String,
    payload: UpdatePatientRequest,
) -> Result<Option<Patient>, AppError> {
    state.patient_service.update_patient(patient_id, payload)
}

#[tauri::command]
pub fn delete_patient(state: State<'_, AppState>, patient_id: String) -> Result<bool, AppError> {
    state.patient_service.delete_patient(patient_id)
}

#[tauri::command]
pub fn list_services(state: State<'_, AppState>) -> Result<Vec<String>, AppError> {
    state.patient_service.list_services()
}

#[tauri::command]
pub fn list_medecins(state: State<'_, AppState>) -> Result<Vec<String>, AppError> {
    state.patient_service.list_medecins()
}

#[tauri::command]
pub fn get_pending_patients(state: State<'_, AppState>) -> Result<Vec<Patient>, AppError> {
    state.patient_service.get_pending()
}

#[tauri::command]
pub fn resolve_patient_sync(
    state: State<'_, AppState>,
    local_id: String,
    remote_id: Option<String>,
    status: String,
) -> Result<(), AppError> {
    state.patient_service.resolve_sync(local_id, remote_id, status)
}