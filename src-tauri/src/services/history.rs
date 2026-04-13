use std::path::{Path, PathBuf};

use crate::types::TranslationRecord;

pub struct HistoryManager {
    records: Vec<TranslationRecord>,
    pointer: i32, // -1 = current mode, >= 0 = history index
    max_records: usize,
    history_path: PathBuf,
}

impl HistoryManager {
    pub fn new(app_data_dir: &Path) -> Self {
        let history_path = app_data_dir.join("history.json");
        let records = Self::load(&history_path);
        Self {
            records,
            pointer: -1,
            max_records: 1000,
            history_path,
        }
    }

    fn load(path: &Path) -> Vec<TranslationRecord> {
        std::fs::read_to_string(path)
            .ok()
            .and_then(|c| serde_json::from_str(&c).ok())
            .unwrap_or_default()
    }

    pub fn save(&self) -> Result<(), String> {
        if let Some(parent) = self.history_path.parent() {
            std::fs::create_dir_all(parent).map_err(|e| e.to_string())?;
        }
        let content = serde_json::to_string(&self.records).map_err(|e| e.to_string())?;
        std::fs::write(&self.history_path, content).map_err(|e| e.to_string())
    }

    pub fn add_record(&mut self, record: TranslationRecord) {
        self.records.push(record);
        if self.records.len() > self.max_records {
            self.records.remove(0);
        }
        self.pointer = -1;
    }

    /// Navigate to an older record. Returns the record if available.
    pub fn navigate_up(&mut self) -> Option<&TranslationRecord> {
        if self.records.is_empty() {
            return None;
        }
        if self.pointer == -1 {
            self.pointer = (self.records.len() as i32) - 1;
        } else if self.pointer > 0 {
            self.pointer -= 1;
        } else {
            return None; // Already at oldest
        }
        self.records.get(self.pointer as usize)
    }

    /// Navigate to a newer record. Returns None when back to current mode.
    pub fn navigate_down(&mut self) -> Option<&TranslationRecord> {
        if self.pointer == -1 {
            return None;
        }
        self.pointer += 1;
        if self.pointer >= self.records.len() as i32 {
            self.pointer = -1;
            None
        } else {
            self.records.get(self.pointer as usize)
        }
    }

    pub fn is_in_history_mode(&self) -> bool {
        self.pointer >= 0
    }

    pub fn exit_history_mode(&mut self) {
        self.pointer = -1;
    }

    pub fn get_pointer(&self) -> i32 {
        self.pointer
    }

    pub fn records(&self) -> &[TranslationRecord] {
        &self.records
    }

    pub fn clear(&mut self) {
        self.records.clear();
        self.pointer = -1;
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use tempfile::TempDir;

    fn make_record(text: &str) -> TranslationRecord {
        TranslationRecord {
            id: uuid::Uuid::new_v4().to_string(),
            source_text: text.to_string(),
            translated_text: format!("translated_{}", text),
            source_language: "en".into(),
            target_language: "zh".into(),
            timestamp: chrono::Utc::now().to_rfc3339(),
            model: "test".into(),
            skill: "通用".into(),
        }
    }

    #[test]
    fn test_add_and_list() {
        let dir = TempDir::new().unwrap();
        let mut history = HistoryManager::new(dir.path());
        history.add_record(make_record("hello"));
        history.add_record(make_record("world"));
        assert_eq!(history.records().len(), 2);
    }

    #[test]
    fn test_navigate_up_from_current() {
        let dir = TempDir::new().unwrap();
        let mut history = HistoryManager::new(dir.path());
        history.add_record(make_record("first"));
        history.add_record(make_record("second"));
        history.add_record(make_record("third"));

        let record = history.navigate_up().unwrap();
        assert_eq!(record.source_text, "third");

        let record = history.navigate_up().unwrap();
        assert_eq!(record.source_text, "second");

        let record = history.navigate_up().unwrap();
        assert_eq!(record.source_text, "first");

        assert!(history.navigate_up().is_none());
    }

    #[test]
    fn test_navigate_down_back_to_current() {
        let dir = TempDir::new().unwrap();
        let mut history = HistoryManager::new(dir.path());
        history.add_record(make_record("first"));
        history.add_record(make_record("second"));

        history.navigate_up(); // "second"
        history.navigate_up(); // "first"

        let record = history.navigate_down().unwrap();
        assert_eq!(record.source_text, "second");

        assert!(history.navigate_down().is_none());
        assert!(!history.is_in_history_mode());
    }

    #[test]
    fn test_navigate_up_empty() {
        let dir = TempDir::new().unwrap();
        let mut history = HistoryManager::new(dir.path());
        assert!(history.navigate_up().is_none());
    }

    #[test]
    fn test_add_resets_pointer() {
        let dir = TempDir::new().unwrap();
        let mut history = HistoryManager::new(dir.path());
        history.add_record(make_record("first"));
        history.navigate_up();
        assert!(history.is_in_history_mode());

        history.add_record(make_record("second"));
        assert!(!history.is_in_history_mode());
    }

    #[test]
    fn test_max_records() {
        let dir = TempDir::new().unwrap();
        let mut history = HistoryManager {
            records: Vec::new(),
            pointer: -1,
            max_records: 3,
            history_path: dir.path().join("history.json"),
        };
        for i in 0..5 {
            history.add_record(make_record(&format!("record_{}", i)));
        }
        assert_eq!(history.records().len(), 3);
        assert_eq!(history.records()[0].source_text, "record_2");
    }

    #[test]
    fn test_save_and_reload() {
        let dir = TempDir::new().unwrap();
        let mut history = HistoryManager::new(dir.path());
        history.add_record(make_record("persistent"));
        history.save().unwrap();

        let reloaded = HistoryManager::new(dir.path());
        assert_eq!(reloaded.records().len(), 1);
        assert_eq!(reloaded.records()[0].source_text, "persistent");
    }
}
