use std::sync::{Arc, RwLock};

use tauri::{
    menu::{CheckMenuItemBuilder, MenuBuilder, MenuItemBuilder},
    tray::{MouseButton, MouseButtonState, TrayIconBuilder, TrayIconEvent},
    AppHandle, Manager,
};

use tauri_plugin_autostart::ManagerExt;

use crate::services::config::ConfigManager;

pub fn setup_tray(app: &AppHandle) -> Result<(), Box<dyn std::error::Error>> {
    let settings_item = MenuItemBuilder::with_id("settings", "设置").build(app)?;

    let autostart_item =
        CheckMenuItemBuilder::with_id("autostart", "开机自启动").build(app)?;

    let about_item = MenuItemBuilder::with_id("about", "关于").build(app)?;

    let quit_item = MenuItemBuilder::with_id("quit", "退出").build(app)?;

    let menu = MenuBuilder::new(app)
        .item(&settings_item)
        .separator()
        .item(&autostart_item)
        .separator()
        .item(&about_item)
        .separator()
        .item(&quit_item)
        .build()?;

    // Set initial check states from config
    if let Ok(config_lock) = app.state::<Arc<RwLock<ConfigManager>>>().read() {
        let config = config_lock.config();
        let _ = autostart_item.set_checked(config.start_on_boot);
    }

    let mut tray_builder = TrayIconBuilder::with_id("main-tray")
        .menu(&menu)
        .show_menu_on_left_click(false)
        .tooltip("CRKT Translator");

    if let Some(icon) = app.default_window_icon().cloned() {
        tray_builder = tray_builder.icon(icon).icon_as_template(true);
    }

    let _tray = tray_builder
        .on_menu_event(move |app, event| {
            match event.id().as_ref() {
                "settings" => {
                    open_settings_window(app);
                }
                "autostart" => {
                    if let Ok(checked) = autostart_item.is_checked() {
                        let config_state = app.state::<Arc<RwLock<ConfigManager>>>();
                        if let Ok(mut manager) = config_state.write() {
                            let _ = manager.update_field(|c| c.start_on_boot = checked);
                        }
                        toggle_autostart(app, checked);
                    }
                }
                "about" => {
                    let _ = open::that("https://github.com/churuikai/CRKT");
                }
                "quit" => {
                    save_all_state(app);
                    app.exit(0);
                }
                _ => {}
            }
        })
        .on_tray_icon_event(|tray, event| {
            if let TrayIconEvent::Click {
                button: MouseButton::Left,
                button_state: MouseButtonState::Up,
                ..
            } = event
            {
                let app = tray.app_handle();
                if let Some(window) = app.get_webview_window("main") {
                    if window.is_visible().unwrap_or(false) {
                        let _ = window.hide();
                    } else {
                        let _ = window.show();
                        let _ = window.unminimize();
                        let _ = window.set_focus();
                    }
                }
            }
        })
        .build(app)?;

    Ok(())
}

fn open_settings_window(app: &AppHandle) {
    if let Some(window) = app.get_webview_window("settings") {
        let _ = window.set_focus();
        return;
    }
    let _ = tauri::WebviewWindowBuilder::new(
        app,
        "settings",
        tauri::WebviewUrl::App("settings.html".into()),
    )
    .title("CRKT - 设置")
    .inner_size(800.0, 600.0)
    .center()
    .build();
}

fn toggle_autostart(app: &AppHandle, enabled: bool) {
    let manager = app.autolaunch();
    if enabled {
        let _ = manager.enable();
    } else {
        let _ = manager.disable();
    }
}

fn save_all_state(app: &AppHandle) {
    if let Ok(cache) = app
        .state::<Arc<RwLock<crate::services::cache::CacheManager>>>()
        .read()
    {
        let _ = cache.save();
    }
    if let Ok(history) = app
        .state::<Arc<RwLock<crate::services::history::HistoryManager>>>()
        .read()
    {
        let _ = history.save();
    }
}
