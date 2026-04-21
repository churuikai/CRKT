"""Type definitions for the application."""

from dataclasses import dataclass, field
from typing import List, Optional, Callable, Any
from datetime import datetime


@dataclass
class APIProfile:
    """API配置信息。"""
    name: str
    api_key: str
    base_url: str
    
    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "api_key": self.api_key,
            "base_url": self.base_url,
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> "APIProfile":
        return cls(
            name=data.get("name", ""),
            api_key=data.get("api_key", ""),
            base_url=data.get("base_url", ""),
        )


@dataclass
class Skill:
    """提示词技能配置。"""
    name: str
    prompt: str
    
    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "prompt": self.prompt,
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> "Skill":
        return cls(
            name=data.get("name", ""),
            prompt=data.get("prompt", ""),
        )


@dataclass
class HotkeyConfig:
    """热键配置。"""
    key: str           # 热键名称，如 "ctrl", "shift", "alt"
    enabled: bool      # 是否启用
    
    def to_dict(self) -> dict:
        return {
            "key": self.key,
            "enabled": self.enabled,
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> "HotkeyConfig":
        return cls(
            key=data.get("key", "ctrl"),
            enabled=data.get("enabled", True),
        )


@dataclass
class LanguageInfo:
    """语言信息。"""
    code: str       # 英文代码，如 "Chinese"
    native: str     # 本地名称，如 "中文"


@dataclass
class TranslationRequest:
    """翻译请求。"""
    text: str
    source_language: LanguageInfo
    target_language: LanguageInfo
    prompt_template: str
    api_key: str
    base_url: str
    model: str


@dataclass
class TranslationResult:
    """翻译结果。"""
    success: bool
    content: str
    error: Optional[str] = None
    from_cache: bool = False


@dataclass
class TranslationRecord:
    """翻译记录，保存原文-翻译对应关系。"""
    id: str                          # 唯一标识符
    source_text: str                 # 原文
    translated_text: str             # 翻译结果
    source_language: str             # 源语言代码
    target_language: str             # 目标语言代码
    timestamp: str                   # 创建时间 ISO格式
    model: str = ""                  # 使用的模型
    skill: str = ""                  # 使用的技能名称
    
    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "source_text": self.source_text,
            "translated_text": self.translated_text,
            "source_language": self.source_language,
            "target_language": self.target_language,
            "timestamp": self.timestamp,
            "model": self.model,
            "skill": self.skill,
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> "TranslationRecord":
        return cls(
            id=data.get("id", ""),
            source_text=data.get("source_text", ""),
            translated_text=data.get("translated_text", ""),
            source_language=data.get("source_language", ""),
            target_language=data.get("target_language", ""),
            timestamp=data.get("timestamp", ""),
            model=data.get("model", ""),
            skill=data.get("skill", ""),
        )
    
    @classmethod
    def create(
        cls,
        source_text: str,
        translated_text: str,
        source_language: str,
        target_language: str,
        model: str = "",
        skill: str = "",
    ) -> "TranslationRecord":
        """创建新的翻译记录。"""
        import uuid
        return cls(
            id=str(uuid.uuid4()),
            source_text=source_text,
            translated_text=translated_text,
            source_language=source_language,
            target_language=target_language,
            timestamp=datetime.now().isoformat(),
            model=model,
            skill=skill,
        )


@dataclass
class AppConfig:
    """应用程序配置。"""
    skills: List[Skill] = field(default_factory=list)
    selected_skill: str = ""
    api_profiles: List[APIProfile] = field(default_factory=list)
    selected_api: str = ""
    models: List[str] = field(default_factory=list)
    selected_model: str = ""
    # 热键配置
    translate_hotkey: HotkeyConfig = field(default_factory=lambda: HotkeyConfig("ctrl", True))
    append_hotkey: HotkeyConfig = field(default_factory=lambda: HotkeyConfig("shift", True))
    start_on_boot: bool = False
    target_language: str = "English"
    prompt: str = ""
    # 显示配置
    show_source_comparison: bool = False  # 原文对照模式
    
    def to_dict(self) -> dict:
        return {
            "skills": [s.to_dict() for s in self.skills],
            "selected_skill": self.selected_skill,
            "api_profiles": [p.to_dict() for p in self.api_profiles],
            "selected_api": self.selected_api,
            "models": self.models.copy(),
            "selected_model": self.selected_model,
            "translate_hotkey": self.translate_hotkey.to_dict(),
            "append_hotkey": self.append_hotkey.to_dict(),
            "start_on_boot": self.start_on_boot,
            "target_language": self.target_language,
            "prompt": self.prompt,
            "show_source_comparison": self.show_source_comparison,
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> "AppConfig":
        # 兼容旧配置：shift_listener -> append_hotkey
        append_hotkey_data = data.get("append_hotkey")
        if append_hotkey_data is None:
            # 兼容旧配置
            shift_enabled = data.get("shift_listener", True)
            append_hotkey_data = {"key": "shift", "enabled": shift_enabled}
        
        translate_hotkey_data = data.get("translate_hotkey", {"key": "ctrl", "enabled": True})
        
        return cls(
            skills=[Skill.from_dict(s) for s in data.get("skills", [])],
            selected_skill=data.get("selected_skill", ""),
            api_profiles=[APIProfile.from_dict(p) for p in data.get("api_profiles", [])],
            selected_api=data.get("selected_api", ""),
            models=data.get("models", []).copy(),
            selected_model=data.get("selected_model", ""),
            translate_hotkey=HotkeyConfig.from_dict(translate_hotkey_data),
            append_hotkey=HotkeyConfig.from_dict(append_hotkey_data),
            start_on_boot=data.get("start_on_boot", False),
            target_language=data.get("target_language", "English"),
            prompt=data.get("prompt", ""),
            show_source_comparison=data.get("show_source_comparison", False),
        )
    
    def get_selected_skill(self) -> Optional[Skill]:
        """获取当前选中的技能。"""
        for skill in self.skills:
            if skill.name == self.selected_skill:
                return skill
        return self.skills[0] if self.skills else None
    
    def get_selected_api_profile(self) -> Optional[APIProfile]:
        """获取当前选中的API配置。"""
        for profile in self.api_profiles:
            if profile.name == self.selected_api:
                return profile
        return self.api_profiles[0] if self.api_profiles else None
