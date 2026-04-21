use std::sync::Arc;

use crate::models::result_session::{CreateSessionRequest, SessionResult, UpdateSessionRequest};
use crate::repositories::result_repository::ResultRepository;

#[derive(Clone)]
pub struct ResultService {
    repository: Arc<dyn ResultRepository>,
}

impl ResultService {
    pub fn new(repository: Arc<dyn ResultRepository>) -> Self {
        Self { repository }
    }

    pub fn list_sessions(&self) -> Result<Vec<SessionResult>, String> {
        self.repository.list()
    }

    pub fn get_session(&self, session_id: u64) -> Result<Option<SessionResult>, String> {
        self.repository.get_by_id(session_id)
    }

    pub fn create_session(&self, payload: CreateSessionRequest) -> Result<SessionResult, String> {
        if payload.mode.trim().is_empty() {
            return Err("mode is required".to_string());
        }
        if payload.started_at.trim().is_empty() {
            return Err("started_at is required".to_string());
        }

        self.repository.create(payload)
    }

    pub fn update_session(&self, session_id: u64, payload: UpdateSessionRequest) -> Result<Option<SessionResult>, String> {
        if let Some(ref mode) = payload.mode {
            if mode.trim().is_empty() {
                return Err("mode is required".to_string());
            }
        }
        if let Some(ref started_at) = payload.started_at {
            if started_at.trim().is_empty() {
                return Err("started_at is required".to_string());
            }
        }

        self.repository.update(session_id, payload)
    }

    pub fn delete_session(&self, session_id: u64) -> Result<bool, String> {
        self.repository.delete(session_id)
    }
}
