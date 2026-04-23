#[cfg(target_os = "macos")]
pub fn ensure_accessibility_permission() -> bool {
    use core_foundation::base::TCFType;
    use core_foundation::boolean::CFBoolean;
    use core_foundation::dictionary::CFDictionary;
    use core_foundation::string::CFString;
    use std::ffi::c_void;

    extern "C" {
        fn AXIsProcessTrustedWithOptions(options: *const c_void) -> bool;
    }

    // Check silently first — no dialog if already trusted
    let key = CFString::new("AXTrustedCheckOptionPrompt");
    let options = CFDictionary::from_CFType_pairs(&[(key, CFBoolean::false_value())]);
    let trusted =
        unsafe { AXIsProcessTrustedWithOptions(options.as_concrete_TypeRef() as *const c_void) };

    if trusted {
        return true;
    }

    // Not trusted — call with prompt=true to register in TCC and show system dialog
    eprintln!("[CRKT] Accessibility permission not granted, prompting user");
    let key = CFString::new("AXTrustedCheckOptionPrompt");
    let options = CFDictionary::from_CFType_pairs(&[(key, CFBoolean::true_value())]);
    unsafe { AXIsProcessTrustedWithOptions(options.as_concrete_TypeRef() as *const c_void) };
    false
}

#[cfg(not(target_os = "macos"))]
pub fn ensure_accessibility_permission() -> bool {
    true
}

/// Get selected text from the focused application.
/// macOS: tries Accessibility API first, falls back to Cmd+C clipboard.
/// Windows: simulates Ctrl+C via SendInput and reads clipboard.
pub fn get_selected_text(app_handle: &tauri::AppHandle) -> Result<String, String> {
    #[cfg(target_os = "macos")]
    {
        get_selected_text_macos(app_handle)
    }
    #[cfg(target_os = "windows")]
    {
        get_selected_text_windows(app_handle)
    }
    #[cfg(not(any(target_os = "macos", target_os = "windows")))]
    {
        let _ = app_handle;
        Err("Text capture not supported on this platform".to_string())
    }
}

#[cfg(target_os = "macos")]
fn get_selected_text_macos(app_handle: &tauri::AppHandle) -> Result<String, String> {
    // Strategy: try Accessibility API first (fast, non-invasive),
    // fall back to simulating Cmd+C if AX fails (wider app compatibility).
    if let Ok(text) = get_selected_text_ax() {
        if !text.trim().is_empty() {
            eprintln!("[CRKT] text capture: AX API succeeded, len={}", text.len());
            return Ok(text);
        }
    }

    eprintln!("[CRKT] text capture: AX API failed, falling back to Cmd+C");
    get_selected_text_clipboard_mac(app_handle)
}

/// Try to get selected text via macOS Accessibility API (AXSelectedText).
/// Works with native Cocoa apps and some well-behaved apps.
#[cfg(target_os = "macos")]
fn get_selected_text_ax() -> Result<String, String> {
    use core_foundation::base::{CFRelease, CFTypeRef, TCFType};
    use core_foundation::string::{CFString, CFStringRef};
    use std::ffi::c_void;

    type AXUIElementRef = *mut c_void;
    type AXError = i32;
    const K_AX_ERROR_SUCCESS: AXError = 0;

    extern "C" {
        fn AXUIElementCreateSystemWide() -> AXUIElementRef;
        fn AXUIElementCopyAttributeValue(
            element: AXUIElementRef,
            attribute: CFStringRef,
            value: *mut CFTypeRef,
        ) -> AXError;
    }

    unsafe {
        let system_wide = AXUIElementCreateSystemWide();

        let attr = CFString::new("AXFocusedApplication");
        let mut focused_app: CFTypeRef = std::ptr::null_mut();
        let err = AXUIElementCopyAttributeValue(
            system_wide,
            attr.as_concrete_TypeRef(),
            &mut focused_app,
        );
        CFRelease(system_wide as CFTypeRef);

        if err != K_AX_ERROR_SUCCESS || focused_app.is_null() {
            return Err("Cannot get focused application".to_string());
        }

        let attr = CFString::new("AXFocusedUIElement");
        let mut focused_element: CFTypeRef = std::ptr::null_mut();
        let err = AXUIElementCopyAttributeValue(
            focused_app as AXUIElementRef,
            attr.as_concrete_TypeRef(),
            &mut focused_element,
        );
        CFRelease(focused_app);

        if err != K_AX_ERROR_SUCCESS || focused_element.is_null() {
            return Err("Cannot get focused UI element".to_string());
        }

        let attr = CFString::new("AXSelectedText");
        let mut selected_text: CFTypeRef = std::ptr::null_mut();
        let err = AXUIElementCopyAttributeValue(
            focused_element as AXUIElementRef,
            attr.as_concrete_TypeRef(),
            &mut selected_text,
        );
        CFRelease(focused_element);

        if err != K_AX_ERROR_SUCCESS || selected_text.is_null() {
            return Err("No text selected".to_string());
        }

        let cf_string = CFString::wrap_under_create_rule(selected_text as CFStringRef);
        Ok(cf_string.to_string())
    }
}

