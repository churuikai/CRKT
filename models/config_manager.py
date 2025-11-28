"""Configuration management module."""

import json
import os
import sys
from typing import Optional, Callable, List

from core.logger import get_logger
from core.types import AppConfig, APIProfile, Skill, HotkeyConfig

logger = get_logger("ConfigManager")


class ConfigManager:
    """配置管理器，负责加载、保存和管理应用配置。"""
    
    DEFAULT_PROMPT = (
        "你将作为一个专业的翻译助手，任务是将{source_language}翻译成{target_language}\n"
        "翻译时需要遵循以下要求：\n"
        "1. 准确性：确保翻译内容的准确性，保留专业术语和专有名词，用反引号`标出。\n"
        "2. 格式要求：使用 Markdown 语法输出内容。\n"
        "3. 公式格式：任何时候所有公式、数学字母都必须使用四个$包围，忽略任何tag和序号。\n"
        "4. 使用常见字符: 任何公式中不常见的字符替换成常见标准的字符，输出latex代码，确保katex可以解析，例如:\n"
        "   - '𝑆'换成'S', '𝐹'换成'F', '𝑛'换成'n', 'i'换成i\n"
        "   - '...' 换成 '\\cdots', '.'换成 '\\cdot'\n"
        "5. 注意，如果是单个单词或短语，你可以精炼地道的解释该单词/短语的含义，给出音标和简单例证。\n"
        "不要给出多余输出，直接翻译以下内容：\n{selected_text}"
    )
    
    def __init__(self, app_dir: str):
        """
        初始化配置管理器。
        
        Args:
            app_dir: 应用程序目录
        """
        self._app_dir = app_dir
        self._data_dir = os.path.join(app_dir, "data")
        self._config_path = os.path.join(self._data_dir, "config.json")
        self._config: Optional[AppConfig] = None
        self._observers: List[Callable[[AppConfig], None]] = []
        
        self._ensure_data_dir()
    
    def _ensure_data_dir(self) -> None:
        """确保数据目录存在。"""
        if not os.path.exists(self._data_dir):
            os.makedirs(self._data_dir)
            logger.info(f"创建数据目录: {self._data_dir}")
    
    @property
    def data_dir(self) -> str:
        """返回数据目录路径。"""
        return self._data_dir
    
    @property
    def config(self) -> AppConfig:
        """获取当前配置。"""
        if self._config is None:
            self._config = self._load_config()
        return self._config
    
    def add_observer(self, callback: Callable[[AppConfig], None]) -> None:
        """添加配置变更观察者。"""
        self._observers.append(callback)
    
    def remove_observer(self, callback: Callable[[AppConfig], None]) -> None:
        """移除配置变更观察者。"""
        if callback in self._observers:
            self._observers.remove(callback)
    
    def _notify_observers(self) -> None:
        """通知所有观察者配置已变更。"""
        for observer in self._observers:
            try:
                observer(self._config)
            except Exception as e:
                logger.error(f"通知观察者时出错: {e}")
    
    def _get_default_config(self) -> AppConfig:
        """获取默认配置。"""
        return AppConfig(
            skills=[
                Skill(name="通用", prompt=self.DEFAULT_PROMPT),
                Skill(name="代码助手", prompt="请逐行解释代码，下面是代码：{selected_text}"),
            ],
            selected_skill="通用",
            api_profiles=[
                APIProfile(
                    name="默认API",
                    api_key="",
                    base_url="https://api.openai.com/v1/",
                ),
            ],
            selected_api="默认API",
            models=[
                "gpt-4.1-nano", "gpt-4o-mini", "gpt-4o",
                "gemini-2.5-flash", "doubao-lite-32k",
                "deepseek-chat"
            ],
            selected_model="gpt-4.1-nano",
            translate_hotkey=HotkeyConfig("ctrl", True),
            append_hotkey=HotkeyConfig("shift", True),
            start_on_boot=False,
            target_language="English",
            prompt=self.DEFAULT_PROMPT,
            show_source_comparison=False,
        )
    
    def _load_config(self) -> AppConfig:
        """从文件加载配置。"""
        default_config = self._get_default_config()
        
        try:
            if os.path.exists(self._config_path):
                with open(self._config_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                # 合并默认配置中缺失的字段
                default_dict = default_config.to_dict()
                for key, value in default_dict.items():
                    if key not in data:
                        data[key] = value
                
                config = AppConfig.from_dict(data)
                self._sync_selected_skill_prompt(config)
                logger.info("配置加载成功")
                return config
            else:
                self._save_config(default_config)
                logger.info("创建默认配置")
                return default_config
                
        except Exception as e:
            logger.error(f"加载配置文件出错: {e}")
            return default_config
    
    def _sync_selected_skill_prompt(self, config: AppConfig) -> None:
        """同步当前选中技能的提示词到prompt配置。"""
        skill = config.get_selected_skill()
        
        if skill:
            config.prompt = skill.prompt
            if config.selected_skill != skill.name:
                config.selected_skill = skill.name
                logger.warning(f"未找到选中的技能，使用: {skill.name}")
        else:
            logger.warning("技能列表为空，使用默认提示词")
            config.prompt = "Translate the following text: {selected_text}"
            config.selected_skill = "通用翻译"
            config.skills = [Skill(name="通用翻译", prompt=config.prompt)]
    
    def _save_config(self, config: Optional[AppConfig] = None) -> bool:
        """
        保存配置到文件。
        
        Args:
            config: 要保存的配置，如果为None则保存当前配置
            
        Returns:
            是否保存成功
        """
        try:
            if config is None:
                config = self._config
            if config is None:
                return False
                
            with open(self._config_path, 'w', encoding='utf-8') as f:
                json.dump(config.to_dict(), f, ensure_ascii=False, indent=2)
            
            logger.debug("配置保存成功")
            return True
        except Exception as e:
            logger.error(f"保存配置文件出错: {e}")
            return False
    
    def update_config(self, **kwargs) -> None:
        """
        更新配置项。
        
        Args:
            **kwargs: 要更新的配置键值对
        """
        config = self.config
        
        for key, value in kwargs.items():
            if hasattr(config, key):
                setattr(config, key, value)
        
        # 如果更新了selected_skill，同步prompt
        if "selected_skill" in kwargs:
            self._sync_selected_skill_prompt(config)
        
        self._save_config()
        self._notify_observers()
    
    def update_from_dict(self, data: dict) -> None:
        """
        从字典更新配置。
        
        Args:
            data: 配置数据字典
        """
        config = self.config
        
        if "api_profiles" in data:
            config.api_profiles = [APIProfile.from_dict(p) for p in data["api_profiles"]]
        if "selected_api" in data:
            config.selected_api = data["selected_api"]
        if "models" in data:
            config.models = data["models"].copy()
        if "selected_model" in data:
            config.selected_model = data["selected_model"]
        if "skills" in data:
            config.skills = [Skill.from_dict(s) for s in data["skills"]]
        if "selected_skill" in data:
            config.selected_skill = data["selected_skill"]
        if "target_language" in data:
            config.target_language = data["target_language"]
        if "translate_hotkey" in data:
            config.translate_hotkey = HotkeyConfig.from_dict(data["translate_hotkey"])
        if "append_hotkey" in data:
            config.append_hotkey = HotkeyConfig.from_dict(data["append_hotkey"])
        if "show_source_comparison" in data:
            config.show_source_comparison = data["show_source_comparison"]
        
        self._sync_selected_skill_prompt(config)
        self._save_config()
        self._notify_observers()
    
    def save(self) -> bool:
        """保存当前配置。"""
        return self._save_config()
