use serde::{Serialize, Serializer};
use thiserror::Error;

#[derive(Debug, Error)]
pub enum AppError {
    #[error("{0}")]
    BadRequest(String),
    #[error("Ressource introuvable: {0}")]
    NotFound(String),
    #[error("Erreur de base de données: {0}")]
    Database(#[from] rusqlite::Error),
    #[error("Erreur interne: {0}")]
    Internal(String),
}

// On sérialise l'erreur pour le frontend (format JSON similaire à Axios)
impl Serialize for AppError {
    fn serialize<S>(&self, serializer: S) -> Result<S::Ok, S::Error>
    where
        S: Serializer,
    {
        #[derive(Serialize)]
        struct ErrorPayload {
            message: String,
            status: u16,
        }
        let (status, message) = match self {
            AppError::BadRequest(m) => (400, m.clone()),
            AppError::NotFound(m) => (404, m.clone()),
            AppError::Database(e) => (500, e.to_string()),
            AppError::Internal(m) => (500, m.clone()),
        };
        ErrorPayload { message, status }.serialize(serializer)
    }
}