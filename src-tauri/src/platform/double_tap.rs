use std::sync::mpsc;

/// Which modifier key to detect double-tap on.
#[derive(Clone, Copy)]
pub enum ModifierKey {
    Ctrl,
    Shift,
}

/// Start a double-tap listener for the given modifier key.
/// Returns a Receiver that emits `()` each time a double-tap is detected.
#[cfg(target_os = "macos")]
pub fn start_listener(key: ModifierKey) -> mpsc::Receiver<()> {
    macos::start_listener(key)
}

#[cfg(not(target_os = "macos"))]
pub fn start_listener(_key: ModifierKey) -> mpsc::Receiver<()> {
    let (_tx, rx) = mpsc::channel();
    eprintln!("[CRKT] double_tap: not implemented on this platform");
    rx
}

/// Parse a "DoubleTap:Ctrl" / "DoubleTap:Shift" config string.
/// Returns None if the string is not a double-tap shortcut.
pub fn parse_double_tap(s: &str) -> Option<ModifierKey> {
    let suffix = s.strip_prefix("DoubleTap:")?;
    match suffix {
        "Ctrl" => Some(ModifierKey::Ctrl),
        "Shift" => Some(ModifierKey::Shift),
        _ => None,
    }
}

#[cfg(target_os = "macos")]
mod macos {
    use super::ModifierKey;
    use std::ffi::c_void;
    use std::sync::mpsc;
    use std::sync::Once;
    use std::time::{Duration, Instant};

    /// Fires at most once per process — both the translate and append listener
    /// can hit the failure path simultaneously, and we don't want to open the
    /// Settings pane twice.
    static OPEN_SETTINGS_ONCE: Once = Once::new();

    const DOUBLE_TAP_INTERVAL: Duration = Duration::from_millis(400);
    const COOLDOWN_AFTER_TRIGGER: Duration = Duration::from_millis(800);

    // CGEvent constants
    const K_CG_EVENT_FLAGS_CHANGED: u32 = 12;
    const K_CG_EVENT_KEY_DOWN: u32 = 10;
    const K_CG_EVENT_TAP_DISABLED_BY_TIMEOUT: u32 = 0xFFFFFFFE;
    const K_CG_EVENT_TAP_DISABLED_BY_USER_INPUT: u32 = 0xFFFFFFFF;
    const K_CG_SESSION_EVENT_TAP: u32 = 1;
    const K_CG_HEAD_INSERT_EVENT_TAP: u32 = 0;
    const K_CG_EVENT_TAP_OPTION_LISTEN_ONLY: u32 = 1;

    // Bits we treat as "modifier state". Anything outside this mask (e.g.
    // kCGEventFlagMaskNonCoalesced = 0x100, device-specific left/right bits)
    // is filtered out of equality checks so that spurious FLAGS_CHANGED events
    // — which macOS does emit — are not mistaken for an interruption.
    const MODIFIER_FLAGS_MASK: u64 = (1 << 16)  // AlphaShift (CapsLock)
        | (1 << 17)  // Shift
        | (1 << 18)  // Control
        | (1 << 19)  // Alternate (Option)
        | (1 << 20)  // Command
        | (1 << 23); // SecondaryFn

    type CGEventTapProxy = *const c_void;
    type CGEventRef = *mut c_void;
    type CFMachPortRef = *mut c_void;

    type CGEventTapCallBack = extern "C" fn(
        CGEventTapProxy,
        u32,
        CGEventRef,
        *mut c_void,
    ) -> CGEventRef;

    extern "C" {
        fn CGEventTapCreate(
            tap: u32,
            place: u32,
            options: u32,
            events_of_interest: u64,
            callback: CGEventTapCallBack,
            user_info: *mut c_void,
        ) -> CFMachPortRef;
        fn CGEventTapEnable(tap: CFMachPortRef, enable: bool);
        fn CGEventGetFlags(event: CGEventRef) -> u64;
        fn CFMachPortCreateRunLoopSource(
            allocator: *const c_void,
            port: CFMachPortRef,
            order: i64,
        ) -> *mut c_void;
        fn CFRunLoopGetCurrent() -> *mut c_void;
        fn CFRunLoopAddSource(rl: *mut c_void, source: *mut c_void, mode: *const c_void);
        fn CFRunLoopRun();

        static kCFRunLoopCommonModes: *const c_void;
    }

    fn flag_mask(key: ModifierKey) -> u64 {
        match key {
            ModifierKey::Ctrl => 1 << 18,  // kCGEventFlagMaskControl
            ModifierKey::Shift => 1 << 17, // kCGEventFlagMaskShift
        }
    }

