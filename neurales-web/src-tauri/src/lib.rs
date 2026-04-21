mod app_state;
mod controllers;
mod models;
mod repositories;
mod services;
mod storage;

use controllers::auth_controller::{desktop_login, desktop_logout, desktop_me, desktop_refresh};
use controllers::device_controller::{
    create_device, delete_device, get_device_by_id, list_devices, update_device,
};
use controllers::patient_controller::{
    create_patient, delete_patient, get_patient_by_id, list_medecins, list_patients,
    list_services, update_patient,
};
use controllers::result_controller::{
    create_session, delete_session, get_session_by_id, list_sessions, update_session,
};

#[cfg_attr(mobile, tauri::mobile_entry_point)]
pub fn run() {
    tauri::Builder::default()
        .manage(app_state::AppState::new())
        .invoke_handler(tauri::generate_handler![
            desktop_login,
            desktop_refresh,
            desktop_me,
            desktop_logout,
            list_devices,
            get_device_by_id,
            create_device,
            update_device,
            delete_device,
            list_patients,
            get_patient_by_id,
            create_patient,
            update_patient,
            delete_patient,
            list_services,
            list_medecins,
            list_sessions,
            get_session_by_id,
            create_session,
            update_session,
            delete_session
        ])
        .run(tauri::generate_context!())
        .expect("error while running tauri application");
}
