mod commands;
mod platform;
mod services;
mod types;

use std::sync::{Arc, Mutex, RwLock};

use tauri::{Emitter, Manager};

use services::cache::CacheManager;
use services::config::ConfigManager;
use services::history::HistoryManager;
use services::language::LanguageDetector;

#[cfg_attr(mobile, tauri::mobile_entry_point)]
pub fn run() {
    tauri::Builder::default()
        .plugin(tauri_plugin_clipboard_manager::init())
        .plugin(tauri_plugin_autostart::init(
            tauri_plugin_autostart::MacosLauncher::LaunchAgent,
            None,
        ))
        .plugin(
            tauri_plugin_global_shortcut::Builder::new()
                .with_handler(|app, shortcut, event| {
                    if event.state == tauri_plugin_global_shortcut::ShortcutState::Pressed {
                        let app = app.clone();
                        let shortcut_str = shortcut.to_string();
                        tauri::async_runtime::spawn(async move {
                            handle_shortcut(&app, &shortcut_str).await;
                        });
                    }
                })
                .build(),
        )
        .setup(|app| {
            let data_dir = app
                .path()
                .app_data_dir()
                .expect("failed to resolve app data dir");

            // Check for legacy CRKT config and migrate if found
            if !data_dir.join("config.json").exists() {
                let legacy_candidates = [
                    data_dir.parent().map(|p| p.join("CRKT")),
                    std::env::current_dir().ok().map(|d| d.join("CRKT")),
                ];
                for candidate in legacy_candidates.into_iter().flatten() {
                    if candidate.join("data").join("config.json").exists() {
                        if let Some(migrated) =
                            services::migration::migrate_legacy_config(&candidate)
                        {
                            let mut cm = ConfigManager::new(&data_dir);
                            let _ = cm.update(migrated);
                            log::info!("Migrated settings from legacy CRKT");
                        }
                        break;
                    }
                }
            }

            // Initialize services
            let config_manager = Arc::new(RwLock::new(ConfigManager::new(&data_dir)));
            let cache_manager = Arc::new(RwLock::new(CacheManager::new(&data_dir)));
            let history_manager = Arc::new(RwLock::new(HistoryManager::new(&data_dir)));
            let language_detector = Arc::new(LanguageDetector);
            let active_translation: Arc<Mutex<Option<tokio::task::AbortHandle>>> =
                Arc::new(Mutex::new(None));

            // Register global shortcuts from config
            register_shortcuts(app.handle(), &config_manager)?;

            // Manage state
            app.manage(config_manager);
            app.manage(cache_manager);
            app.manage(history_manager);
            app.manage(language_detector);
            app.manage(active_translation);

            // Setup system tray
            platform::tray::setup_tray(app.handle())
                .expect("failed to setup system tray");

            Ok(())
        })
        .invoke_handler(tauri::generate_handler![
            commands::config::get_config,
            commands::config::update_config,
            commands::cache::get_cache_stats,
            commands::cache::clear_cache,
            commands::history::history_navigate_up,
            commands::history::history_navigate_down,
            commands::history::history_exit,
            commands::history::history_is_in_history_mode,
            commands::history::history_get_pointer,
            commands::history::history_clear,
            commands::translation::translate,
            commands::translation::cancel_translation,
        ])
        .run(tauri::generate_context!())
        .expect("error while running tauri application");
}

fn register_shortcuts(
    app: &tauri::AppHandle,
    config_manager: &Arc<RwLock<ConfigManager>>,
) -> Result<(), Box<dyn std::error::Error>> {
    use tauri_plugin_global_shortcut::GlobalShortcutExt;

    let config = config_manager.read().map_err(|e| e.to_string())?;

    let translate_shortcut = config.config().translate_shortcut.clone();
    let append_shortcut = config.config().append_shortcut.clone();

    if let Ok(shortcut) = translate_shortcut.parse::<tauri_plugin_global_shortcut::Shortcut>() {
        app.global_shortcut().register(shortcut)?;
    }
    if let Ok(shortcut) = append_shortcut.parse::<tauri_plugin_global_shortcut::Shortcut>() {
        app.global_shortcut().register(shortcut)?;
    }

    Ok(())
}

async fn handle_shortcut(app: &tauri::AppHandle, shortcut_str: &str) {
    let config_arc: Arc<RwLock<ConfigManager>> = {
        let state = app.state::<Arc<RwLock<ConfigManager>>>();
        Arc::clone(&state)
    };
    let config = match config_arc.read() {
        Ok(manager) => manager.config().clone(),
        Err(_) => return,
    };

    // Determine which shortcut was triggered
    let is_translate = shortcut_str == config.translate_shortcut;
    let is_append = shortcut_str == config.append_shortcut;

    if !is_translate && !is_append {
        return;
    }

    // Check if in history mode — if so, exit history mode instead
    let history_arc: Arc<RwLock<HistoryManager>> = {
        let state = app.state::<Arc<RwLock<HistoryManager>>>();
        Arc::clone(&state)
    };
    if let Ok(mut history) = history_arc.write() {
        if history.is_in_history_mode() {
            history.exit_history_mode();
            drop(history);
            let _ = app.emit("history:exited", ());
            return;
        }
    }

    // Capture selected text from focused application
    let text = tokio::task::spawn_blocking({
        let app = app.clone();
        move || platform::text_capture::get_selected_text(&app)
    })
    .await;

    let text = match text {
        Ok(Ok(t)) if !t.trim().is_empty() => t,
        _ => return, // No text captured
    };

    if is_append {
        let _ = app.emit("source:append", &text);
        platform::window::show_near_cursor(app);
    } else {
        // Translate: show window and invoke translation
        platform::window::show_near_cursor(app);
        let _ = app.emit("translation:started", ());

        // Invoke translation through the command pipeline
        let config_state = app.state::<Arc<RwLock<ConfigManager>>>();
        let cache_state = app.state::<Arc<RwLock<CacheManager>>>();
        let history_state = app.state::<Arc<RwLock<HistoryManager>>>();
        let detector_state = app.state::<Arc<LanguageDetector>>();
        let abort_state = app.state::<Arc<Mutex<Option<tokio::task::AbortHandle>>>>();

        let _ = commands::translation::translate(
            text,
            app.clone(),
            config_state,
            cache_state,
            history_state,
            detector_state,
            abort_state,
        )
        .await;
    }
}
