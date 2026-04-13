/// Get selected text from the focused application.
/// macOS: uses Accessibility API (no clipboard involvement).
/// Windows: simulates Ctrl+C via SendInput and reads clipboard.
pub fn get_selected_text(#[allow(unused)] app_handle: &tauri::AppHandle) -> Result<String, String> {
    #[cfg(target_os = "macos")]
    {
        get_selected_text_macos()
    }
    #[cfg(target_os = "windows")]
    {
        get_selected_text_windows(app_handle)
    }
    #[cfg(not(any(target_os = "macos", target_os = "windows")))]
    {
        Err("Text capture not supported on this platform".to_string())
    }
}

#[cfg(target_os = "macos")]
fn get_selected_text_macos() -> Result<String, String> {
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

        // Get focused application
        let attr = CFString::new("AXFocusedApplication");
        let mut focused_app: CFTypeRef = std::ptr::null_mut();
        let err = AXUIElementCopyAttributeValue(
            system_wide,
            attr.as_concrete_TypeRef(),
            &mut focused_app,
        );
        CFRelease(system_wide as CFTypeRef);

        if err != K_AX_ERROR_SUCCESS || focused_app.is_null() {
            return Err(
                "Cannot get focused application. Grant Accessibility permission in System Settings > Privacy & Security > Accessibility."
                    .to_string(),
            );
        }

        // Get focused UI element
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

        // Get selected text
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
