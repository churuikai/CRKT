"""Module for getting selected text from the system."""

import time
import threading
from typing import Optional

import pyperclip
from win32api import keybd_event

from core.logger import get_logger

logger = get_logger("SelectedText")


def get_selected_text_by_clipboard() -> Optional[str]:
    """
    通过剪贴板获取选中的文本。
    
    Returns:
        选中的文本，如果没有选中文本则返回None
    """
    try:
        old_clipboard = pyperclip.paste()
        
        # 清空剪贴板
        pyperclip.copy("")
        
        # 发送 Ctrl+C 复制选中的文本
        keybd_event(0x11, 0, 0, 0)  # Ctrl 按下
        keybd_event(0x43, 0, 0, 0)  # C 按下
        keybd_event(0x43, 0, 2, 0)  # C 释放
        keybd_event(0x11, 0, 2, 0)  # Ctrl 释放
        
        # 等待剪贴板更新
        text = ""
        for _ in range(10):
            time.sleep(0.02)
            text = pyperclip.paste()
            if text:
                break
        
        # 恢复原始剪贴板
        def restore(old_content: str) -> None:
            time.sleep(0.2)
            pyperclip.copy(old_content)
        
        threading.Thread(target=restore, args=(old_clipboard,), daemon=True).start()
        
        return text
        
    except Exception as e:
        logger.error(f"剪贴板获取文本时出错: {e}")
        return None


def get_selected_text() -> str:
    """
    获取选中文本。
    
    Returns:
        选中的文本，如果所有方法都失败则返回空字符串
    """
    text = get_selected_text_by_clipboard()
    
    if text:
        logger.debug(f"成功获取到 {len(text)} 个字符")
    else:
        logger.debug("未能获取到任何文本")
    
    return text or ""


if __name__ == "__main__":
    print("请选择一些文本并按回车键...")
    input()
    text = get_selected_text()
    print(f"选中的文本: {text}")

