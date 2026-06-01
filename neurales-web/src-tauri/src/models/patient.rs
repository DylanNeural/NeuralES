use serde::{Deserialize, Serialize};

#[derive(Debug, Serialize, Deserialize, Clone)]
pub struct Patient {
    pub patient_id: String,
    pub identifiant_interne: String,
    pub nom: String,
    pub prenom: String,
    pub date_naissance: Option<String>,
    pub numero_securite_sociale: Option<String>,
    pub sexe: Option<String>,
    pub service: Option<String>,
    pub medecin_referent: Option<String>,
    pub remarque: Option<String>,
    pub notes: Option<String>,
    pub organisation_id: u64,
    pub sync_status: String,
    pub remote_id: Option<String>,
}

#[derive(Debug, Deserialize)]
pub struct CreatePatientRequest {
    pub identifiant_interne: String,
    pub nom: String,
    pub prenom: String,
    pub date_naissance: Option<String>,
    pub numero_securite_sociale: Option<String>,
    pub sexe: Option<String>,
    pub service: Option<String>,
    pub medecin_referent: Option<String>,
    pub remarque: Option<String>,
    pub notes: Option<String>,
}

// Tous les champs sont optionnels pour permettre des mises à jour partielles (PATCH)
#[derive(Debug, Deserialize)]
pub struct UpdatePatientRequest {
    pub identifiant_interne: Option<String>,
    pub nom: Option<String>,
    pub prenom: Option<String>,
    pub date_naissance: Option<String>,
    pub numero_securite_sociale: Option<String>,
    pub sexe: Option<String>,
    pub service: Option<String>,
    pub medecin_referent: Option<String>,
    pub remarque: Option<String>,
    pub notes: Option<String>,
}