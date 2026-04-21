use serde::{Deserialize, Serialize};

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct SessionResult {
    pub session_id: u64,
    pub mode: String,
    pub started_at: String,
    pub ended_at: Option<String>,
    pub notes: Option<String>,
    pub app_version: Option<String>,
    pub device_id: Option<u64>,
    pub patient_id: Option<u64>,
    pub organisation_id: u64,
    pub created_by_user_id: Option<u64>,
    pub consent_id: Option<u64>,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct CreateSessionRequest {
    pub mode: String,
    pub started_at: String,
    pub ended_at: Option<String>,
    pub notes: Option<String>,
    pub app_version: Option<String>,
    pub device_id: Option<u64>,
    pub patient_id: Option<u64>,
    pub created_by_user_id: Option<u64>,
    pub consent_id: Option<u64>,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct UpdateSessionRequest {
    pub mode: Option<String>,
    pub started_at: Option<String>,
    pub ended_at: Option<String>,
    pub notes: Option<String>,
    pub app_version: Option<String>,
    pub device_id: Option<u64>,
    pub patient_id: Option<u64>,
    pub created_by_user_id: Option<u64>,
    pub consent_id: Option<u64>,
}
