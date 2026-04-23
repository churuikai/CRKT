pub mod double_tap;
pub mod text_capture;
pub mod tray;
pub mod window;

/// Open a System Settings page by URL scheme.
/// Non-blocking, safe to call at any point during app lifecycle.
#[cfg(target_os = "macos")]
pub fn open_settings(settings_url: &str) {
    let _ = open::that(settings_url);
}
