use serde::{Deserialize, Serialize};

#[derive(Serialize, Deserialize, Clone, Debug, PartialEq)]
pub struct AppConfig {
    pub skills: Vec<Skill>,
    pub selected_skill: String,
    pub api_profiles: Vec<ApiProfile>,
    pub selected_api: String,
    pub models: Vec<String>,
    pub selected_model: String,
    pub translate_shortcut: String,
    pub append_shortcut: String,
    pub start_on_boot: bool,
    pub target_language: String,
    pub show_source_comparison: bool,
}

#[derive(Serialize, Deserialize, Clone, Debug, PartialEq)]
pub struct ApiProfile {
    pub name: String,
    pub api_key: String,
    pub base_url: String,
}

#[derive(Serialize, Deserialize, Clone, Debug, PartialEq)]
pub struct Skill {
    pub name: String,
    pub prompt: String,
}

#[derive(Serialize, Deserialize, Clone, Debug, PartialEq)]
pub struct TranslationRecord {
    pub id: String,
    pub source_text: String,
    pub translated_text: String,
    pub source_language: String,
    pub target_language: String,
    pub timestamp: String,
    pub model: String,
    pub skill: String,
}

pub const DEFAULT_PROMPT: &str = "You are a professional academic translator, tasked with translating from {source_language} to {target_language}.\n\n\
Basic Requirements:\n\
1. Format Requirement: Ignore input formatting. Output in Markdown format (directly, not in a code block).\n\
2. Retain Proper Nouns and Terminology, marking them with `.\n\n\
Extended Requirements:\n\
1. Formula Formatting: Ignore input formula formatting, tags, and numbering. Output formulas and mathematical symbols using LaTeX format, enclosed in double dollar signs ($$…$$), for example, $$r_t > 1$$.\n\
2. Use Standard Characters: Replace uncommon characters in input formulas (resulting from PDF copying or OCR scanning) with standard characters and LaTeX code.\n\n\
Input:\n\n\
{selected_text}\n\n\
Please output the result only:\n";

pub const CODE_PROMPT: &str = "请逐行解释代码，下面是代码：{selected_text}";

impl Default for AppConfig {
    fn default() -> Self {
        Self {
            skills: vec![
                Skill {
                    name: "通用".to_string(),
                    prompt: DEFAULT_PROMPT.to_string(),
                },
                Skill {
                    name: "代码助手".to_string(),
                    prompt: CODE_PROMPT.to_string(),
                },
            ],
            selected_skill: "通用".to_string(),
            api_profiles: vec![ApiProfile {
                name: "默认API".to_string(),
                api_key: String::new(),
                base_url: "https://api.openai.com/v1/".to_string(),
            }],
            selected_api: "默认API".to_string(),
            models: vec![
                "gpt-4o-mini".to_string(),
                "gemini-2.5-flash-lite".to_string(),
                "claude-4-5-haiku".to_string(),
                "deepseek-chat".to_string(),
            ],
            selected_model: "gpt-4o-mini".to_string(),
            translate_shortcut: "CmdOrCtrl+Shift+T".to_string(),
            append_shortcut: "CmdOrCtrl+Shift+A".to_string(),
            start_on_boot: false,
            target_language: "中文".to_string(),
            show_source_comparison: false,
        }
    }
}

impl AppConfig {
    pub fn get_selected_api_profile(&self) -> Option<&ApiProfile> {
        self.api_profiles.iter().find(|p| p.name == self.selected_api)
    }

    pub fn get_selected_skill_prompt(&self) -> Option<&str> {
        self.skills
            .iter()
            .find(|s| s.name == self.selected_skill)
            .map(|s| s.prompt.as_str())
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_app_config_serialization_roundtrip() {
        let config = AppConfig::default();
        let json = serde_json::to_string(&config).unwrap();
        let deserialized: AppConfig = serde_json::from_str(&json).unwrap();
        assert_eq!(config, deserialized);
    }

    #[test]
    fn test_translation_record_serialization() {
        let record = TranslationRecord {
            id: "abc-123".to_string(),
            source_text: "hello".to_string(),
            translated_text: "你好".to_string(),
            source_language: "en".to_string(),
            target_language: "zh".to_string(),
            timestamp: "2026-04-12T00:00:00Z".to_string(),
            model: "gpt-4o-mini".to_string(),
            skill: "通用".to_string(),
        };
        let json = serde_json::to_string(&record).unwrap();
        let deserialized: TranslationRecord = serde_json::from_str(&json).unwrap();
        assert_eq!(record, deserialized);
    }

    #[test]
    fn test_get_selected_api_profile() {
        let config = AppConfig::default();
        let profile = config.get_selected_api_profile().unwrap();
        assert_eq!(profile.name, "默认API");
    }

    #[test]
    fn test_get_selected_skill_prompt() {
        let config = AppConfig::default();
        let prompt = config.get_selected_skill_prompt().unwrap();
        assert!(prompt.contains("{source_language}"));
    }
}
