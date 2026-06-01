use serde::{Deserialize, Serialize};

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct Device {
    pub device_id: String,
    pub organisation_id: u64,
    pub marque_modele: String,
    pub serial_number: Option<String>,
    pub connection_type: String,
    pub etat: String,
    pub sync_status: String,
    pub remote_id: Option<String>,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct CreateDeviceRequest {
    pub marque_modele: String,
    pub serial_number: Option<String>,
    pub connection_type: String,
    pub etat: String,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct UpdateDeviceRequest {
    pub marque_modele: Option<String>,
    pub serial_number: Option<String>,
    pub connection_type: Option<String>,
    pub etat: Option<String>,
}
