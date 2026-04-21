use std::sync::Arc;

use crate::repositories::device_repository::InMemoryDeviceRepository;
use crate::repositories::patient_repository::InMemoryPatientRepository;
use crate::repositories::result_repository::InMemoryResultRepository;
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
        let auth_service = AuthService::new();
        let device_repository = Arc::new(InMemoryDeviceRepository::new());
        let device_service = DeviceService::new(device_repository);
        let patient_repository = Arc::new(InMemoryPatientRepository::new());
        let patient_service = PatientService::new(patient_repository);
        let result_repository = Arc::new(InMemoryResultRepository::new());
        let result_service = ResultService::new(result_repository);

        Self {
            auth_service,
            device_service,
            patient_service,
            result_service,
        }
    }
}
