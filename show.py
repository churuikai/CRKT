import sys
# 添加到环境
sys.path.append('D:/Pearcat/Desktop/CRKT')
import os
from PyQt5.QtWidgets import QApplication, QMainWindow, QTextEdit
from PyQt5.QtCore import Qt, QUrl
from PyQt5 import QtGui
from PyQt5.QtWebEngineWidgets import QWebEngineView
import re
from bs4 import BeautifulSoup

class MarkdownWindow(QMainWindow):
    def __init__(self, md_text=" ", font_size=50):
        super().__init__()
        # 窗口置顶
        self.setWindowFlags(self.windowFlags() | Qt.WindowStaysOnTopHint) 
    
        # 设置窗口标题和大小
        self.setWindowTitle(' ')
        self.setGeometry(0, 0, 1000, 700)
        # 创建一个 QWebEngineView 来显示HTML内容
        self.web_view = QWebEngineView(self)
        self.web_view.setZoomFactor(1.75)
        self.setCentralWidget(self.web_view)
        # 设置初始的字体大小
        self.update_html_content(md_text)
        
        # 创建 QTextEdit 作为显示区域
        # self.text_edit = QTextEdit(self)
        # self.text_edit.setReadOnly(True)  # 设置为只读
        # self.setCentralWidget(self.text_edit)
        # self.text_edit.setMarkdown(md_text)

    def update_html_content(self, md_text):
        
        # 保存到文件
        with open(os.path.abspath("index.html"), "r", encoding="utf-8") as f:
            html_template = f.read()

        soup = BeautifulSoup(html_template, 'html.parser')
        # 找到匹配的textarea标签并替换其内容
        textarea = soup.find('textarea')
        if textarea:
            textarea.string = md_text
            
        with open(os.path.abspath("index.html"), "w", encoding="utf-8") as f:
            f.write(str(soup))
        
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