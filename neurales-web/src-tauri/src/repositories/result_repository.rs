use std::sync::Mutex;
use rusqlite::{params, Connection};

use crate::models::result_session::{CreateSessionRequest, SessionResult, UpdateSessionRequest};
use crate::error::AppError;

pub trait ResultRepository: Send + Sync {
    fn list(&self) -> Result<Vec<SessionResult>, AppError>;
    fn get_by_id(&self, session_id: &str) -> Result<Option<SessionResult>, AppError>;
    fn create(&self, payload: CreateSessionRequest) -> Result<SessionResult, AppError>;
    fn update(&self, session_id: &str, payload: UpdateSessionRequest) -> Result<Option<SessionResult>, AppError>;
    fn delete(&self, session_id: &str) -> Result<bool, AppError>;
    fn get_pending(&self) -> Result<Vec<SessionResult>, AppError>;
    fn resolve_sync(&self, local_id: &str, remote_id: Option<String>, status: &str) -> Result<(), AppError>;
}

pub struct SqliteResultRepository {
    conn: Mutex<Connection>,
}

impl SqliteResultRepository {
    pub fn new(db_path: &str) -> Self {
        let conn = Connection::open(db_path).expect("Impossible d'ouvrir la base de données SQLite");
        
        conn.execute(
            "CREATE TABLE IF NOT EXISTS results (
                session_id TEXT PRIMARY KEY,
                mode TEXT NOT NULL,
                started_at TEXT NOT NULL,
                ended_at TEXT,
                notes TEXT,
                app_version TEXT,
                device_id TEXT,
                patient_id TEXT,
                organisation_id INTEGER NOT NULL,
                created_by_user_id INTEGER,
                consent_id INTEGER,
                sync_status TEXT NOT NULL DEFAULT 'pending_insert',
                remote_id TEXT
            )",
            [],
        ).expect("Impossible de créer la table results");

        Self {
            conn: Mutex::new(conn),
        }
    }
}

impl ResultRepository for SqliteResultRepository {
    fn list(&self) -> Result<Vec<SessionResult>, AppError> {
        let conn = self.conn.lock().map_err(|_| AppError::Internal("lock poisoned".into()))?;
        let mut stmt = conn.prepare("SELECT session_id, mode, started_at, ended_at, notes, app_version, device_id, patient_id, organisation_id, created_by_user_id, consent_id, sync_status, remote_id FROM results WHERE sync_status != 'pending_delete'")?;
        
        let iter = stmt.query_map([], |row| {
            Ok(SessionResult {
                session_id: row.get(0)?,
                mode: row.get(1)?,
                started_at: row.get(2)?,
                ended_at: row.get(3)?,
                notes: row.get(4)?,
                app_version: row.get(5)?,
                device_id: row.get(6)?,
                patient_id: row.get(7)?,
                organisation_id: row.get::<_, i64>(8)? as u64,
                created_by_user_id: row.get::<_, Option<i64>>(9)?.map(|v| v as u64),
                consent_id: row.get::<_, Option<i64>>(10)?.map(|v| v as u64),
                sync_status: row.get(11)?,
                remote_id: row.get(12)?,
            })
        })?;

        let mut items = Vec::new();
        for item in iter {
            items.push(item?);
        }
        Ok(items)
    }

    fn get_by_id(&self, session_id: &str) -> Result<Option<SessionResult>, AppError> {
        let conn = self.conn.lock().map_err(|_| AppError::Internal("lock poisoned".into()))?;
        let mut stmt = conn.prepare("SELECT session_id, mode, started_at, ended_at, notes, app_version, device_id, patient_id, organisation_id, created_by_user_id, consent_id, sync_status, remote_id FROM results WHERE session_id = ?1 AND sync_status != 'pending_delete'")?;
        
        let mut iter = stmt.query_map(params![session_id], |row| {
            Ok(SessionResult {
                session_id: row.get(0)?,
                mode: row.get(1)?,
                started_at: row.get(2)?,
                ended_at: row.get(3)?,
                notes: row.get(4)?,
                app_version: row.get(5)?,
                device_id: row.get(6)?,
                patient_id: row.get(7)?,
                organisation_id: row.get::<_, i64>(8)? as u64,
                created_by_user_id: row.get::<_, Option<i64>>(9)?.map(|v| v as u64),
                consent_id: row.get::<_, Option<i64>>(10)?.map(|v| v as u64),
                sync_status: row.get(11)?,
                remote_id: row.get(12)?,
            })
        })?;

        if let Some(item) = iter.next() {
            Ok(Some(item?))
        } else {
            Ok(None)
        }
    }

