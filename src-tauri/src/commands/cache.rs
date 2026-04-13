use std::sync::Arc;
use std::sync::RwLock;

use serde::Serialize;

use crate::services::cache::CacheManager;

#[derive(Serialize)]
pub struct CacheStats {
    pub size: usize,
}

#[tauri::command]
pub fn get_cache_stats(
    cache: tauri::State<'_, Arc<RwLock<CacheManager>>>,
) -> Result<CacheStats, String> {
    let manager = cache.read().map_err(|e| e.to_string())?;
    Ok(CacheStats {
        size: manager.len(),
    })
}

#[tauri::command]
pub fn clear_cache(
    cache: tauri::State<'_, Arc<RwLock<CacheManager>>>,
) -> Result<(), String> {
    let mut manager = cache.write().map_err(|e| e.to_string())?;
    manager.clear();
    manager.save()
}
