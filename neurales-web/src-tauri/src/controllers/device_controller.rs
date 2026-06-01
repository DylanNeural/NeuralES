// "State" est fourni par Tauri: il permet d'acceder a un etat global partage
// (services, configuration, etc.) sans recreer ces objets a chaque appel.
use tauri::State;

// AppState contient les services instancies au demarrage de l'application.
// Ici on utilisera state.device_service.
use crate::app_state::AppState;
// Types metier utilises par les commandes:
// - Device: structure complete renvoyee au frontend
// - CreateDeviceRequest: donnees attendues pour creer
// - UpdateDeviceRequest: donnees partielles pour modifier
use crate::models::device::{CreateDeviceRequest, Device, UpdateDeviceRequest};
use crate::error::AppError;

// #[tauri::command] expose cette fonction au frontend via invoke("list_devices").
// Signature:
// - entree: State (acces aux services)
// - sortie: Result<Vec<Device>, String>
//   Ok(...)  => succes, la liste des dispositifs
//   Err(...) => message d'erreur a remonter au frontend
#[tauri::command]
pub fn list_devices(state: State<'_, AppState>) -> Result<Vec<Device>, AppError> {
    // Le controller delegue la logique au service.
    // Le service appelle ensuite le repository (JSON).
    state.device_service.list_devices()
}

// Expose invoke("get_device_by_id", { deviceId: ... }) cote frontend.
// Note importante: Tauri mappe l'argument JS deviceId vers le parametre Rust device_id.
#[tauri::command]
pub fn get_device_by_id(state: State<'_, AppState>, device_id: String) -> Result<Option<Device>, AppError> {
    // Option<Device>:
    // - Some(device): trouve
    // - None: non trouve (ce n'est pas forcement une erreur technique)
    state.device_service.get_device(device_id)
}

// Expose invoke("create_device", { payload: {...} }).
// payload est deserialise automatiquement en CreateDeviceRequest.
// Si un champ obligatoire manque ou est invalide, le service renvoie Err(String).
#[tauri::command]
pub fn create_device(
    state: State<'_, AppState>,
    payload: CreateDeviceRequest,
) -> Result<Device, AppError> {
    // Retourne l'objet cree avec son identifiant, pour mise a jour immediate de l'UI.
    state.device_service.create_device(payload)
}

// Expose invoke("update_device", { deviceId: ..., payload: {...} }).
// Retourne Option<Device> car l'id peut ne pas exister.
#[tauri::command]
pub fn update_device(
    state: State<'_, AppState>,
    device_id: String,
    payload: UpdateDeviceRequest,
) -> Result<Option<Device>, AppError> {
    // Validation et persistance sont faites dans le service/repository.
    state.device_service.update_device(device_id, payload)
}

// Expose invoke("delete_device", { deviceId: ... }).
// Retourne bool:
// - true  => suppression reussie
// - false => aucun element correspondant
#[tauri::command]
pub fn delete_device(state: State<'_, AppState>, device_id: String) -> Result<bool, AppError> {
    state.device_service.delete_device(device_id)
}

#[tauri::command]
pub fn get_pending_devices(state: State<'_, AppState>) -> Result<Vec<Device>, AppError> {
    state.device_service.get_pending()
}

#[tauri::command]
pub fn resolve_device_sync(
    state: State<'_, AppState>,
    local_id: String,
    remote_id: Option<String>,
    status: String,
) -> Result<(), AppError> {
    state.device_service.resolve_sync(local_id, remote_id, status)
}
