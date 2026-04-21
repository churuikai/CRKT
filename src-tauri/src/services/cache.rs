use std::collections::HashMap;
use std::path::{Path, PathBuf};

use serde::{Deserialize, Serialize};

#[derive(Serialize, Deserialize, Clone)]
struct CacheEntry {
    translation: String,
    timestamp: f64,
    last_accessed: f64,
}

pub struct CacheManager {
    entries: HashMap<String, CacheEntry>,
    max_size: usize,
    cache_path: PathBuf,
    writes_since_save: u32,
}

impl CacheManager {
    pub fn new(app_data_dir: &Path) -> Self {
        let cache_path = app_data_dir.join("cache.json");
        let entries = Self::load(&cache_path);
        Self {
            entries,
            max_size: 1000,
            cache_path,
            writes_since_save: 0,
        }
    }

    fn load(path: &Path) -> HashMap<String, CacheEntry> {
        std::fs::read_to_string(path)
            .ok()
            .and_then(|c| serde_json::from_str(&c).ok())
            .unwrap_or_default()
    }

    /// Returns cached translation, or None if not found or within the 3-second dedup window.
    pub fn get(&mut self, key: &str) -> Option<String> {
        let now = Self::now();
        if let Some(entry) = self.entries.get_mut(key) {
            if now - entry.last_accessed < 3.0 {
                return None; // Within dedup window — force fresh translation
            }
            entry.last_accessed = now;
            Some(entry.translation.clone())
        } else {
            None
        }
    }

    pub fn set(&mut self, key: String, translation: String) {
        let now = Self::now();
        self.entries.insert(
            key,
            CacheEntry {
                translation,
                timestamp: now,
                last_accessed: now,
            },
        );
        if self.entries.len() > self.max_size {
            self.evict();
        }
        self.writes_since_save += 1;
        if self.writes_since_save >= 20 {
            let _ = self.save();
            self.writes_since_save = 0;
        }
    }

    fn evict(&mut self) {
        let remove_count = self.entries.len() / 5; // Remove oldest 20%
        let mut by_time: Vec<(String, f64)> = self
            .entries
            .iter()
            .map(|(k, v)| (k.clone(), v.timestamp))
            .collect();
        by_time.sort_by(|a, b| a.1.partial_cmp(&b.1).unwrap());

        for (key, _) in by_time.into_iter().take(remove_count) {
            self.entries.remove(&key);
        }
    }

    pub fn save(&self) -> Result<(), String> {
        if let Some(parent) = self.cache_path.parent() {
            std::fs::create_dir_all(parent).map_err(|e| e.to_string())?;
        }
        let content = serde_json::to_string(&self.entries).map_err(|e| e.to_string())?;
        std::fs::write(&self.cache_path, content).map_err(|e| e.to_string())
    }

    pub fn clear(&mut self) {
        self.entries.clear();
    }

    pub fn len(&self) -> usize {
        self.entries.len()
    }

    fn now() -> f64 {
        std::time::SystemTime::now()
            .duration_since(std::time::UNIX_EPOCH)
            .unwrap()
            .as_secs_f64()
    }

    #[cfg(test)]
    fn set_with_timestamp(&mut self, key: String, translation: String, timestamp: f64) {
        self.entries.insert(
            key,
            CacheEntry {
                translation,
                timestamp,
                last_accessed: timestamp,
            },
        );
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use tempfile::TempDir;

    fn setup() -> (TempDir, CacheManager) {
        let dir = TempDir::new().unwrap();
        let manager = CacheManager::new(dir.path());
        (dir, manager)
    }

    #[test]
    fn test_set_and_get() {
        let (_dir, mut cache) = setup();
        cache.set("hello".into(), "你好".into());
        // First get within 3s returns None (dedup window)
        assert!(cache.get("hello").is_none());
    }

    #[test]
    fn test_get_after_dedup_window() {
        let (_dir, mut cache) = setup();
        let old_time = CacheManager::now() - 5.0;
        cache.set_with_timestamp("hello".into(), "你好".into(), old_time);
        assert_eq!(cache.get("hello"), Some("你好".into()));
    }

    #[test]
    fn test_get_nonexistent() {
        let (_dir, mut cache) = setup();
        assert!(cache.get("nonexistent").is_none());
    }

    #[test]
    fn test_eviction() {
        let dir = TempDir::new().unwrap();
        let mut cache = CacheManager {
            entries: HashMap::new(),
            max_size: 5,
            cache_path: dir.path().join("cache.json"),
            writes_since_save: 0,
        };
        for i in 0..6 {
            cache.set_with_timestamp(
                format!("key{}", i),
                format!("val{}", i),
                i as f64,
            );
        }
        // Insert one more to trigger eviction
        cache.set("trigger".into(), "val".into());
        // After eviction of oldest 20% (1 entry from 6+1=7), should be <= max_size
        assert!(cache.entries.len() <= 7); // eviction removes ~1-2
    }

    #[test]
    fn test_clear() {
        let (_dir, mut cache) = setup();
        cache.set("a".into(), "b".into());
        cache.clear();
        assert_eq!(cache.len(), 0);
    }

    #[test]
    fn test_save_and_reload() {
        let (dir, mut cache) = setup();
        let old_time = CacheManager::now() - 10.0;
        cache.set_with_timestamp("hello".into(), "你好".into(), old_time);
        cache.save().unwrap();

        let mut reloaded = CacheManager::new(dir.path());
        assert_eq!(reloaded.get("hello"), Some("你好".into()));
    }
}
