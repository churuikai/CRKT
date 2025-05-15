import sys
import os
from PyQt5.QtWidgets import QApplication, QMainWindow
from PyQt5.QtCore import Qt, QUrl, pyqtSignal
from PyQt5 import QtGui
from PyQt5.QtWebEngineWidgets import QWebEngineView

class DisplayWindow(QMainWindow):
    append_text = pyqtSignal(str)
    windowStateChanged = pyqtSignal(Qt.WindowStates)
    
    def __init__(self):
        super().__init__()
        # 窗口置顶
        self.setWindowFlags(self.windowFlags() | Qt.WindowStaysOnTopHint) 
        self.setWindowTitle(' ')
        self.setGeometry(0, 0, 1000, 700)
        
        # 设置窗口样式
        self.setStyleSheet("""
            QMainWindow {
                background-color: #f5f5f5;
                border: 1px solid #ddd;
                border-radius: 10px;
            }
        """)
        
        # 创建一个 QWebEngineView 来显示HTML内容
        self.web_view = QWebEngineView(self)
        self.web_view.setZoomFactor(1.75)
        self.setCentralWidget(self.web_view)
        self.web_view.load(QUrl.fromLocalFile(os.path.abspath("index.html")))
        print("DisplayWindow initialized")
        
        # 当前内容 - 用于在后台更新内容而不显示窗口时保存
        self.current_content = ""
    
    # 重写windowStateChange事件，发送信号
    def changeEvent(self, event):
        if event.type() == event.WindowStateChange:
            self.windowStateChanged.emit(self.windowState())
        super().changeEvent(event)
        
    def update_html_content(self, md_text):
        """更新HTML内容并显示窗口"""
        self.current_content = md_text
        self.__display()
        javascript = f'updateMarkdown(`{md_text.replace("`", "\\`")}`);'
        try:
            self.web_view.page().runJavaScript(javascript)
        except Exception as e:
            print(f"Error updating HTML content: {e}")
            self.web_view.load(QUrl.fromLocalFile(os.path.abspath("index.html")))
    
    def update_html_without_show(self, md_text):
        """更新HTML内容但不显示窗口（用于最小化状态）"""
        self.current_content = md_text
        javascript = f'updateMarkdown(`{md_text.replace("`", "\\`")}`);'
        try:
            self.web_view.page().runJavaScript(javascript)
        except Exception as e:
            print(f"Error updating HTML content without showing: {e}")
            
    def append_text_content(self, text):
        """添加文本内容并显示窗口"""
        self.__display()
        javascript = f'appendText(`{text.replace("`", "\\`")}`);'
        try:
            self.web_view.page().runJavaScript(javascript)
        except Exception as e:
            print(f"Error appending text: {e}")
            self.web_view.load(QUrl.fromLocalFile(os.path.abspath("index.html")))
    
    def append_text_without_show(self, text):
        """添加文本内容但不显示窗口（用于最小化状态）"""
        javascript = f'appendText(`{text.replace("`", "\\`")}`);'
        try:
            self.web_view.page().runJavaScript(javascript)
        except Exception as e:
            print(f"Error appending text without showing: {e}")
    
    def get_text(self, text):
        """获取文本并触发翻译信号"""
        javascript = f'getText(`{text.replace("`", "\\`")}`);'
        try:
            self.web_view.page().runJavaScript(javascript, self.__send_text_signal)
        except Exception as e:
            print(f"Error getting text: {e}")
    
    def __send_text_signal(self, text):
        """发送文本信号到翻译模块"""
        self.append_text.emit(text)
            
    def __display(self):
        """显示窗口"""
        if not self.isVisible():
            cursor_pos = QtGui.QCursor.pos()
            window_size = self.size()
            x = cursor_pos.x() - window_size.width() // 2
            y = cursor_pos.y()
            # 移动窗口
            self.move(x, y)
            self.show()
        elif self.isMinimized():
            # 只有当窗口被最小化时才恢复正常状态
            self.showNormal()

def show_markdown_window(md_text):
    app = QApplication(sys.argv)
    window = DisplayWindow()
    window.update_html_content(md_text)
    window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":    
    show_markdown_window("# Hello, Markdown!")