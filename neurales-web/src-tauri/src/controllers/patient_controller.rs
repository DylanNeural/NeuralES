use tauri::State;

use crate::app_state::AppState;
use crate::models::patient::{CreatePatientRequest, Patient, UpdatePatientRequest};

#[tauri::command]
pub fn list_patients(state: State<'_, AppState>) -> Result<Vec<Patient>, String> {
    state.patient_service.list_patients()
}

#[tauri::command]
pub fn get_patient_by_id(state: State<'_, AppState>, patient_id: u64) -> Result<Option<Patient>, String> {
    state.patient_service.get_patient(patient_id)
}

#[tauri::command]
pub fn create_patient(
    state: State<'_, AppState>,
    payload: CreatePatientRequest,
) -> Result<Patient, String> {
    state.patient_service.create_patient(payload)
}

#[tauri::command]
pub fn update_patient(
    state: State<'_, AppState>,
    patient_id: u64,
    payload: UpdatePatientRequest,
) -> Result<Option<Patient>, String> {
    state.patient_service.update_patient(patient_id, payload)
}

#[tauri::command]
pub fn delete_patient(state: State<'_, AppState>, patient_id: u64) -> Result<bool, String> {
    state.patient_service.delete_patient(patient_id)
}

#[tauri::command]
pub fn list_services(state: State<'_, AppState>) -> Vec<String> {
    state.patient_service.list_services()
}

#[tauri::command]
pub fn list_medecins(state: State<'_, AppState>) -> Vec<String> {
    state.patient_service.list_medecins()
}
