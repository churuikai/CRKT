import sys
# 添加到环境
# sys.path.append('D:/Pearcat/Desktop/CRKT')
import os
from PyQt5.QtWidgets import QApplication, QMainWindow
from PyQt5.QtCore import Qt, QUrl
from PyQt5 import QtGui
from PyQt5.QtWebEngineWidgets import QWebEngineView
from bs4 import BeautifulSoup
import time

class MarkdownWindow(QMainWindow):
    def __init__(self ):
        super().__init__()
        # 窗口置顶
        self.setWindowFlags(self.windowFlags() | Qt.WindowStaysOnTopHint) 
        self.setWindowTitle(' ')
        self.setGeometry(0, 0, 1000, 700)
        # 创建一个 QWebEngineView 来显示HTML内容
        self.web_view = QWebEngineView(self)
        self.web_view.setZoomFactor(1.75)
        self.setCentralWidget(self.web_view)
        self.web_view.load(QUrl.fromLocalFile(os.path.abspath("index.html")))

    def update_html_content(self, md_text):
        # 如果窗口关闭
        if not self.isVisible():
            self.display()
            time.sleep(0.1)
        # 如果窗口最下化
        if self.isMinimized():
            self.showNormal()
    
        # 执行JavaScript代码
        javascript = f'updateMarkdown(`{md_text.replace("`", "\\`")}`);'
        try:
            self.web_view.page().runJavaScript(javascript)
        except Exception as e:
            self.web_view.load(QUrl.fromLocalFile(os.path.abspath("index.html")))
            
    def display(self):
        cursor_pos = QtGui.QCursor.pos()
        window_size = self.size()
        x = cursor_pos.x() - window_size.width() // 2
        y = cursor_pos.y()
        # 移动窗口
        self.move(x, y)
        self.show()

def show_markdown_window(md_text):
    app = QApplication(sys.argv)
    window = MarkdownWindow(md_text)
    window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":    
    show_markdown_window("# Hello, Markdown!")