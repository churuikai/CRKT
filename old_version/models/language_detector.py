"""Language detection module."""

import re
from typing import Tuple, Dict

from core.logger import get_logger
from core.types import LanguageInfo

logger = get_logger("LanguageDetector")


class LanguageDetector:
    """语言检测器，负责检测文本语言和确定目标语言。"""
    
    # 语言映射表（支持英文和本地名称作为键）
    LANGUAGE_MAP: Dict[str, Tuple[str, str]] = {
        # 英文键
        "English": ("English", "English"),
        "Chinese": ("Chinese", "中文"),
        "Japanese": ("Japanese", "日本語"),
        "Korean": ("Korean", "한국어"),
        "French": ("French", "Français"),
        "German": ("German", "Deutsch"),
        "Spanish": ("Spanish", "Español"),
        "Russian": ("Russian", "Русский"),
        # 本地名称键
        "中文": ("Chinese", "中文"),
        "日本語": ("Japanese", "日本語"),
        "한국어": ("Korean", "한국어"),
        "Français": ("French", "Français"),
        "Deutsch": ("German", "Deutsch"),
        "Español": ("Spanish", "Español"),
        "Русский": ("Russian", "Русский"),
    }
    
    def detect(self, text: str) -> LanguageInfo:
        """
        检测文本的语言。
        
        Args:
            text: 要检测的文本
            
        Returns:
            语言信息
        """
        # 检查是否包含中文字符
        if re.search(r'[\u4e00-\u9fff]', text):
            return LanguageInfo(code="Chinese", native="中文")
        
        # 日语（平假名、片假名）
        if re.search(r'[\u3040-\u309f\u30a0-\u30ff]', text):
            return LanguageInfo(code="Japanese", native="日本語")
        
        # 韩语
        if re.search(r'[\uac00-\ud7af]', text):
            return LanguageInfo(code="Korean", native="한국어")
        
        # 俄语
        if re.search(r'[\u0400-\u04ff]', text):
            return LanguageInfo(code="Russian", native="Русский")
        
        # 默认为英语
        return LanguageInfo(code="English", native="English")
    
    def get_target_language(
        self,
        source_lang: LanguageInfo,
        configured_target: str,
    ) -> LanguageInfo:
        """
        确定目标语言。
        
        根据源语言和用户配置的目标语言，智能选择实际的翻译目标语言。
        如果源语言与目标语言相同，则自动切换。
        
        Args:
            source_lang: 源语言信息
            configured_target: 用户配置的目标语言
            
        Returns:
            目标语言信息
        """
        # 获取配置目标语言的标准化信息
        target_tuple = self.LANGUAGE_MAP.get(configured_target)
        target_code = target_tuple[0] if target_tuple else configured_target
        
        # 如果源语言与配置的目标语言一致，自动切换
        if source_lang.code == target_code:
            # 如果源语言是英文，则翻译为中文
            if source_lang.code == "English":
                return LanguageInfo(code="Chinese", native="中文")
            else:
                # 否则翻译为英文
                return LanguageInfo(code="English", native="English")
        
        # 使用用户配置的目标语言
        if target_tuple:
            return LanguageInfo(code=target_tuple[0], native=target_tuple[1])
        else:
            # 回退到英语
            return LanguageInfo(code="English", native="English")
