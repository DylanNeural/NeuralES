use std::sync::Arc;

use crate::models::result_session::{CreateSessionRequest, SessionResult, UpdateSessionRequest};
use crate::repositories::result_repository::ResultRepository;
use crate::error::AppError;

#[derive(Clone)]
pub struct ResultService {
    repository: Arc<dyn ResultRepository>,
}

impl ResultService {
    pub fn new(repository: Arc<dyn ResultRepository>) -> Self {
        Self { repository }
    }

    pub fn list_sessions(&self) -> Result<Vec<SessionResult>, AppError> {
        self.repository.list()
    }

    pub fn get_session(&self, session_id: String) -> Result<Option<SessionResult>, AppError> {
        self.repository.get_by_id(&session_id)
    }

    pub fn create_session(&self, payload: CreateSessionRequest) -> Result<SessionResult, AppError> {
        if payload.mode.trim().is_empty() {
            return Err(AppError::BadRequest("mode is required".to_string()));
        }
        if payload.started_at.trim().is_empty() {
            return Err(AppError::BadRequest("started_at is required".to_string()));
        }

        self.repository.create(payload)
    }

    pub fn update_session(&self, session_id: String, payload: UpdateSessionRequest) -> Result<Option<SessionResult>, AppError> {
        if let Some(ref mode) = payload.mode {
            if mode.trim().is_empty() {
                return Err(AppError::BadRequest("mode is required".to_string()));
            }
        }
        if let Some(ref started_at) = payload.started_at {
            if started_at.trim().is_empty() {
                return Err(AppError::BadRequest("started_at is required".to_string()));
            }
        }

        self.repository.update(&session_id, payload)
    }

    pub fn delete_session(&self, session_id: String) -> Result<bool, AppError> {
        self.repository.delete(&session_id)
    }

    pub fn get_pending(&self) -> Result<Vec<SessionResult>, AppError> {
        self.repository.get_pending()
    }

    pub fn resolve_sync(&self, local_id: String, remote_id: Option<String>, status: String) -> Result<(), AppError> {
        self.repository.resolve_sync(&local_id, remote_id, &status)
    }
}
