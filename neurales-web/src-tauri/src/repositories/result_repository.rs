use std::sync::atomic::{AtomicU64, Ordering};
use std::sync::Mutex;

use crate::models::result_session::{CreateSessionRequest, SessionResult, UpdateSessionRequest};
use crate::storage::json_store::{load_items, save_items};

const RESULTS_FILE: &str = "results.json";

pub trait ResultRepository: Send + Sync {
    fn list(&self) -> Result<Vec<SessionResult>, String>;
    fn get_by_id(&self, session_id: u64) -> Result<Option<SessionResult>, String>;
    fn create(&self, payload: CreateSessionRequest) -> Result<SessionResult, String>;
    fn update(&self, session_id: u64, payload: UpdateSessionRequest) -> Result<Option<SessionResult>, String>;
    fn delete(&self, session_id: u64) -> Result<bool, String>;
}

pub struct InMemoryResultRepository {
    next_id: AtomicU64,
    items: Mutex<Vec<SessionResult>>,
}

impl InMemoryResultRepository {
    pub fn new() -> Self {
        let items = load_items::<SessionResult>(RESULTS_FILE).unwrap_or_default();
        let next_id = items.iter().map(|item| item.session_id).max().unwrap_or(0) + 1;

        Self {
            next_id: AtomicU64::new(next_id),
            items: Mutex::new(items),
        }
    }
}

impl ResultRepository for InMemoryResultRepository {
    fn list(&self) -> Result<Vec<SessionResult>, String> {
        let items = self
            .items
            .lock()
            .map_err(|_| "results repository lock poisoned".to_string())?;
        Ok(items.clone())
    }

    fn get_by_id(&self, session_id: u64) -> Result<Option<SessionResult>, String> {
        let items = self
            .items
            .lock()
            .map_err(|_| "results repository lock poisoned".to_string())?;
        Ok(items.iter().find(|s| s.session_id == session_id).cloned())
    }

    fn create(&self, payload: CreateSessionRequest) -> Result<SessionResult, String> {
        let mut items = self
            .items
            .lock()
            .map_err(|_| "results repository lock poisoned".to_string())?;

        let session = SessionResult {
            session_id: self.next_id.fetch_add(1, Ordering::Relaxed),
            mode: payload.mode,
            started_at: payload.started_at,
            ended_at: payload.ended_at,
            notes: payload.notes,
            app_version: payload.app_version,
            device_id: payload.device_id,
            patient_id: payload.patient_id,
            organisation_id: 1,
            created_by_user_id: payload.created_by_user_id.or(Some(1)),
            consent_id: payload.consent_id,
        };

        items.push(session.clone());
        save_items(RESULTS_FILE, &items)?;
        Ok(session)
    }

    fn update(&self, session_id: u64, payload: UpdateSessionRequest) -> Result<Option<SessionResult>, String> {
        let mut items = self
            .items
            .lock()
            .map_err(|_| "results repository lock poisoned".to_string())?;

        let updated = items.iter_mut().find(|s| s.session_id == session_id).map(|session| {
            if let Some(value) = payload.mode {
                session.mode = value;
            }
            if let Some(value) = payload.started_at {
                session.started_at = value;
            }
            if let Some(value) = payload.ended_at {
                session.ended_at = Some(value);
            }
            if let Some(value) = payload.notes {
                session.notes = Some(value);
            }
            if let Some(value) = payload.app_version {
                session.app_version = Some(value);
            }
            if let Some(value) = payload.device_id {
                session.device_id = Some(value);
            }
            if let Some(value) = payload.patient_id {
                session.patient_id = Some(value);
            }
            if let Some(value) = payload.created_by_user_id {
                session.created_by_user_id = Some(value);
            }
            if let Some(value) = payload.consent_id {
                session.consent_id = Some(value);
            }
            session.clone()
        });

        if updated.is_some() {
            save_items(RESULTS_FILE, &items)?;
        }

        Ok(updated)
    }

    fn delete(&self, session_id: u64) -> Result<bool, String> {
        let mut items = self
            .items
            .lock()
            .map_err(|_| "results repository lock poisoned".to_string())?;

        let before = items.len();
        items.retain(|s| s.session_id != session_id);
        let deleted = items.len() != before;
        if deleted {
            save_items(RESULTS_FILE, &items)?;
        }
        Ok(deleted)
    }
}
