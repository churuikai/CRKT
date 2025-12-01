"""Global hotkey listener module."""

import time
from typing import Optional, Dict, Set, Tuple

from PyQt5.QtCore import QThread, pyqtSignal
from pynput import keyboard

from core.logger import get_logger
from utils.selected_text import get_selected_text  # 预加载，避免首次调用延迟

logger = get_logger("Listener")

# 常量定义
TIME_LIMIT: float = 0.2  # 双击时间限制（秒）
COOLDOWN_TIME: float = 1.0  # 冷却时间（秒）

# 支持的热键映射
HOTKEY_MAP: Dict[str, Tuple[Set, str]] = {
    "ctrl": (
        {keyboard.Key.ctrl, keyboard.Key.ctrl_l, keyboard.Key.ctrl_r},
        "Ctrl"
    ),
    "shift": (
        {keyboard.Key.shift, keyboard.Key.shift_l, keyboard.Key.shift_r},
        "Shift"
    ),
    "alt": (
        {keyboard.Key.alt, keyboard.Key.alt_l, keyboard.Key.alt_r},
        "Alt"
    ),
}


class Listener(QThread):
    """全局热键监听器，支持自定义双击热键。"""
    
    signal = pyqtSignal(str)
    translate_triggered = pyqtSignal(str)  # 翻译热键触发
    append_triggered = pyqtSignal(str)     # 附加热键触发
    
    # 兼容旧信号名
    double_ctrl = translate_triggered
    double_shift = append_triggered
    
    def __init__(
        self,
        translate_key: str = "ctrl",
        append_key: str = "shift",
        translate_enabled: bool = True,
        append_enabled: bool = True,
    ) -> None:
        """
        初始化监听器。
        
        Args:
            translate_key: 翻译热键 (ctrl/shift/alt)
            append_key: 附加热键 (ctrl/shift/alt)
            translate_enabled: 是否启用翻译热键
            append_enabled: 是否启用附加热键
        """
        super().__init__()
        
        self._translate_key = translate_key.lower()
        self._append_key = append_key.lower()
        self._translate_enabled = translate_enabled
        self._append_enabled = append_enabled
        
        # 各热键的时间戳
        self._key_times: Dict[str, float] = {"ctrl": 0, "shift": 0, "alt": 0}
        self._cooldown_end_times: Dict[str, float] = {"ctrl": 0, "shift": 0, "alt": 0}
        
        self._text_before: str = ""
        self._is_append: bool = False
        self._running: bool = True
        self._keyboard_listener: Optional[keyboard.Listener] = None
    
    def set_translate_hotkey(self, key: str, enabled: bool) -> None:
        """设置翻译热键。"""
        self._translate_key = key.lower()
        self._translate_enabled = enabled
        logger.info(f"翻译热键设置为: 双击{key.upper()}, 启用={enabled}")
    
    def set_append_hotkey(self, key: str, enabled: bool) -> None:
        """设置附加热键。"""
        self._append_key = key.lower()
        self._append_enabled = enabled
        logger.info(f"附加热键设置为: 双击{key.upper()}, 启用={enabled}")
    
    def run(self) -> None:
        """启动键盘监听。"""
        logger.info(f"热键监听器已启动 (翻译:{self._translate_key}, 附加:{self._append_key})")
        self._keyboard_listener = keyboard.Listener(on_release=self._on_release)
        self._keyboard_listener.start()
        self._keyboard_listener.join()
    
    def stop(self) -> None:
        """停止监听器。"""
        self._running = False
        if self._keyboard_listener:
            self._keyboard_listener.stop()
        logger.info("热键监听器已停止")
    
    def _get_key_type(self, key: keyboard.Key) -> Optional[str]:
        """获取按键类型。"""
        for key_type, (keys, _) in HOTKEY_MAP.items():
            if key in keys:
                return key_type
        return None
    
    def _on_release(self, key: keyboard.Key) -> None:
        """处理按键释放事件。"""
        if not self._running:
            return
        
        try:
            key_type = self._get_key_type(key)
            if key_type is None:
                return
            
            current_time = time.time()
            
            # 检查是否在冷却期（非阻塞方式）
            if current_time < self._cooldown_end_times.get(key_type, 0):
                return
            
            # 检查是否双击
            if current_time - self._key_times.get(key_type, 0) < TIME_LIMIT:
                self._key_times[key_type] -= TIME_LIMIT  # 防止连续触发
                self._handle_double_press(key_type)
            else:
                self._key_times[key_type] = current_time
                
        except Exception as e:
            logger.error(f"键盘事件处理错误: {e}")
    
    def _handle_double_press(self, key_type: str) -> None:
        """处理双击事件。"""
        # 检查是否是翻译热键
        if key_type == self._translate_key and self._translate_enabled:
            self._on_translate()
            # 使用时间戳实现非阻塞冷却
            self._cooldown_end_times[key_type] = time.time() + COOLDOWN_TIME
        
        # 检查是否是附加热键
        elif key_type == self._append_key and self._append_enabled:
            self._on_append()
    
    def _on_translate(self) -> None:
        """处理翻译热键事件。"""
        try:
            text = self._get_selected_text()
            
            if self._is_append:
                self._is_append = False
                if text == self._text_before:
                    self.translate_triggered.emit("")
                else:
                    self.translate_triggered.emit(text)
            else:
                if text == "":
                    text = self._text_before
                self.translate_triggered.emit(text)
            
            self._text_before = text if text != "" else self._text_before
            
        except Exception as e:
            logger.error(f"翻译热键处理错误: {e}")
    
    def _on_append(self) -> None:
        """处理附加热键事件。"""
        # 重置翻译热键时间避免触发
        self._key_times[self._translate_key] = 0
        text = self._get_selected_text()
        self._text_before = text
        self.append_triggered.emit(text)
        self._is_append = True
    
    def _get_selected_text(self) -> str:
        """获取选中的文本。"""
        logger.debug("正在获取选中文本...")
        text = get_selected_text()
        text = self._format_text(text)
        
        if text:
            logger.debug(f"获取到 {len(text)} 个字符")
        else:
            logger.debug("未获取到文本")
        
        return text
    
    def _format_text(self, text: str) -> str:
        """格式化文本。"""
        return text or ""
    
    @staticmethod
    def get_available_hotkeys() -> list:
        """获取可用的热键列表。"""
        return list(HOTKEY_MAP.keys())
    
    @staticmethod
    def get_hotkey_display_name(key: str) -> str:
        """获取热键的显示名称。"""
        if key.lower() in HOTKEY_MAP:
            return HOTKEY_MAP[key.lower()][1]
        return key.upper()

