use tauri::State;

use crate::app_state::AppState;
use crate::models::device::{CreateDeviceRequest, Device, UpdateDeviceRequest};

#[tauri::command]
pub fn list_devices(state: State<'_, AppState>) -> Result<Vec<Device>, String> {
    state.device_service.list_devices()
}

#[tauri::command]
pub fn get_device_by_id(state: State<'_, AppState>, device_id: u64) -> Result<Option<Device>, String> {
    state.device_service.get_device(device_id)
}

#[tauri::command]
pub fn create_device(
    state: State<'_, AppState>,
    payload: CreateDeviceRequest,
) -> Result<Device, String> {
    state.device_service.create_device(payload)
}

#[tauri::command]
pub fn update_device(
    state: State<'_, AppState>,
    device_id: u64,
    payload: UpdateDeviceRequest,
) -> Result<Option<Device>, String> {
    state.device_service.update_device(device_id, payload)
}

#[tauri::command]
pub fn delete_device(state: State<'_, AppState>, device_id: u64) -> Result<bool, String> {
    state.device_service.delete_device(device_id)
}
