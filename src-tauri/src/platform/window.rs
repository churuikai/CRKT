use tauri::{AppHandle, Manager, PhysicalPosition, WebviewWindow};

/// Show the main window near the mouse cursor position.
/// If the window is already visible, don't reposition — just ensure focus.
pub fn show_near_cursor(app: &AppHandle) {
    let Some(window) = app.get_webview_window("main") else {
        return;
    };

    if window.is_visible().unwrap_or(false) && !window.is_minimized().unwrap_or(false) {
        let _ = window.set_focus();
        return;
    }

    if let Ok(cursor_pos) = get_cursor_position() {
        position_window_near(&window, cursor_pos);
    }

    let _ = window.show();
    let _ = window.unminimize();
    let _ = window.set_focus();
}

/// Toggle main window visibility. Used by tray icon click.
pub fn toggle_main_window(app: &AppHandle) {
    let Some(window) = app.get_webview_window("main") else {
        return;
    };

    if window.is_visible().unwrap_or(false) && !window.is_minimized().unwrap_or(false) {
        let _ = window.hide();
    } else {
        let _ = window.show();
        let _ = window.unminimize();
        let _ = window.set_focus();
    }
}

fn position_window_near(window: &WebviewWindow, cursor: PhysicalPosition<i32>) {
    let Ok(window_size) = window.outer_size() else {
        return;
    };

    let monitors = match window.available_monitors() {
        Ok(m) => m,
        Err(_) => return,
    };

    let monitor = monitors
        .iter()
        .find(|m| {
            let pos = m.position();
            let size = m.size();
            cursor.x >= pos.x
                && cursor.x < pos.x + size.width as i32
                && cursor.y >= pos.y
                && cursor.y < pos.y + size.height as i32
        })
        .or(monitors.first());

    let Some(monitor) = monitor else {
        return;
    };

    let screen_pos = monitor.position();
    let screen_size = monitor.size();

    let mut x = cursor.x - (window_size.width as i32) / 2;
    let mut y = cursor.y;

    let right_edge = screen_pos.x + screen_size.width as i32;
    let bottom_edge = screen_pos.y + screen_size.height as i32;

    if x + window_size.width as i32 > right_edge {
        x = right_edge - window_size.width as i32;
    }
    if x < screen_pos.x {
        x = screen_pos.x;
    }
    if y + window_size.height as i32 > bottom_edge {
        y = cursor.y - window_size.height as i32 - 10;
    }
    if y < screen_pos.y {
        y = screen_pos.y;
    }

    let _ = window.set_position(PhysicalPosition::new(x, y));
}

#[cfg(target_os = "macos")]
fn get_cursor_position() -> Result<PhysicalPosition<i32>, String> {
    extern "C" {
        fn CGEventCreate(source: *const std::ffi::c_void) -> *mut std::ffi::c_void;
        fn CGEventGetLocation(event: *const std::ffi::c_void) -> CGPoint;
        fn CFRelease(cf: *const std::ffi::c_void);
    }

    #[repr(C)]
    struct CGPoint {
        x: f64,
        y: f64,
    }

    unsafe {
        let event = CGEventCreate(std::ptr::null());
        if event.is_null() {
            return Err("Failed to create CG event".into());
        }
        let point = CGEventGetLocation(event);
        CFRelease(event);
        Ok(PhysicalPosition::new(point.x as i32, point.y as i32))
    }
}

#[cfg(target_os = "windows")]
fn get_cursor_position() -> Result<PhysicalPosition<i32>, String> {
    use windows::Win32::Foundation::POINT;
    use windows::Win32::UI::WindowsAndMessaging::GetCursorPos;

    unsafe {
        let mut point = POINT::default();
        GetCursorPos(&mut point).map_err(|e| e.to_string())?;
        Ok(PhysicalPosition::new(point.x, point.y))
    }
}

#[cfg(not(any(target_os = "macos", target_os = "windows")))]
fn get_cursor_position() -> Result<PhysicalPosition<i32>, String> {
    Ok(PhysicalPosition::new(500, 300))
}
