// Arc (Atomic Reference Counted) permet de partager la meme instance
// du repository entre plusieurs owners de facon thread-safe.
use std::sync::Arc;

// Types metier utilises dans la couche service.
use crate::models::device::{CreateDeviceRequest, Device, UpdateDeviceRequest};
// Le service depend d'un trait (abstraction), pas d'une implementation concrete.
use crate::repositories::device_repository::DeviceRepository;
use crate::error::AppError;

// Clone est derive pour pouvoir dupliquer legerement le service
// (la copie partage le meme Arc interne, pas une duplication lourde).
#[derive(Clone)]
pub struct DeviceService {
    // Dependance principale: acces CRUD aux devices.
    // dyn DeviceRepository = dispatch dynamique sur le trait.
    repository: Arc<dyn DeviceRepository>,
}

impl DeviceService {
    // Constructeur simple avec injection de dependance.
    // Cette approche facilite les tests (mock repository possible).
    pub fn new(repository: Arc<dyn DeviceRepository>) -> Self {
        Self { repository }
    }

    // Liste tous les dispositifs.
    // Le service ne transforme pas ici: il relaie le repository.
    pub fn list_devices(&self) -> Result<Vec<Device>, AppError> {
        self.repository.list()
    }

    // Recupere un dispositif par id.
    // Option<Device> signifie:
    // - Some(device): trouve
    // - None: id inexistant
    pub fn get_device(&self, device_id: String) -> Result<Option<Device>, AppError> {
        self.repository.get_by_id(&device_id)
    }

    // Cree un dispositif avec validations metier minimales.
    // Ici le service protege la couche repository contre les valeurs vides.
    pub fn create_device(&self, payload: CreateDeviceRequest) -> Result<Device, AppError> {
        // trim() retire les espaces en debut/fin.
        // On evite ainsi qu'une chaine "   " passe la validation.
        if payload.marque_modele.trim().is_empty() {
            return Err(AppError::BadRequest("marque_modele is required".to_string()));
        }
        if payload.connection_type.trim().is_empty() {
            return Err(AppError::BadRequest("connection_type is required".to_string()));
        }
        if payload.etat.trim().is_empty() {
            return Err(AppError::BadRequest("etat is required".to_string()));
        }

        // Si la validation passe, on delegue la creation effective au repository.
        self.repository.create(payload)
    }

    // Met a jour un dispositif existant.
    // Le payload est partiel (Option sur chaque champ), donc on valide
    // uniquement les champs presents.
    pub fn update_device(&self, device_id: String, payload: UpdateDeviceRequest) -> Result<Option<Device>, AppError> {
        // if let Some(...) => validation conditionnelle seulement si champ fourni.
        if let Some(ref marque_modele) = payload.marque_modele {
            if marque_modele.trim().is_empty() {
                return Err(AppError::BadRequest("marque_modele is required".to_string()));
            }
        }
        if let Some(ref connection_type) = payload.connection_type {
            if connection_type.trim().is_empty() {
                return Err(AppError::BadRequest("connection_type is required".to_string()));
            }
        }
        if let Some(ref etat) = payload.etat {
            if etat.trim().is_empty() {
                return Err(AppError::BadRequest("etat is required".to_string()));
            }
        }

        // Le repository applique la modification et persiste le JSON.
        self.repository.update(&device_id, payload)
    }

    // Supprime un dispositif par id.
    // bool:
    // - true  => un element supprime
    // - false => rien a supprimer (id absent)
    pub fn delete_device(&self, device_id: String) -> Result<bool, AppError> {
        self.repository.delete(&device_id)
    }

    pub fn get_pending(&self) -> Result<Vec<Device>, AppError> {
        self.repository.get_pending()
    }

    pub fn resolve_sync(&self, local_id: String, remote_id: Option<String>, status: String) -> Result<(), AppError> {
        self.repository.resolve_sync(&local_id, remote_id, &status)
    }
}