    fn create(&self, payload: CreateSessionRequest) -> Result<SessionResult, AppError> {
        let conn = self.conn.lock().map_err(|_| AppError::Internal("lock poisoned".into()))?;
        let organisation_id: i64 = 1;
        let created_by_user_id = payload.created_by_user_id.or(Some(1));
        let session_id = uuid::Uuid::new_v4().to_string();

        conn.execute(
            "INSERT INTO results (session_id, mode, started_at, ended_at, notes, app_version, device_id, patient_id, organisation_id, created_by_user_id, consent_id, sync_status, remote_id) VALUES (?1, ?2, ?3, ?4, ?5, ?6, ?7, ?8, ?9, ?10, ?11, ?12, ?13)",
            params![
                session_id, payload.mode, payload.started_at, payload.ended_at, payload.notes,
                payload.app_version, payload.device_id, payload.patient_id,
                organisation_id, created_by_user_id.map(|v| v as i64), payload.consent_id.map(|v| v as i64), "pending_insert", None::<String>
            ],
        )?;

        Ok(SessionResult {
            session_id,
            mode: payload.mode,
            started_at: payload.started_at,
            ended_at: payload.ended_at,
            notes: payload.notes,
            app_version: payload.app_version,
            device_id: payload.device_id,
            patient_id: payload.patient_id,
            organisation_id: organisation_id as u64,
            created_by_user_id,
            consent_id: payload.consent_id,
            sync_status: "pending_insert".to_string(),
            remote_id: None,
        })
    }

    fn update(&self, session_id: &str, payload: UpdateSessionRequest) -> Result<Option<SessionResult>, AppError> {
        let mut session = match self.get_by_id(session_id)? {
            Some(s) => s,
            None => return Ok(None),
        };

        if let Some(val) = payload.mode { session.mode = val; }
        if let Some(val) = payload.started_at { session.started_at = val; }
        if let Some(val) = payload.ended_at { session.ended_at = Some(val); }
        if let Some(val) = payload.notes { session.notes = Some(val); }
        if let Some(val) = payload.app_version { session.app_version = Some(val); }
        if let Some(val) = payload.device_id { session.device_id = Some(val); }
        if let Some(val) = payload.patient_id { session.patient_id = Some(val); }
        if let Some(val) = payload.created_by_user_id { session.created_by_user_id = Some(val); }
        if let Some(val) = payload.consent_id { session.consent_id = Some(val); }

        if session.sync_status != "pending_insert" {
            session.sync_status = "pending_update".to_string();
        }

        let conn = self.conn.lock().map_err(|_| AppError::Internal("lock poisoned".into()))?;
        conn.execute(
            "UPDATE results SET
                mode = ?1, started_at = ?2, ended_at = ?3, notes = ?4,
                app_version = ?5, device_id = ?6, patient_id = ?7, created_by_user_id = ?8,
                consent_id = ?9, sync_status = ?10
            WHERE session_id = ?11",
            params![
                session.mode, session.started_at, session.ended_at, session.notes,
                session.app_version, session.device_id, session.patient_id,
                session.created_by_user_id.map(|v| v as i64), session.consent_id.map(|v| v as i64),
                session.sync_status, session_id
            ],
        )?;

        Ok(Some(session))
    }

    fn delete(&self, session_id: &str) -> Result<bool, AppError> {
        let conn = self.conn.lock().map_err(|_| AppError::Internal("lock poisoned".into()))?;
        
        let mut stmt = conn.prepare("SELECT sync_status FROM results WHERE session_id = ?1")?;
        let status: Option<String> = stmt.query_row(params![session_id], |row| row.get(0)).ok();
        
        let changes = if let Some(st) = status {
            if st == "pending_insert" {
                conn.execute("DELETE FROM results WHERE session_id = ?1", params![session_id])?
            } else {
                conn.execute("UPDATE results SET sync_status = 'pending_delete' WHERE session_id = ?1", params![session_id])?
            }
        } else {
            0
        };
        Ok(changes > 0)
    }

    fn get_pending(&self) -> Result<Vec<SessionResult>, AppError> {
        let conn = self.conn.lock().map_err(|_| AppError::Internal("lock poisoned".into()))?;
        let mut stmt = conn.prepare("SELECT session_id, mode, started_at, ended_at, notes, app_version, device_id, patient_id, organisation_id, created_by_user_id, consent_id, sync_status, remote_id FROM results WHERE sync_status != 'synced'")?;
        
        let iter = stmt.query_map([], |row| {
            Ok(SessionResult {
                session_id: row.get(0)?,
                mode: row.get(1)?,
                started_at: row.get(2)?,
                ended_at: row.get(3)?,
                notes: row.get(4)?,
                app_version: row.get(5)?,
                device_id: row.get(6)?,
                patient_id: row.get(7)?,
                organisation_id: row.get::<_, i64>(8)? as u64,
                created_by_user_id: row.get::<_, Option<i64>>(9)?.map(|v| v as u64),
                consent_id: row.get::<_, Option<i64>>(10)?.map(|v| v as u64),
                sync_status: row.get(11)?,
                remote_id: row.get(12)?,
            })
        })?;

        let mut items = Vec::new();
        for item in iter {
            items.push(item?);
        }
        Ok(items)
    }

    fn resolve_sync(&self, local_id: &str, remote_id: Option<String>, status: &str) -> Result<(), AppError> {
        let conn = self.conn.lock().map_err(|_| AppError::Internal("lock poisoned".into()))?;
        if status == "deleted" {
            conn.execute("DELETE FROM results WHERE session_id = ?1", params![local_id])?;
        } else {
            conn.execute(
                "UPDATE results SET sync_status = ?1, remote_id = ?2 WHERE session_id = ?3",
                params![status, remote_id, local_id],
            )?;
        }
        Ok(())
    }
}