    fn key_name(key: ModifierKey) -> &'static str {
        match key {
            ModifierKey::Ctrl => "Ctrl",
            ModifierKey::Shift => "Shift",
        }
    }

    struct TapState {
        target_mask: u64,
        last_key_release: Option<Instant>,
        other_key_pressed: bool,
        cooldown_until: Option<Instant>,
        was_key_pressed: bool,
        prev_modifier_flags: u64,
        tap_port: CFMachPortRef,
        tx: mpsc::Sender<()>,
    }

    extern "C" fn tap_callback(
        _proxy: CGEventTapProxy,
        event_type: u32,
        event: CGEventRef,
        user_info: *mut c_void,
    ) -> CGEventRef {
        let state = unsafe { &mut *(user_info as *mut TapState) };

        // Re-enable if macOS disabled the tap due to timeout
        if event_type == K_CG_EVENT_TAP_DISABLED_BY_TIMEOUT
            || event_type == K_CG_EVENT_TAP_DISABLED_BY_USER_INPUT
        {
            if !state.tap_port.is_null() {
                unsafe { CGEventTapEnable(state.tap_port, true) };
            }
            return event;
        }

        // Cooldown: only suppresses triggering, NOT state tracking
        let in_cooldown = state
            .cooldown_until
            .map(|until| {
                if Instant::now() < until {
                    true
                } else {
                    state.cooldown_until = None;
                    false
                }
            })
            .unwrap_or(false);

        if event_type == K_CG_EVENT_FLAGS_CHANGED {
            let flags = unsafe { CGEventGetFlags(event) } & MODIFIER_FLAGS_MASK;
            let key_now = (flags & state.target_mask) != 0;
            let prev_flags = state.prev_modifier_flags;
            state.prev_modifier_flags = flags;

            if key_now != state.was_key_pressed {
                // Target modifier state changed — always update was_key_pressed
                if key_now {
                    // Key pressed — check for double-tap (skip if in cooldown)
                    if !in_cooldown {
                        if let Some(last) = state.last_key_release {
                            if !state.other_key_pressed
                                && last.elapsed() < DOUBLE_TAP_INTERVAL
                            {
                                state.last_key_release = None;
                                state.cooldown_until =
                                    Some(Instant::now() + COOLDOWN_AFTER_TRIGGER);
                                let _ = state.tx.send(());
                            }
                        }
                    }
                } else {
                    // Key released
                    if !state.other_key_pressed {
                        state.last_key_release = Some(Instant::now());
                    }
                    state.other_key_pressed = false;
                }
                state.was_key_pressed = key_now;
            } else if (flags ^ prev_flags) & !state.target_mask != 0 {
                // Some OTHER modifier actually changed — treat as interruption.
                // Plain `key_now == was_key_pressed` is not enough: macOS also
                // emits FLAGS_CHANGED events with no real modifier change, and
                // those would otherwise wipe `last_key_release` between the
                // release and the next press of a double-tap.
                state.other_key_pressed = true;
                state.last_key_release = None;
            }
        } else if event_type == K_CG_EVENT_KEY_DOWN {
            // Regular key pressed — reset
            state.other_key_pressed = true;
            state.last_key_release = None;
        }

        event
    }

    pub fn start_listener(key: ModifierKey) -> mpsc::Receiver<()> {
        let (tx, rx) = mpsc::channel();
        let mask = flag_mask(key);
        let name = key_name(key);

        std::thread::spawn(move || {
            eprintln!("[CRKT] double_tap: starting CGEventTap for {}", name);

            let event_mask: u64 =
                (1 << K_CG_EVENT_FLAGS_CHANGED) | (1 << K_CG_EVENT_KEY_DOWN);

            unsafe {
                let state = Box::into_raw(Box::new(TapState {
                    target_mask: mask,
                    last_key_release: None,
                    other_key_pressed: false,
                    cooldown_until: None,
                    was_key_pressed: false,
                    prev_modifier_flags: 0,
                    tap_port: std::ptr::null_mut(),
                    tx,
                }));

                let tap = CGEventTapCreate(
                    K_CG_SESSION_EVENT_TAP,
                    K_CG_HEAD_INSERT_EVENT_TAP,
                    K_CG_EVENT_TAP_OPTION_LISTEN_ONLY,
                    event_mask,
                    tap_callback,
                    state as *mut c_void,
                );

                if tap.is_null() {
                    eprintln!("[CRKT] double_tap: CGEventTapCreate failed for {}", name);
                    OPEN_SETTINGS_ONCE.call_once(|| {
                        eprintln!("[CRKT] Input Monitoring permission likely missing, prompting user");
                        // Modal dialog first so the user actually sees this — a
                        // bare `open::that(Settings)` gets covered by the AX
                        // system dialog that fires around the same time.
                        let _ = std::process::Command::new("osascript")
                            .args([
                                "-e",
                                r#"display dialog "Translator 需要「输入监控」权限来识别双击 Ctrl/Shift 等全局快捷键。

点击「打开设置」后，请在「输入监控」列表中找到 Translator,打开它的开关,然后完全退出并重新启动 Translator。" with title "需要输入监控权限" buttons {"打开设置"} default button 1 with icon caution"#,
                            ])
                            .status();
                        let _ = open::that(
                            "x-apple.systempreferences:com.apple.preference.security?Privacy_ListenEvent",
                        );
                    });
                    drop(Box::from_raw(state));
                    return;
                }

                (*state).tap_port = tap;

                let source = CFMachPortCreateRunLoopSource(std::ptr::null(), tap, 0);
                if source.is_null() {
                    eprintln!("[CRKT] double_tap: CFMachPortCreateRunLoopSource failed");
                    drop(Box::from_raw(state));
                    return;
                }

                CFRunLoopAddSource(CFRunLoopGetCurrent(), source, kCFRunLoopCommonModes);
                CGEventTapEnable(tap, true);

                eprintln!("[CRKT] double_tap: {} listener active", name);
                CFRunLoopRun();
            }
        });

        rx
    }
}
