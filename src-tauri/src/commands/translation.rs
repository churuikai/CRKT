use std::sync::{Arc, Mutex, RwLock};

use tauri::Emitter;

use crate::services::cache::CacheManager;
use crate::services::config::ConfigManager;
use crate::services::history::HistoryManager;
use crate::services::language::LanguageDetector;
use crate::services::translator;
use crate::types::TranslationRecord;

#[tauri::command]
pub async fn translate(
    text: String,
    app_handle: tauri::AppHandle,
    config_state: tauri::State<'_, Arc<RwLock<ConfigManager>>>,
    cache_state: tauri::State<'_, Arc<RwLock<CacheManager>>>,
    history_state: tauri::State<'_, Arc<RwLock<HistoryManager>>>,
    detector_state: tauri::State<'_, Arc<LanguageDetector>>,
    abort_state: tauri::State<'_, Arc<Mutex<Option<tokio::task::AbortHandle>>>>,
) -> Result<(), String> {
    // Cancel any active translation
    {
        let mut active = abort_state.lock().map_err(|e| e.to_string())?;
        if let Some(handle) = active.take() {
            handle.abort();
        }
    }

    // Read config
    let config = config_state
        .read()
        .map_err(|e| e.to_string())?
        .config()
        .clone();

    // Detect language
    let detector = detector_state.inner().clone();
    let source_lang = detector.detect(&text);
    let target_lang = detector.get_target_language(&source_lang, &config.target_language);

    // Emit source update
    let _ = app_handle.emit("source:update", &text);

    // Check cache
    {
        let mut cache = cache_state.write().map_err(|e| e.to_string())?;
        if let Some(cached) = cache.get(&text) {
            let _ = app_handle.emit("translation:complete", &cached);
            return Ok(());
        }
    }

    // Get API profile + skill prompt
    let api_profile = config
        .get_selected_api_profile()
        .ok_or("No API profile selected")?
        .clone();
    let skill_prompt = config
        .get_selected_skill_prompt()
        .ok_or("No skill selected")?
        .to_string();

    if api_profile.api_key.is_empty() {
        return Err("API Key is not configured".to_string());
    }

    eprintln!("[CRKT] translate: api={}, model={}, url={}", api_profile.name, config.selected_model, api_profile.base_url);

    // Clone everything needed for the spawned task
    let cache = Arc::clone(&cache_state);
    let history = Arc::clone(&history_state);
    let app = app_handle.clone();
    let text_clone = text.clone();
    let source_code = source_lang.code.clone();
    let target_code = target_lang.code.clone();
    let source_name = source_lang.name.clone();
    let target_name = target_lang.name.clone();
    let model = config.selected_model.clone();
    let skill_name = config.selected_skill.clone();

    let task = tokio::spawn(async move {
        eprintln!("[CRKT] spawned task: calling translate_stream...");
        match translator::translate_stream(
            &text_clone,
            &skill_prompt,
            &source_name,
            &target_name,
            &api_profile.api_key,
            &api_profile.base_url,
            &model,
            &app,
        )
        .await
        {
            Ok(ref result) => {
                eprintln!("[CRKT] translate_stream OK, len={}", result.len());
                // Save to cache
                if let Ok(mut c) = cache.write() {
                    c.set(text_clone.clone(), result.clone());
                }
                // Save to history
                if let Ok(mut h) = history.write() {
                    h.add_record(TranslationRecord {
                        id: uuid::Uuid::new_v4().to_string(),
                        source_text: text_clone,
                        translated_text: result.clone(),
                        source_language: source_code,
                        target_language: target_code,
                        timestamp: chrono::Utc::now().to_rfc3339(),
                        model,
                        skill: skill_name,
                    });
                    let _ = h.save();
                }
            }
            Err(ref e) => {
                eprintln!("[CRKT] translate_stream ERROR: {}", e);
                let _ = app.emit("translation:error", e.as_str());
            }
        }
    });

    // Store abort handle
    {
        let mut active = abort_state.lock().map_err(|e| e.to_string())?;
        *active = Some(task.abort_handle());
    }

    Ok(())
}

#[tauri::command]
pub fn cancel_translation(
    abort_state: tauri::State<'_, Arc<Mutex<Option<tokio::task::AbortHandle>>>>,
) -> Result<(), String> {
    let mut active = abort_state.lock().map_err(|e| e.to_string())?;
    if let Some(handle) = active.take() {
        handle.abort();
    }
    Ok(())
}
