use tauri::State;

use crate::app_state::AppState;
use crate::models::result_session::{CreateSessionRequest, SessionResult, UpdateSessionRequest};

#[tauri::command]
pub fn list_sessions(state: State<'_, AppState>) -> Result<Vec<SessionResult>, String> {
    state.result_service.list_sessions()
}

#[tauri::command]
pub fn get_session_by_id(state: State<'_, AppState>, session_id: u64) -> Result<Option<SessionResult>, String> {
    state.result_service.get_session(session_id)
}

#[tauri::command]
pub fn create_session(
    state: State<'_, AppState>,
    payload: CreateSessionRequest,
) -> Result<SessionResult, String> {
    state.result_service.create_session(payload)
}

#[tauri::command]
pub fn update_session(
    state: State<'_, AppState>,
    session_id: u64,
    payload: UpdateSessionRequest,
) -> Result<Option<SessionResult>, String> {
    state.result_service.update_session(session_id, payload)
}

#[tauri::command]
pub fn delete_session(state: State<'_, AppState>, session_id: u64) -> Result<bool, String> {
    state.result_service.delete_session(session_id)
}
