mod app_state;
mod controllers;
mod models;
mod repositories;
mod services;
pub mod error;

use controllers::auth_controller::{desktop_login, desktop_logout, desktop_me, desktop_refresh};
use controllers::device_controller::{
    create_device, delete_device, get_device_by_id, list_devices, update_device,
    get_pending_devices, resolve_device_sync,
};
use controllers::patient_controller::{
    create_patient, delete_patient, get_patient_by_id, list_medecins, list_patients,
    list_services, update_patient,
    get_pending_patients, resolve_patient_sync,
};
use controllers::result_controller::{
    create_session, delete_session, get_session_by_id, list_sessions, update_session,
    get_pending_sessions, resolve_session_sync,
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
            get_pending_devices,
            resolve_device_sync,
            list_patients,
            get_patient_by_id,
            create_patient,
            update_patient,
            delete_patient,
            list_services,
            list_medecins,
            get_pending_patients,
            resolve_patient_sync,
            list_sessions,
            get_session_by_id,
            create_session,
            update_session,
            delete_session,
            get_pending_sessions,
            resolve_session_sync
        ])
        .run(tauri::generate_context!())
        .expect("error while running tauri application");
}
