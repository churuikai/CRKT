use serde::Serialize;

#[derive(Clone, Debug, Serialize)]
pub struct LanguageInfo {
    pub code: String,
    pub name: String,
}

pub struct LanguageDetector;

impl LanguageDetector {
    pub fn detect(&self, text: &str) -> LanguageInfo {
        let mut cjk = 0u32;
        let mut cyrillic = 0u32;
        let mut latin = 0u32;

        for ch in text.chars() {
            if Self::is_cjk(ch) {
                cjk += 1;
            } else if Self::is_cyrillic(ch) {
                cyrillic += 1;
            } else if Self::is_latin(ch) {
                latin += 1;
            }
        }

        if cjk > latin && cjk > cyrillic {
            LanguageInfo { code: "zh".into(), name: "中文".into() }
        } else if cyrillic > latin {
            LanguageInfo { code: "ru".into(), name: "俄语".into() }
        } else {
            LanguageInfo { code: "en".into(), name: "英语".into() }
        }
    }

    pub fn get_target_language(&self, source: &LanguageInfo, configured_target: &str) -> LanguageInfo {
        if source.name == configured_target {
            // Source and target are the same language — default to English
            return LanguageInfo { code: "en".into(), name: "英语".into() };
        }
        Self::language_from_name(configured_target)
    }

    fn language_from_name(name: &str) -> LanguageInfo {
        match name {
            "中文" => LanguageInfo { code: "zh".into(), name: "中文".into() },
            "英语" | "English" => LanguageInfo { code: "en".into(), name: "英语".into() },
            "俄语" => LanguageInfo { code: "ru".into(), name: "俄语".into() },
            "日语" => LanguageInfo { code: "ja".into(), name: "日语".into() },
            _ => LanguageInfo { code: "zh".into(), name: "中文".into() },
        }
    }

    fn is_cjk(ch: char) -> bool {
        matches!(ch as u32,
            0x4E00..=0x9FFF
            | 0x3400..=0x4DBF
            | 0xF900..=0xFAFF
            | 0x3000..=0x303F
            | 0x3040..=0x309F
            | 0x30A0..=0x30FF
        )
    }

    fn is_cyrillic(ch: char) -> bool {
        matches!(ch as u32, 0x0400..=0x04FF | 0x0500..=0x052F)
    }

    fn is_latin(ch: char) -> bool {
        matches!(ch as u32, 0x0041..=0x005A | 0x0061..=0x007A | 0x00C0..=0x00FF)
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_detect_chinese() {
        let detector = LanguageDetector;
        let result = detector.detect("这是一段中文测试文本");
        assert_eq!(result.code, "zh");
    }

    #[test]
    fn test_detect_english() {
        let detector = LanguageDetector;
        let result = detector.detect("This is an English test string");
        assert_eq!(result.code, "en");
    }

    #[test]
    fn test_detect_cyrillic() {
        let detector = LanguageDetector;
        let result = detector.detect("Это тестовая строка на русском языке");
        assert_eq!(result.code, "ru");
    }

    #[test]
    fn test_detect_mixed_chinese_dominant() {
        let detector = LanguageDetector;
        let result = detector.detect("这是一段包含了 some English 的中文文本");
        assert_eq!(result.code, "zh");
    }

    #[test]
    fn test_auto_swap_chinese_source_chinese_target() {
        let detector = LanguageDetector;
        let source = LanguageInfo { code: "zh".into(), name: "中文".into() };
        let target = detector.get_target_language(&source, "中文");
        assert_eq!(target.code, "en");
    }

    #[test]
    fn test_same_language_defaults_to_english() {
        let detector = LanguageDetector;
        // When source == target, always default to English
        let source = LanguageInfo { code: "en".into(), name: "英语".into() };
        let target = detector.get_target_language(&source, "英语");
        assert_eq!(target.code, "en");
        assert_eq!(target.name, "英语");

        let source = LanguageInfo { code: "ru".into(), name: "俄语".into() };
        let target = detector.get_target_language(&source, "俄语");
        assert_eq!(target.code, "en");
        assert_eq!(target.name, "英语");
    }

    #[test]
    fn test_no_swap_when_different() {
        let detector = LanguageDetector;
        let source = LanguageInfo { code: "en".into(), name: "英语".into() };
        let target = detector.get_target_language(&source, "中文");
        assert_eq!(target.code, "zh");
    }
}
