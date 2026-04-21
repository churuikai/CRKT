use std::path::Path;

use serde_json::Value;

use crate::types::{ApiProfile, AppConfig, Skill};

/// Attempt to migrate config from legacy Python CRKT format.
/// Returns Some(AppConfig) if migration succeeded, None if no legacy config found.
pub fn migrate_legacy_config(legacy_data_dir: &Path) -> Option<AppConfig> {
    let config_path = legacy_data_dir.join("data").join("config.json");
    let content = std::fs::read_to_string(&config_path).ok()?;
    let data: Value = serde_json::from_str(&content).ok()?;

    let mut config = AppConfig::default();

    // Migrate API profiles
    if let Some(profiles) = data["api_profiles"].as_array() {
        config.api_profiles = profiles
            .iter()
            .filter_map(|p| {
                Some(ApiProfile {
                    name: p["name"].as_str()?.to_string(),
                    api_key: p["api_key"].as_str().unwrap_or("").to_string(),
                    base_url: p["base_url"]
                        .as_str()
                        .unwrap_or("https://api.openai.com/v1/")
                        .to_string(),
                })
            })
            .collect();
    }

    if let Some(api) = data["selected_api"].as_str() {
        config.selected_api = api.to_string();
    }

    // Migrate models
    if let Some(models) = data["models"].as_array() {
        config.models = models
            .iter()
            .filter_map(|m| m.as_str().map(|s| s.to_string()))
            .collect();
    }
    if let Some(model) = data["selected_model"].as_str() {
        config.selected_model = model.to_string();
    }

    // Migrate skills
    if let Some(skills) = data["skills"].as_array() {
        config.skills = skills
            .iter()
            .filter_map(|s| {
                Some(Skill {
                    name: s["name"].as_str()?.to_string(),
                    prompt: s["prompt"].as_str().unwrap_or("").to_string(),
                })
            })
            .collect();
    }
    if let Some(skill) = data["selected_skill"].as_str() {
        config.selected_skill = skill.to_string();
    }

    // Migrate target language
    if let Some(lang) = data["target_language"].as_str() {
        config.target_language = lang.to_string();
    }

    // Migrate hotkeys: legacy uses {"key": "ctrl", "enabled": true}
    // New format: standard shortcut string
    if let Some(hotkey) = data["translate_hotkey"].as_object() {
        if let Some(key) = hotkey.get("key").and_then(|k| k.as_str()) {
            config.translate_shortcut = legacy_hotkey_to_shortcut(key, "T");
        }
    }
    if let Some(hotkey) = data["append_hotkey"].as_object() {
        if let Some(key) = hotkey.get("key").and_then(|k| k.as_str()) {
            config.append_shortcut = legacy_hotkey_to_shortcut(key, "A");
        }
    }

    // Migrate other flags
    config.start_on_boot = data["start_on_boot"].as_bool().unwrap_or(false);
    config.show_source_comparison = data["show_source_comparison"]
        .as_bool()
        .unwrap_or(false);

    Some(config)
}

fn legacy_hotkey_to_shortcut(legacy_key: &str, action_key: &str) -> String {
    match legacy_key {
        "ctrl" => format!("CmdOrCtrl+Shift+{}", action_key),
        "shift" => format!("CmdOrCtrl+Shift+{}", action_key),
        "alt" => format!("Alt+Shift+{}", action_key),
        _ => format!("CmdOrCtrl+Shift+{}", action_key),
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use tempfile::TempDir;

    fn write_legacy_config(dir: &Path, json: &str) {
        let data_dir = dir.join("data");
        std::fs::create_dir_all(&data_dir).unwrap();
        std::fs::write(data_dir.join("config.json"), json).unwrap();
    }

    #[test]
    fn test_migrate_basic() {
        let dir = TempDir::new().unwrap();
        write_legacy_config(
            dir.path(),
            r#"{
                "api_profiles": [{"name": "Test", "api_key": "sk-123", "base_url": "https://example.com/v1"}],
                "selected_api": "Test",
                "models": ["gpt-4o"],
                "selected_model": "gpt-4o",
                "target_language": "English"
            }"#,
        );

        let config = migrate_legacy_config(dir.path()).unwrap();
        assert_eq!(config.api_profiles[0].name, "Test");
        assert_eq!(config.api_profiles[0].api_key, "sk-123");
        assert_eq!(config.selected_model, "gpt-4o");
        assert_eq!(config.target_language, "English");
    }

    #[test]
    fn test_migrate_hotkeys() {
        let dir = TempDir::new().unwrap();
        write_legacy_config(
            dir.path(),
            r#"{
                "translate_hotkey": {"key": "ctrl", "enabled": true},
                "append_hotkey": {"key": "shift", "enabled": true}
            }"#,
        );

        let config = migrate_legacy_config(dir.path()).unwrap();
        assert_eq!(config.translate_shortcut, "CmdOrCtrl+Shift+T");
        assert_eq!(config.append_shortcut, "CmdOrCtrl+Shift+A");
    }

    #[test]
    fn test_no_legacy_returns_none() {
        let dir = TempDir::new().unwrap();
        assert!(migrate_legacy_config(dir.path()).is_none());
    }
}
