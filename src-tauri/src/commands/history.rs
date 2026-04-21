use std::sync::Arc;
use std::sync::RwLock;

use crate::services::history::HistoryManager;
use crate::types::TranslationRecord;

#[tauri::command]
pub fn history_navigate_up(
    history: tauri::State<'_, Arc<RwLock<HistoryManager>>>,
) -> Result<Option<TranslationRecord>, String> {
    let mut manager = history.write().map_err(|e| e.to_string())?;
    Ok(manager.navigate_up().cloned())
}

#[tauri::command]
pub fn history_navigate_down(
    history: tauri::State<'_, Arc<RwLock<HistoryManager>>>,
) -> Result<Option<TranslationRecord>, String> {
    let mut manager = history.write().map_err(|e| e.to_string())?;
    Ok(manager.navigate_down().cloned())
}

#[tauri::command]
pub fn history_exit(
    history: tauri::State<'_, Arc<RwLock<HistoryManager>>>,
) -> Result<(), String> {
    let mut manager = history.write().map_err(|e| e.to_string())?;
    manager.exit_history_mode();
    Ok(())
}

#[tauri::command]
pub fn history_is_in_history_mode(
    history: tauri::State<'_, Arc<RwLock<HistoryManager>>>,
) -> Result<bool, String> {
    let manager = history.read().map_err(|e| e.to_string())?;
    Ok(manager.is_in_history_mode())
}

#[tauri::command]
pub fn history_get_pointer(
    history: tauri::State<'_, Arc<RwLock<HistoryManager>>>,
) -> Result<i32, String> {
    let manager = history.read().map_err(|e| e.to_string())?;
    Ok(manager.get_pointer())
}

#[tauri::command]
pub fn history_clear(
    history: tauri::State<'_, Arc<RwLock<HistoryManager>>>,
) -> Result<(), String> {
    let mut manager = history.write().map_err(|e| e.to_string())?;
    manager.clear();
    manager.save()
}
