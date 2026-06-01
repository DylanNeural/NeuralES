use tauri::State;

use crate::app_state::AppState;
use crate::models::result_session::{CreateSessionRequest, SessionResult, UpdateSessionRequest};
use crate::error::AppError;

#[tauri::command]
pub fn list_sessions(state: State<'_, AppState>) -> Result<Vec<SessionResult>, AppError> {
    state.result_service.list_sessions()
}

#[tauri::command]
pub fn get_session_by_id(state: State<'_, AppState>, session_id: String) -> Result<Option<SessionResult>, AppError> {
    state.result_service.get_session(session_id)
}

#[tauri::command]
pub fn create_session(
    state: State<'_, AppState>,
    payload: CreateSessionRequest,
) -> Result<SessionResult, AppError> {
    state.result_service.create_session(payload)
}

#[tauri::command]
pub fn update_session(
    state: State<'_, AppState>,
    session_id: String,
    payload: UpdateSessionRequest,
) -> Result<Option<SessionResult>, AppError> {
    state.result_service.update_session(session_id, payload)
}

#[tauri::command]
pub fn delete_session(state: State<'_, AppState>, session_id: String) -> Result<bool, AppError> {
    state.result_service.delete_session(session_id)
}

#[tauri::command]
pub fn get_pending_sessions(state: State<'_, AppState>) -> Result<Vec<SessionResult>, AppError> {
    state.result_service.get_pending()
}

#[tauri::command]
pub fn resolve_session_sync(
    state: State<'_, AppState>,
    local_id: String,
    remote_id: Option<String>,
    status: String,
) -> Result<(), AppError> {
    state.result_service.resolve_sync(local_id, remote_id, status)
}
