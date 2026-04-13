use std::path::{Path, PathBuf};

use crate::types::AppConfig;

pub struct ConfigManager {
    config: AppConfig,
    config_path: PathBuf,
}

impl ConfigManager {
    pub fn new(app_data_dir: &Path) -> Self {
        let config_path = app_data_dir.join("config.json");
        let config = Self::load_or_default(&config_path);
        Self { config, config_path }
    }

    fn load_or_default(path: &Path) -> AppConfig {
        match std::fs::read_to_string(path) {
            Ok(content) => serde_json::from_str(&content).unwrap_or_default(),
            Err(_) => AppConfig::default(),
        }
    }

    pub fn config(&self) -> &AppConfig {
        &self.config
    }

    pub fn save(&self) -> Result<(), String> {
        if let Some(parent) = self.config_path.parent() {
            std::fs::create_dir_all(parent).map_err(|e| e.to_string())?;
        }
        let content = serde_json::to_string_pretty(&self.config).map_err(|e| e.to_string())?;
        std::fs::write(&self.config_path, content).map_err(|e| e.to_string())
    }

    pub fn update(&mut self, new_config: AppConfig) -> Result<(), String> {
        self.config = new_config;
        self.save()
    }

    pub fn update_field(&mut self, updater: impl FnOnce(&mut AppConfig)) -> Result<(), String> {
        updater(&mut self.config);
        self.save()
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use tempfile::TempDir;

    fn setup() -> (TempDir, ConfigManager) {
        let dir = TempDir::new().unwrap();
        let manager = ConfigManager::new(dir.path());
        (dir, manager)
    }

    #[test]
    fn test_new_returns_defaults_when_no_file() {
        let (_dir, manager) = setup();
        assert_eq!(manager.config().selected_model, "gpt-4o-mini");
        assert_eq!(manager.config().skills.len(), 2);
    }

    #[test]
    fn test_save_and_reload() {
        let (dir, mut manager) = setup();
        manager.config.selected_model = "deepseek-chat".to_string();
        manager.save().unwrap();

        let reloaded = ConfigManager::new(dir.path());
        assert_eq!(reloaded.config().selected_model, "deepseek-chat");
    }

    #[test]
    fn test_update_persists() {
        let (dir, mut manager) = setup();
        let mut new_config = manager.config().clone();
        new_config.target_language = "English".to_string();
        manager.update(new_config).unwrap();

        let reloaded = ConfigManager::new(dir.path());
        assert_eq!(reloaded.config().target_language, "English");
    }

    #[test]
    fn test_update_field() {
        let (dir, mut manager) = setup();
        manager
            .update_field(|c| c.show_source_comparison = true)
            .unwrap();

        let reloaded = ConfigManager::new(dir.path());
        assert!(reloaded.config().show_source_comparison);
    }

    #[test]
    fn test_corrupted_file_returns_defaults() {
        let dir = TempDir::new().unwrap();
        std::fs::write(dir.path().join("config.json"), "NOT JSON").unwrap();
        let manager = ConfigManager::new(dir.path());
        assert_eq!(manager.config().selected_model, "gpt-4o-mini");
    }
}
