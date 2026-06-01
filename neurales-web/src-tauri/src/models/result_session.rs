use serde::{Deserialize, Serialize};

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct SessionResult {
    pub session_id: String,
    pub mode: String,
    pub started_at: String,
    pub ended_at: Option<String>,
    pub notes: Option<String>,
    pub app_version: Option<String>,
    pub device_id: Option<String>,
    pub patient_id: Option<String>,
    pub organisation_id: u64,
    pub created_by_user_id: Option<u64>,
    pub consent_id: Option<u64>,
    pub sync_status: String,
    pub remote_id: Option<String>,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct CreateSessionRequest {
    pub mode: String,
    pub started_at: String,
    pub ended_at: Option<String>,
    pub notes: Option<String>,
    pub app_version: Option<String>,
    pub device_id: Option<String>,
    pub patient_id: Option<String>,
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
    pub device_id: Option<String>,
    pub patient_id: Option<String>,
    pub created_by_user_id: Option<u64>,
    pub consent_id: Option<u64>,
}
