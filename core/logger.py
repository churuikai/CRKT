"""Logging configuration for the application."""

import logging
import sys
import os
from typing import Optional


_logger: Optional[logging.Logger] = None


def setup_logging(
    name: str = "CRKT",
    level: int = logging.INFO,
    log_file: Optional[str] = None,
) -> logging.Logger:
    """
    配置并返回应用程序的日志记录器。
    
    Args:
        name: 日志记录器名称
        level: 日志级别
        log_file: 可选的日志文件路径
    
    Returns:
        配置好的Logger实例
    """
    global _logger
    
    if _logger is not None:
        return _logger
    
    logger = logging.getLogger(name)
    logger.setLevel(level)
    
    # 避免重复添加handler
    if logger.handlers:
        return logger
    
    # 创建格式化器
    formatter = logging.Formatter(
        fmt="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )
    
    # 控制台处理器
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(level)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    # 文件处理器（可选）
    if log_file:
        try:
            os.makedirs(os.path.dirname(log_file), exist_ok=True)
            file_handler = logging.FileHandler(log_file, encoding="utf-8")
            file_handler.setLevel(level)
            file_handler.setFormatter(formatter)
            logger.addHandler(file_handler)
        except Exception as e:
            logger.warning(f"无法创建日志文件: {e}")
    
    _logger = logger
    return logger


def get_logger(name: Optional[str] = None) -> logging.Logger:
    """
    获取日志记录器实例。
    
    Args:
        name: 可选的子日志记录器名称
    
    Returns:
        Logger实例
    """
    global _logger
    
    if _logger is None:
        _logger = setup_logging()
    
    if name:
        return _logger.getChild(name)
    
    return _logger
