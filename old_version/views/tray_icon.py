"""System tray icon view module."""

import webbrowser
from typing import Optional, Callable

from PyQt5.QtWidgets import QSystemTrayIcon, QMenu, QAction, QApplication
from PyQt5.QtGui import QIcon

from core.logger import get_logger

logger = get_logger("TrayIconView")


class TrayIconView:
    """系统托盘图标视图。"""
    
    def __init__(
        self,
        icon: QIcon,
        tooltip: str = "CRK-Translator",
    ):
        """
        初始化托盘图标。
        
        Args:
            icon: 托盘图标
            tooltip: 提示文本
        """
        self._tray_icon = QSystemTrayIcon(icon)
        self._tray_icon.setToolTip(tooltip)
        
        self._menu = QMenu()
        self._actions: dict = {}
        
        # 回调函数
        self._on_settings_click: Optional[Callable[[], None]] = None
        self._on_startup_toggle: Optional[Callable[[bool], None]] = None
        self._on_source_comparison_toggle: Optional[Callable[[bool], None]] = None
        self._on_quit_click: Optional[Callable[[], None]] = None
        self._on_tray_activated: Optional[Callable[[QSystemTrayIcon.ActivationReason], None]] = None
        
        self._setup_menu()
        self._setup_signals()
    
    def _setup_menu(self) -> None:
        """设置托盘菜单。"""
        # 设置菜单项
        self._actions["settings"] = QAction("设置")
        self._actions["settings"].triggered.connect(self._handle_settings_click)
        
        self._actions["source_comparison"] = QAction("原文对照")
        self._actions["source_comparison"].setCheckable(True)
        self._actions["source_comparison"].triggered.connect(self._handle_source_comparison_toggle)
        
        self._actions["startup"] = QAction("开机自启动")
        self._actions["startup"].setCheckable(True)
        self._actions["startup"].triggered.connect(self._handle_startup_toggle)
        
        self._actions["about"] = QAction("关于")
        self._actions["about"].triggered.connect(
            lambda: webbrowser.open("https://github.com/churuikai/CRKT")
        )
        
        self._actions["quit"] = QAction("退出")
        self._actions["quit"].triggered.connect(self._handle_quit_click)
        
        # 添加菜单项
        self._menu.addAction(self._actions["settings"])
        self._menu.addSeparator()
        self._menu.addAction(self._actions["source_comparison"])
        self._menu.addAction(self._actions["startup"])
        self._menu.addSeparator()
        self._menu.addAction(self._actions["about"])
        self._menu.addSeparator()
        self._menu.addAction(self._actions["quit"])
        
        self._tray_icon.setContextMenu(self._menu)
    
    def _setup_signals(self) -> None:
        """设置信号连接。"""
        self._tray_icon.activated.connect(self._handle_tray_activated)
    
    # 事件处理
    def _handle_settings_click(self) -> None:
        if self._on_settings_click:
            self._on_settings_click()
    
    def _handle_startup_toggle(self, checked: bool) -> None:
        if self._on_startup_toggle:
            self._on_startup_toggle(checked)
    
    def _handle_source_comparison_toggle(self, checked: bool) -> None:
        if self._on_source_comparison_toggle:
            self._on_source_comparison_toggle(checked)
    
    def _handle_quit_click(self) -> None:
        if self._on_quit_click:
            self._on_quit_click()
    
    def _handle_tray_activated(self, reason: QSystemTrayIcon.ActivationReason) -> None:
        if self._on_tray_activated:
            self._on_tray_activated(reason)
    
    # 公共方法
    def show(self) -> None:
        """显示托盘图标。"""
        self._tray_icon.show()
    
    def hide(self) -> None:
        """隐藏托盘图标。"""
        self._tray_icon.hide()
    
    def set_startup_checked(self, checked: bool) -> None:
        """设置开机自启动选项的选中状态。"""
        self._actions["startup"].setChecked(checked)
    
    def set_source_comparison_checked(self, checked: bool) -> None:
        """设置原文对照选项的选中状态。"""
        self._actions["source_comparison"].setChecked(checked)
    
    # 回调设置
    def set_on_settings_click(self, callback: Callable[[], None]) -> None:
        self._on_settings_click = callback
    
    def set_on_startup_toggle(self, callback: Callable[[bool], None]) -> None:
        self._on_startup_toggle = callback
    
    def set_on_source_comparison_toggle(self, callback: Callable[[bool], None]) -> None:
        self._on_source_comparison_toggle = callback
    
    def set_on_quit_click(self, callback: Callable[[], None]) -> None:
        self._on_quit_click = callback
    
    def set_on_tray_activated(
        self,
        callback: Callable[[QSystemTrayIcon.ActivationReason], None],
    ) -> None:
        self._on_tray_activated = callback
    
    @property
    def tray_icon(self) -> QSystemTrayIcon:
        """获取底层的QSystemTrayIcon对象。"""
        return self._tray_icon
