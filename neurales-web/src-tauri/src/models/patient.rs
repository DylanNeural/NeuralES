use serde::{Deserialize, Serialize};

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct Patient {
    pub patient_id: u64,
    pub organisation_id: u64,
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
    pub created_at: String,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
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

#[derive(Debug, Clone, Serialize, Deserialize)]
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
