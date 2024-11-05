import sys
import os
from PyQt5.QtWidgets import QApplication, QMainWindow
from PyQt5.QtCore import Qt, QUrl, pyqtSignal
from PyQt5 import QtGui
from PyQt5.QtWebEngineWidgets import QWebEngineView

class DisplayWindow(QMainWindow):
    append_text = pyqtSignal(str)
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
        print("DisplayWindow")

    def update_html_content(self, md_text):
        self.__display()
        javascript = f'updateMarkdown(`{md_text.replace("`", "\\`")}`);'
        try:
            self.web_view.page().runJavaScript(javascript)
        except Exception as e:
            self.web_view.load(QUrl.fromLocalFile(os.path.abspath("index.html")))

    def append_text_content(self, text):
        self.__display()
        javascript = f'appendText(`{text.replace("`", "\\`")}`);'
        try:
            self.web_view.page().runJavaScript(javascript)
        except Exception as e:
            self.web_view.load(QUrl.fromLocalFile(os.path.abspath("index.html")))
    
    def get_text(self, text):
        javascript = f'getText(`{text.replace("`", "\\`")}`);'
        try:
            self.web_view.page().runJavaScript(javascript, self.__send_text_signal)
        except Exception as e:
            print(e)
    
    def __send_text_signal(self, text):
        self.append_text.emit(text)
            
    def __display(self):
        if not self.isVisible():
            cursor_pos = QtGui.QCursor.pos()
            window_size = self.size()
            x = cursor_pos.x() - window_size.width() // 2
            y = cursor_pos.y()
            # 移动窗口
            self.move(x, y)
            self.show()
        elif self.isMinimized():
            self.showNormal()

def show_markdown_window(md_text):
    app = QApplication(sys.argv)
    window = DisplayWindow(md_text)
    window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":    
    show_markdown_window("# Hello, Markdown!")