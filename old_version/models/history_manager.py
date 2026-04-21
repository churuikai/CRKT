"""Translation history management module."""

import json
import os
from typing import List, Optional, Callable
from datetime import datetime

from core.logger import get_logger
from core.types import TranslationRecord

logger = get_logger("HistoryManager")


class HistoryManager:
    """翻译历史记录管理器。
    
    负责管理原文-翻译对应关系的历史记录，支持持久化存储。
    """
    
    MAX_RECORDS = 1000  # 最大记录数
    
    def __init__(self, history_path: str):
        """
        初始化历史管理器。
        
        Args:
            history_path: 历史记录文件路径
        """
        self._history_path = history_path
        self._records: List[TranslationRecord] = []
        self._observers: List[Callable[[TranslationRecord], None]] = []
        self._history_pointer = -1  # -1表示当前模式，>=0表示历史模式
        
        self._load()
        logger.info(f"历史管理器初始化完成，已加载 {len(self._records)} 条记录")
    
    def _load(self) -> None:
        """从文件加载历史记录。"""
        try:
            if os.path.exists(self._history_path):
                with open(self._history_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                self._records = [
                    TranslationRecord.from_dict(r) 
                    for r in data.get("records", [])
                ]
                
                logger.debug(f"加载了 {len(self._records)} 条历史记录")
        except Exception as e:
            logger.error(f"加载历史记录出错: {e}")
            self._records = []
    
    def save(self) -> bool:
        """
        保存历史记录到文件。
        
        Returns:
            是否保存成功
        """
        try:
            data = {
                "records": [r.to_dict() for r in self._records],
            }
            
            # 确保目录存在
            os.makedirs(os.path.dirname(self._history_path), exist_ok=True)
            
            with open(self._history_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            
            logger.debug("历史记录保存成功")
            return True
        except Exception as e:
            logger.error(f"保存历史记录出错: {e}")
            return False
    
    def add_observer(self, callback: Callable[[TranslationRecord], None]) -> None:
        """添加观察者，当新记录添加时通知。"""
        if callback not in self._observers:
            self._observers.append(callback)
    
    def remove_observer(self, callback: Callable[[TranslationRecord], None]) -> None:
        """移除观察者。"""
        if callback in self._observers:
            self._observers.remove(callback)
    
    def _notify_observers(self, record: TranslationRecord) -> None:
        """通知观察者新记录已添加。"""
        for observer in self._observers:
            try:
                observer(record)
            except Exception as e:
                logger.error(f"通知观察者时出错: {e}")
    
    # ==================== 历史记录管理 ====================
    
    def add_record(
        self,
        source_text: str,
        translated_text: str,
        source_language: str,
        target_language: str,
        model: str = "",
        skill: str = "",
    ) -> TranslationRecord:
        """
        添加新的翻译记录。
        
        Args:
            source_text: 原文
            translated_text: 翻译结果
            source_language: 源语言代码
            target_language: 目标语言代码
            model: 使用的模型
            skill: 使用的技能名称
            
        Returns:
            创建的翻译记录
        """
        record = TranslationRecord.create(
            source_text=source_text,
            translated_text=translated_text,
            source_language=source_language,
            target_language=target_language,
            model=model,
            skill=skill,
        )
        
        # 添加到记录列表（最新的在前）
        self._records.insert(0, record)
        
        # 限制记录数量
        if len(self._records) > self.MAX_RECORDS:
            self._records = self._records[:self.MAX_RECORDS]
        
        logger.info(f"添加翻译记录: {record.id[:8]}... ({source_language} -> {target_language})")
        
        # 自动保存
        self.save()
        
        # 通知观察者
        self._notify_observers(record)
        
        return record
    
    def get_record(self, record_id: str) -> Optional[TranslationRecord]:
        """
        根据ID获取记录。
        
        Args:
            record_id: 记录ID
            
        Returns:
            翻译记录，未找到返回None
        """
        for record in self._records:
            if record.id == record_id:
                return record
        return None
    
    def get_records(
        self,
        limit: int = 50,
        offset: int = 0,
    ) -> List[TranslationRecord]:
        """
        获取历史记录列表。
        
        Args:
            limit: 返回数量限制
            offset: 偏移量
            
        Returns:
            翻译记录列表
        """
        return self._records[offset:offset + limit]
    
    def get_latest_record(self) -> Optional[TranslationRecord]:
        """获取最新的翻译记录。"""
        return self._records[0] if self._records else None
    
    def search_records(
        self,
        keyword: str,
        limit: int = 50,
    ) -> List[TranslationRecord]:
        """
        搜索历史记录。
        
        Args:
            keyword: 搜索关键词
            limit: 返回数量限制
            
        Returns:
            匹配的翻译记录列表
        """
        keyword_lower = keyword.lower()
        results = []
        
        for record in self._records:
            if (keyword_lower in record.source_text.lower() or 
                keyword_lower in record.translated_text.lower()):
                results.append(record)
                if len(results) >= limit:
                    break
        
        return results
    
    def delete_record(self, record_id: str) -> bool:
        """
        删除指定记录。
        
        Args:
            record_id: 记录ID
            
        Returns:
            是否删除成功
        """
        for i, record in enumerate(self._records):
            if record.id == record_id:
                del self._records[i]
                self.save()
                logger.info(f"已删除记录: {record_id[:8]}...")
                return True
        return False
    
    def clear_history(self) -> None:
        """清空所有历史记录。"""
        self._records = []
        self.save()
        logger.info("历史记录已清空")
    
    @property
    def record_count(self) -> int:
        """获取记录总数。"""
        return len(self._records)
    
    # ==================== 历史翻阅功能 ====================
    
    def navigate_up(self) -> Optional[TranslationRecord]:
        """
        上翻历史记录。
        
        Returns:
            翻阅到的历史记录，如果无法上翻返回None
        """
        if len(self._records) == 0:
            return None
        
        if self._history_pointer == -1:
            # 从当前模式进入历史模式
            self._history_pointer = 0
        elif self._history_pointer < len(self._records) - 1:
            # 在历史模式中继续上翻
            self._history_pointer += 1
        else:
            # 已经是最旧的记录
            return None
        
        logger.debug(f"上翻到历史记录: 指针={self._history_pointer}")
        return self._records[self._history_pointer]
    
    def navigate_down(self) -> Optional[TranslationRecord]:
        """
        下翻历史记录。
        
        Returns:
            翻阅到的历史记录，如果回到当前模式返回None
        """
        if self._history_pointer <= 0:
            # 回到当前模式
            self._history_pointer = -1
            logger.debug("下翻回到当前模式")
            return None
        
        # 在历史模式中下翻
        self._history_pointer -= 1
        logger.debug(f"下翻到历史记录: 指针={self._history_pointer}")
        return self._records[self._history_pointer]
    
    def exit_history_mode(self) -> None:
        """退出历史模式，回到当前模式。"""
        self._history_pointer = -1
        logger.debug("退出历史模式")
    
    def is_in_history_mode(self) -> bool:
        """是否处于历史模式。"""
        return self._history_pointer >= 0
    
    def get_history_pointer(self) -> int:
        """获取历史指针。"""
        return self._history_pointer

