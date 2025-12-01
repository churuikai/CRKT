"""Display window view module."""

import sys
import os
from typing import Optional, Callable

from PyQt5.QtWidgets import QMainWindow, QApplication, QDesktopWidget, QPushButton, QWidget, QHBoxLayout, QLabel, QVBoxLayout
from PyQt5.QtCore import Qt, QUrl, pyqtSignal, QTimer
from PyQt5.QtGui import QCursor, QIcon
from PyQt5.QtWebEngineWidgets import QWebEngineView, QWebEnginePage

from core.logger import get_logger

logger = get_logger("DisplayWindowView")


class CustomWebEnginePage(QWebEnginePage):
    """自定义 WebEnginePage，用于接收前端 JS 的消息。"""
    
    navigate_up_requested = pyqtSignal()
    navigate_down_requested = pyqtSignal()
    
    def javaScriptConsoleMessage(self, level, message, line, source):
        """接收前端 console.log 消息。"""
        if message == 'CRKT_ACTION:navigate-up':
            self.navigate_up_requested.emit()
        elif message == 'CRKT_ACTION:navigate-down':
            self.navigate_down_requested.emit()


class DisplayWindowView(QMainWindow):
    """显示窗口视图，用于展示翻译结果。"""
    
    # 信号定义
    text_ready = pyqtSignal(str)  # 文本准备好进行翻译
    window_state_changed = pyqtSignal(object)  # 窗口状态改变
    window_closed = pyqtSignal()  # 窗口关闭
    page_ready = pyqtSignal()  # 页面加载完成
    history_navigate_up = pyqtSignal()  # 历史记录上翻
    history_navigate_down = pyqtSignal()  # 历史记录下翻
    
    # 默认窗口尺寸
    DEFAULT_WIDTH = 1000
    DEFAULT_HEIGHT = 700
    COMPARISON_WIDTH_FACTOR = 1.5  # 对照模式宽度倍数
    
    def __init__(self, app_dir: str):
        """
        初始化显示窗口。
        
        Args:
            app_dir: 应用程序目录
        """
        super().__init__()
        
        self._app_dir = app_dir
        self._index_html_path = os.path.join(app_dir, "index.html")
        self._current_content = ""
        self._current_source_text = ""
        self._user_closed = False
        self._comparison_mode = False
        
        self._setup_window()
        self._setup_web_view()
        self._load_html()
        
        logger.info(f"显示窗口初始化完成，HTML路径: {self._index_html_path}")
    
    def _setup_window(self) -> None:
        """设置窗口属性。"""
        self.setWindowFlags(self.windowFlags() | Qt.WindowStaysOnTopHint)
        self.setWindowTitle('CRKT Translator')
        self.setGeometry(0, 0, self.DEFAULT_WIDTH, self.DEFAULT_HEIGHT)
        
        self.setStyleSheet("""
            QMainWindow {
                background-color: #f5f5f5;
            }
        """)
    
    def _setup_history_toolbar(self) -> QWidget:
        """设置历史翻阅工具栏。"""
        toolbar = QWidget()
        toolbar.setFixedHeight(24)
        toolbar.setStyleSheet("""
            QWidget {
                background-color: #ffffff;
            }
            QPushButton {
                background-color: #f0f0f0;
                border: 1px solid #d5d5d5;
                border-radius: 3px;
                font-size: 13px;
                color: #444444;
            }
            QPushButton:hover {
                background-color: #e5e5e5;
                border-color: #c0c0c0;
            }
            QPushButton:pressed {
                background-color: #d8d8d8;
            }
            QLabel {
                color: #888888;
                font-size: 14px;
            }
        """)
        
        layout = QHBoxLayout(toolbar)
        layout.setContentsMargins(6, 2, 6, 0)
        layout.setSpacing(4)
        
        # 历史记录上翻按钮
        self._btn_history_up = QPushButton("↑", toolbar)
        self._btn_history_up.setFixedSize(22, 20)
        self._btn_history_up.setToolTip("上翻历史记录")
        self._btn_history_up.setFocusPolicy(Qt.NoFocus)
        self._btn_history_up.clicked.connect(self._on_history_up_clicked)
        
        # 历史记录下翻按钮
        self._btn_history_down = QPushButton("↓", toolbar)
        self._btn_history_down.setFixedSize(22, 20)
        self._btn_history_down.setToolTip("下翻历史记录")
        self._btn_history_down.setFocusPolicy(Qt.NoFocus)
        self._btn_history_down.clicked.connect(self._on_history_down_clicked)
        
        # 历史位置提示标签
        self._label_history_info = QLabel("", toolbar)
        self._label_history_info.setVisible(False)
        
        layout.addWidget(self._btn_history_up)
        layout.addWidget(self._btn_history_down)
        layout.addWidget(self._label_history_info)
        layout.addStretch()
        
        return toolbar
    
    def _setup_web_view(self) -> None:
        """设置WebEngineView。"""
        # 创建历史工具栏
        toolbar = self._setup_history_toolbar()
        
        # 创建web view 和自定义 page
        self._web_view = QWebEngineView()
        self._custom_page = CustomWebEnginePage(self._web_view)
        self._web_view.setPage(self._custom_page)
        self._web_view.setZoomFactor(1.75)
        self._web_view.setContextMenuPolicy(Qt.NoContextMenu)
        
        # 连接自定义页面的信号
        self._custom_page.navigate_up_requested.connect(self._on_history_up_clicked)
        self._custom_page.navigate_down_requested.connect(self._on_history_down_clicked)
        
        # 组合布局
        vbox = QVBoxLayout()
        vbox.setContentsMargins(0, 0, 0, 0)
        vbox.setSpacing(0)
        vbox.addWidget(toolbar)
        vbox.addWidget(self._web_view)
        
        wrapper = QWidget()
        wrapper.setLayout(vbox)
        self.setCentralWidget(wrapper)
    
    def _load_html(self) -> None:
        """加载HTML文件。"""
        # 连接页面加载完成信号
        self._web_view.loadFinished.connect(self._on_page_load_finished)
        
        try:
            with open(self._index_html_path, 'r', encoding='utf-8') as f:
                html_content = f.read()
            
            base_url = QUrl.fromLocalFile(self._app_dir + os.path.sep)
            self._web_view.setHtml(html_content, baseUrl=base_url)
        except Exception as e:
            logger.error(f"加载HTML文件出错: {e}")
            self._web_view.load(QUrl.fromLocalFile(self._index_html_path))
    
    def _on_page_load_finished(self, success: bool) -> None:
        """页面加载完成回调。"""
        if success:
            # 延迟触发 page_ready 信号，确保 JS 完全加载
            QTimer.singleShot(800, self.page_ready.emit)
            logger.debug("页面加载完成，将在 800ms 后触发初始化")
        else:
            logger.error("页面加载失败")
    
    def _execute_js(self, javascript: str, reload_on_error: bool = False) -> None:
        """执行JavaScript代码。"""
        try:
            self._web_view.page().runJavaScript(javascript)
        except Exception as e:
            logger.error(f"执行JavaScript出错: {e}")
            if reload_on_error:
                self._load_html()
    
    def _execute_js_with_callback(
        self,
        javascript: str,
        callback: Callable,
    ) -> None:
        """执行带回调的JavaScript代码。"""
        try:
            self._web_view.page().runJavaScript(javascript, callback)
        except Exception as e:
            logger.error(f"执行JavaScript出错: {e}")
    
    # Qt事件重写
    def changeEvent(self, event) -> None:
        """处理窗口状态改变事件。"""
        if event.type() == event.WindowStateChange:
            self.window_state_changed.emit(self.windowState())
        super().changeEvent(event)
    
    def resizeEvent(self, event) -> None:
        """处理窗口大小变化事件。"""
        super().resizeEvent(event)
        # 通知前端更新布局方向
        if self._comparison_mode:
            self._execute_js('updateLayoutDirection();')
    
    def closeEvent(self, event) -> None:
        """处理窗口关闭事件。"""
        self._user_closed = True
        self.window_closed.emit()
        event.accept()
    
    # 对照模式相关方法
    def set_comparison_mode(self, enabled: bool) -> None:
        """
        设置对照模式（会初始化对应的编辑器）。
        
        Args:
            enabled: 是否启用对照模式
        """
        self._apply_comparison_mode(enabled)
    
    def _apply_comparison_mode(self, enabled: bool) -> None:
        """应用对照模式设置。"""
        self._comparison_mode = enabled
        
        # 调整窗口大小
        if enabled:
            new_width = int(self.DEFAULT_WIDTH * self.COMPARISON_WIDTH_FACTOR)
            self.resize(new_width, self.DEFAULT_HEIGHT)
        else:
            self.resize(self.DEFAULT_WIDTH, self.DEFAULT_HEIGHT)
        
        # 通知前端切换模式并初始化编辑器
        js = f'setComparisonMode({str(enabled).lower()});'
        self._execute_js(js)
        
        logger.info(f"对照模式: {'开启' if enabled else '关闭'}")
    
    def lock_source_pane(self) -> None:
        """锁定原文区。"""
        self._execute_js('lockSourcePane();')
    
    def unlock_source_pane(self) -> None:
        """解锁原文区。"""
        self._execute_js('unlockSourcePane();')
    
    # 数据更新接口（Python → JavaScript）
    def update_source(self, text: str, show_window: bool = True) -> None:
        """
        更新原文数据。
        
        Args:
            text: 原文内容
            show_window: 是否显示窗口
        """
        self._current_source_text = text
        text_escaped = text.replace("`", "\\`").replace("\\", "\\\\")
        js = f'updateSource(`{text_escaped}`);'
        
        if show_window:
            self._display()
        self._execute_js(js, reload_on_error=True)
    
    def append_source(self, text: str, show_window: bool = True) -> None:
        """
        追加原文数据。
        
        Args:
            text: 要追加的文本
            show_window: 是否显示窗口
        """
        text_escaped = text.replace("`", "\\`").replace("\\", "\\\\")
        js = f'appendSource(`{text_escaped}`);'
        
        if show_window:
            self._display()
        self._execute_js(js, reload_on_error=True)
    
    def update_translation(self, markdown: str, show_window: bool = True) -> None:
        """
        更新翻译数据。
        
        Args:
            markdown: 翻译内容（Markdown格式）
            show_window: 是否显示窗口
        """
        self._current_content = markdown
        markdown_escaped = markdown.replace("`", "\\`")
        js = f'updateTranslation(`{markdown_escaped}`);'
        
        if show_window:
            self._display()
            self._execute_js(js, reload_on_error=True)
        else:
            self._execute_js(js)
    
    def get_source(self, callback: Callable[[str], None]) -> None:
        """
        获取当前原文。
        
        Args:
            callback: 回调函数，参数为原文内容
        """
        self._execute_js_with_callback('getSource();', callback)
    
    def is_locked(self, callback: Callable[[bool], None]) -> None:
        """
        检查是否锁定。
        
        Args:
            callback: 回调函数，参数为是否锁定
        """
        self._execute_js_with_callback('isLocked();', callback)
    
    def enter_history_mode(self, source_text: str, translation_text: str, history_index: int = 0) -> None:
        """
        进入历史模式，显示历史记录。
        
        Args:
            source_text: 历史原文
            translation_text: 历史翻译结果
            history_index: 历史记录索引（0为最新）
        """
        source_escaped = source_text.replace("`", "\\`").replace("\\", "\\\\")
        translation_escaped = translation_text.replace("`", "\\`")
        js = f'enterHistoryMode(`{source_escaped}`, `{translation_escaped}`);'
        self._execute_js(js)
        
        # 更新历史位置提示
        self._label_history_info.setText(f"上{history_index + 1}条")
        self._label_history_info.setVisible(True)
        
        logger.debug(f"进入历史模式: 第{history_index}条")
    
    def exit_history_mode(self) -> None:
        """退出历史模式，回到当前模式。"""
        self._execute_js('exitHistoryMode();')
        
        # 隐藏历史位置提示
        self._label_history_info.setVisible(False)
        
        logger.debug("退出历史模式")
    
    def _on_history_up_clicked(self) -> None:
        """历史记录上翻按钮点击。"""
        self.history_navigate_up.emit()
    
    def _on_history_down_clicked(self) -> None:
        """历史记录下翻按钮点击。"""
        self.history_navigate_down.emit()
    
    def _on_text_ready(self, text: str) -> None:
        """文本准备好时的回调。"""
        self.text_ready.emit(text)
    
    def _display(self) -> None:
        """显示窗口，智能调整位置避免超出屏幕边界。"""
        self._user_closed = False
        
        if not self.isVisible():
            cursor_pos = QCursor.pos()
            window_size = self.size()
            
            # 获取鼠标所在屏幕的可用区域
            screen = QApplication.screenAt(cursor_pos)
            if screen:
                screen_geometry = screen.availableGeometry()
            else:
                screen_geometry = QDesktopWidget().availableGeometry()
            
            # 计算初始位置（窗口中心对齐鼠标）
            x = cursor_pos.x() - window_size.width() // 2
            y = cursor_pos.y()
            
            # 智能调整：确保窗口不超出屏幕边界
            # 右边界检查
            if x + window_size.width() > screen_geometry.right():
                x = screen_geometry.right() - window_size.width()
            # 左边界检查
            if x < screen_geometry.left():
                x = screen_geometry.left()
            # 下边界检查
            if y + window_size.height() > screen_geometry.bottom():
                y = cursor_pos.y() - window_size.height() - 10  # 显示在鼠标上方
            # 上边界检查
            if y < screen_geometry.top():
                y = screen_geometry.top()
            
            self.move(x, y)
            self.show()
        elif self.isMinimized():
            self.showNormal()
    
    def show_and_activate(self) -> None:
        """显示并激活窗口。"""
        self._user_closed = False
        self.showNormal()
        self.activateWindow()
    
    @property
    def user_closed(self) -> bool:
        """窗口是否被用户关闭。"""
        return self._user_closed
    
    @user_closed.setter
    def user_closed(self, value: bool) -> None:
        self._user_closed = value
    
    @property
    def current_content(self) -> str:
        """当前显示内容。"""
        return self._current_content
    
    @property
    def current_source_text(self) -> str:
        """当前原文内容。"""
        return self._current_source_text
    
    @property
    def comparison_mode(self) -> bool:
        """是否处于对照模式。"""
        return self._comparison_mode
