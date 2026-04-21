"""Cache management module."""

import time
import pickle
import os
from typing import Optional, Dict, Tuple, Any

from core.logger import get_logger

logger = get_logger("CacheManager")


class CacheManager:
    """缓存管理器，负责翻译结果的缓存和持久化。"""
    
    def __init__(
        self,
        path: str,
        max_size: int = 1000,
        save_frequency: int = 20,
    ):
        """
        初始化缓存管理器。
        
        Args:
            path: 缓存文件路径
            max_size: 最大缓存条目数
            save_frequency: 自动保存频率（每N次写入保存一次）
        """
        self._path = path
        self._max_size = max_size
        self._save_frequency = save_frequency
        self._cache: Dict[str, Tuple[float, str]] = {}
        self._write_count = 0
        
        self._load()
        logger.info("缓存管理器初始化完成")
    
    def _load(self) -> None:
        """从文件加载缓存。"""
        try:
            if os.path.exists(self._path):
                with open(self._path, "rb") as f:
                    self._cache = pickle.load(f)
                logger.info(f"加载了 {len(self._cache)} 条缓存记录")
            else:
                self._cache = {}
                logger.info("缓存文件不存在，创建空缓存")
        except Exception as e:
            logger.error(f"加载缓存失败: {e}")
            self._cache = {}
    
    def save(self) -> None:
        """保存缓存到文件。"""
        try:
            start_time = time.time()
            
            # 确保目录存在
            os.makedirs(os.path.dirname(self._path), exist_ok=True)
            
            with open(self._path, "wb") as f:
                pickle.dump(self._cache, f)
            
            elapsed = time.time() - start_time
            logger.info(f"缓存保存完成，耗时 {elapsed:.2f} 秒")
        except Exception as e:
            logger.error(f"保存缓存失败: {e}")
    
    def get(self, key: str, min_gap: float = 3.0) -> Optional[str]:
        """
        获取缓存值。
        
        Args:
            key: 缓存键
            min_gap: 两次请求的最小时间间隔（秒），间隔内返回None避免重复请求
            
        Returns:
            缓存的值，如果不存在或在冷却期内返回None
        """
        if key not in self._cache:
            return None
        
        timestamp, value = self._cache[key]
        current_time = time.time()
        
        # 检查时间间隔
        if current_time - timestamp < min_gap:
            # 更新时间戳但不返回值（防止短时间内重复翻译）
            self._cache[key] = (current_time, value)
            return None
        
        # 更新时间戳并返回值
        self._cache[key] = (current_time, value)
        return value
    
    def set(self, key: str, value: str) -> None:
        """
        设置缓存值。
        
        Args:
            key: 缓存键
            value: 缓存值
        """
        # 检查容量，如果超过最大值则清理旧条目
        if len(self._cache) > self._max_size:
            self._cleanup()
        
        self._cache[key] = (time.time(), value)
        self._write_count += 1
        
        # 自动保存
        if self._write_count >= self._save_frequency:
            self.save()
            self._write_count = 0
    
    def _cleanup(self) -> None:
        """清理旧的缓存条目，保留80%容量。"""
        target_size = int(self._max_size * 0.8)
        
        if len(self._cache) <= target_size:
            return
        
        # 按时间戳排序，删除最旧的条目
        sorted_keys = sorted(
            self._cache.keys(),
            key=lambda k: self._cache[k][0]
        )
        
        keys_to_remove = sorted_keys[:len(self._cache) - target_size]
        for key in keys_to_remove:
            del self._cache[key]
        
        logger.info(f"清理了 {len(keys_to_remove)} 条旧缓存")
    
    def clear(self) -> None:
        """清空所有缓存。"""
        self._cache.clear()
        self._write_count = 0
        self.save()
        logger.info("缓存已清空")
    
    @property
    def size(self) -> int:
        """返回当前缓存条目数。"""
        return len(self._cache)
