use std::sync::Arc;
use std::fs;

use crate::repositories::device_repository::SqliteDeviceRepository;
use crate::repositories::patient_repository::SqlitePatientRepository;
use crate::repositories::result_repository::SqliteResultRepository;
use crate::services::auth_service::AuthService;
use crate::services::device_service::DeviceService;
use crate::services::patient_service::PatientService;
use crate::services::result_service::ResultService;

#[derive(Clone)]
pub struct AppState {
    pub auth_service: AuthService,
    pub device_service: DeviceService,
    pub patient_service: PatientService,
    pub result_service: ResultService,
}

impl AppState {
    pub fn new() -> Self {
        // On place la BDD dans le dossier local de l'OS (AppData) pour eviter le hot-reload de Tauri
        let db_path = if let Some(mut path) = dirs::data_local_dir() {
            path.push("NeuralES");
            let _ = fs::create_dir_all(&path);
            path.push("neurales.db");
            path.to_string_lossy().to_string()
        } else {
            "neurales.db".to_string()
        };

        let auth_service = AuthService::new();
        let device_repository = Arc::new(SqliteDeviceRepository::new(&db_path));
        let device_service = DeviceService::new(device_repository);
        let patient_repository = Arc::new(SqlitePatientRepository::new(&db_path));
        let patient_service = PatientService::new(patient_repository);
        let result_repository = Arc::new(SqliteResultRepository::new(&db_path));
        let result_service = ResultService::new(result_repository);

        Self {
            auth_service,
            device_service,
            patient_service,
            result_service,
        }
    }
}
