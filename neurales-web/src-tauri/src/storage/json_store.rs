use std::fs;
use std::path::PathBuf;

use serde::de::DeserializeOwned;
use serde::Serialize;

const DATA_DIR_NAME: &str = "neurales_desktop_data";
const APP_DIR_NAME: &str = "NeuralESDesktop";

fn data_dir() -> Result<PathBuf, String> {
    let base_dir = dirs::data_local_dir().or_else(|| dirs::data_dir()).unwrap_or_else(|| {
        std::env::current_dir().unwrap_or_else(|_| PathBuf::from("."))
    });

    let dir = base_dir.join(APP_DIR_NAME).join(DATA_DIR_NAME);
    fs::create_dir_all(&dir).map_err(|e| format!("cannot create data dir: {e}"))?;
    Ok(dir)
}

fn data_file(file_name: &str) -> Result<PathBuf, String> {
    Ok(data_dir()?.join(file_name))
}

pub fn load_items<T: DeserializeOwned>(file_name: &str) -> Result<Vec<T>, String> {
    let path = data_file(file_name)?;

    // Dev-mode migration path: preserve data previously written under the working directory.
    if !path.exists() {
        let legacy = legacy_data_file(file_name)?;
        if legacy.exists() {
            if let Some(parent) = path.parent() {
                fs::create_dir_all(parent)
                    .map_err(|e| format!("cannot create data dir {}: {e}", parent.display()))?;
            }
            fs::copy(&legacy, &path)
                .map_err(|e| format!("cannot migrate {} to {}: {e}", legacy.display(), path.display()))?;
        }
    }

    if !path.exists() {
        return Ok(Vec::new());
    }

    let raw = fs::read_to_string(&path).map_err(|e| format!("cannot read {}: {e}", path.display()))?;
    if raw.trim().is_empty() {
        return Ok(Vec::new());
    }

    serde_json::from_str::<Vec<T>>(&raw)
        .map_err(|e| format!("invalid json in {}: {e}", path.display()))
}

pub fn save_items<T: Serialize>(file_name: &str, items: &[T]) -> Result<(), String> {
    let path = data_file(file_name)?;
    let raw = serde_json::to_string_pretty(items)
        .map_err(|e| format!("cannot serialize {}: {e}", path.display()))?;
    fs::write(&path, raw).map_err(|e| format!("cannot write {}: {e}", path.display()))
}

fn legacy_data_file(file_name: &str) -> Result<PathBuf, String> {
    let cwd = std::env::current_dir().map_err(|e| format!("cannot resolve current dir: {e}"))?;
    Ok(cwd.join(DATA_DIR_NAME).join(file_name))
}
