use std::sync::Arc;
use std::sync::RwLock;

use crate::services::config::ConfigManager;
use crate::types::AppConfig;

#[tauri::command]
pub fn get_config(config: tauri::State<'_, Arc<RwLock<ConfigManager>>>) -> Result<AppConfig, String> {
    let manager = config.read().map_err(|e| e.to_string())?;
    Ok(manager.config().clone())
}

#[tauri::command]
pub fn update_config(
    new_config: AppConfig,
    config: tauri::State<'_, Arc<RwLock<ConfigManager>>>,
) -> Result<(), String> {
    let mut manager = config.write().map_err(|e| e.to_string())?;
    manager.update(new_config)
}
