use tauri::State;

use crate::app_state::AppState;
use crate::models::auth::{AuthUser, LoginRequest, LoginResponse};

#[tauri::command]
pub fn desktop_login(state: State<'_, AppState>, payload: LoginRequest) -> Result<LoginResponse, String> {
    state.auth_service.login(payload)
}

#[tauri::command]
pub fn desktop_refresh(state: State<'_, AppState>, token: Option<String>) -> Result<LoginResponse, String> {
    state.auth_service.refresh(token)
}

#[tauri::command]
pub fn desktop_me(state: State<'_, AppState>) -> Result<AuthUser, String> {
    state.auth_service.me()
}

#[tauri::command]
pub fn desktop_logout(state: State<'_, AppState>) -> Result<(), String> {
    state.auth_service.logout()
}