/// Fallback: simulate Cmd+C, read clipboard via Tauri plugin, restore original.
/// Works with virtually all apps that support standard copy.
#[cfg(target_os = "macos")]
fn get_selected_text_clipboard_mac(app_handle: &tauri::AppHandle) -> Result<String, String> {
    use std::ffi::c_void;
    use tauri_plugin_clipboard_manager::ClipboardExt;

    extern "C" {
        fn CGEventCreateKeyboardEvent(
            source: *const c_void,
            keycode: u16,
            key_down: bool,
        ) -> *mut c_void;
        fn CGEventSetFlags(event: *mut c_void, flags: u64);
        fn CGEventPost(tap: u32, event: *mut c_void);
        fn CFRelease(cf: *const c_void);
    }

    const K_VK_C: u16 = 8; // macOS virtual keycode for 'C'
    const K_CG_EVENT_FLAG_MASK_COMMAND: u64 = 1 << 20;
    const K_CG_HID_EVENT_TAP: u32 = 0; // kCGHIDEventTap

    let clipboard = app_handle.clipboard();

    // Save original clipboard content
    let saved = clipboard.read_text().ok();

    // Clear clipboard so we can detect if copy worked
    let _ = clipboard.write_text("");

    // Simulate Cmd+C
    unsafe {
        let cmd_down = CGEventCreateKeyboardEvent(std::ptr::null(), K_VK_C, true);
        CGEventSetFlags(cmd_down, K_CG_EVENT_FLAG_MASK_COMMAND);
        CGEventPost(K_CG_HID_EVENT_TAP, cmd_down);
        CFRelease(cmd_down as *const c_void);

        let cmd_up = CGEventCreateKeyboardEvent(std::ptr::null(), K_VK_C, false);
        CGEventSetFlags(cmd_up, K_CG_EVENT_FLAG_MASK_COMMAND);
        CGEventPost(K_CG_HID_EVENT_TAP, cmd_up);
        CFRelease(cmd_up as *const c_void);
    }

    // Wait for clipboard update
    std::thread::sleep(std::time::Duration::from_millis(150));

    // Read copied text
    let text = clipboard
        .read_text()
        .map_err(|e| format!("Clipboard read error: {}", e))?;

    // Restore original clipboard
    if let Some(saved) = saved {
        let _ = clipboard.write_text(saved);
    }

    if text.is_empty() {
        return Err("No text copied".to_string());
    }

    Ok(text)
}

#[cfg(target_os = "windows")]
fn get_selected_text_windows(app_handle: &tauri::AppHandle) -> Result<String, String> {
    use tauri_plugin_clipboard_manager::ClipboardExt;
    use windows::Win32::UI::Input::KeyboardAndMouse::*;

    let clipboard = app_handle.clipboard();

    // Save current clipboard
    let saved = clipboard.read_text().ok();

    // Clear clipboard
    let _ = clipboard.write_text("");

    // Simulate Ctrl+C
    unsafe {
        let inputs = [
            INPUT {
                r#type: INPUT_KEYBOARD,
                Anonymous: INPUT_0 {
                    ki: KEYBDINPUT {
                        wVk: VK_CONTROL,
                        ..Default::default()
                    },
                },
            },
            INPUT {
                r#type: INPUT_KEYBOARD,
                Anonymous: INPUT_0 {
                    ki: KEYBDINPUT {
                        wVk: VK_C,
                        ..Default::default()
                    },
                },
            },
            INPUT {
                r#type: INPUT_KEYBOARD,
                Anonymous: INPUT_0 {
                    ki: KEYBDINPUT {
                        wVk: VK_C,
                        dwFlags: KEYEVENTF_KEYUP,
                        ..Default::default()
                    },
                },
            },
            INPUT {
                r#type: INPUT_KEYBOARD,
                Anonymous: INPUT_0 {
                    ki: KEYBDINPUT {
                        wVk: VK_CONTROL,
                        dwFlags: KEYEVENTF_KEYUP,
                        ..Default::default()
                    },
                },
            },
        ];
        SendInput(&inputs, std::mem::size_of::<INPUT>() as i32);
    }

    // Wait for clipboard update
    std::thread::sleep(std::time::Duration::from_millis(150));

    // Read selected text
    let text = clipboard.read_text().map_err(|e| e.to_string())?;

    // Restore original clipboard
    if let Some(saved) = saved {
        let _ = clipboard.write_text(saved);
    }

    Ok(text)
}
