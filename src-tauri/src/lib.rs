mod commands;
mod services;
mod types;

use std::sync::{Arc, RwLock};

use services::config::ConfigManager;
use tauri::Manager;

#[cfg_attr(mobile, tauri::mobile_entry_point)]
pub fn run() {
    tauri::Builder::default()
        .plugin(tauri_plugin_clipboard_manager::init())
        .plugin(tauri_plugin_autostart::init(
            tauri_plugin_autostart::MacosLauncher::LaunchAgent,
            None,
        ))
        .setup(|app| {
            let data_dir = app
                .path()
                .app_data_dir()
                .expect("failed to resolve app data dir");

            let config_manager = Arc::new(RwLock::new(ConfigManager::new(&data_dir)));
            app.manage(config_manager);

            let cache_manager = Arc::new(RwLock::new(
                services::cache::CacheManager::new(&data_dir),
            ));
            app.manage(cache_manager);

            let history_manager = Arc::new(RwLock::new(
                services::history::HistoryManager::new(&data_dir),
            ));
            app.manage(history_manager);

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
        ])
        .run(tauri::generate_context!())
        .expect("error while running tauri application");
}
