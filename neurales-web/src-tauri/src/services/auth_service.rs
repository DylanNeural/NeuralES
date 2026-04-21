use std::sync::{Arc, Mutex};

use crate::models::auth::{AuthUser, LoginRequest, LoginResponse};

const DESKTOP_TOKEN: &str = "desktop-local-token";
const DESKTOP_EMAIL: &str = "admin@neurales.com";
const DESKTOP_PASSWORD: &str = "admin123";

#[derive(Clone)]
pub struct AuthService {
    session_user: Arc<Mutex<Option<AuthUser>>>,
}

impl AuthService {
    pub fn new() -> Self {
        Self {
            session_user: Arc::new(Mutex::new(None)),
        }
    }

    pub fn login(&self, payload: LoginRequest) -> Result<LoginResponse, String> {
        if payload.email != DESKTOP_EMAIL || payload.password != DESKTOP_PASSWORD {
            return Err("Identifiants invalides.".to_string());
        }

        let mut guard = self
            .session_user
            .lock()
            .map_err(|_| "auth session lock poisoned".to_string())?;
        *guard = Some(default_user());

        Ok(default_token_response())
    }

    pub fn refresh(&self, token: Option<String>) -> Result<LoginResponse, String> {
        let mut guard = self
            .session_user
            .lock()
            .map_err(|_| "auth session lock poisoned".to_string())?;

        if guard.is_some() {
            return Ok(default_token_response());
        }

        if token.as_deref() == Some(DESKTOP_TOKEN) {
            *guard = Some(default_user());
            return Ok(default_token_response());
        }

        Err("Session locale introuvable.".to_string())
    }

    pub fn me(&self) -> Result<AuthUser, String> {
        let guard = self
            .session_user
            .lock()
            .map_err(|_| "auth session lock poisoned".to_string())?;

        guard
            .clone()
            .ok_or_else(|| "Utilisateur non connecte.".to_string())
    }

    pub fn logout(&self) -> Result<(), String> {
        let mut guard = self
            .session_user
            .lock()
            .map_err(|_| "auth session lock poisoned".to_string())?;
        *guard = None;
        Ok(())
    }
}

fn default_user() -> AuthUser {
    AuthUser {
        user_id: 1,
        prenom: "Admin".to_string(),
        nom: "Local".to_string(),
        email: DESKTOP_EMAIL.to_string(),
        organisation_id: 1,
        role: "admin".to_string(),
    }
}

fn default_token_response() -> LoginResponse {
    LoginResponse {
        access_token: DESKTOP_TOKEN.to_string(),
        token_type: "bearer".to_string(),
    }
}
