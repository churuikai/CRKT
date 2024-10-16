import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QTextEdit
from PyQt5.QtCore import Qt
from PyQt5 import QtGui
from PyQt5.QtWebEngineWidgets import QWebEngineView
import markdown

class MarkdownWindow(QMainWindow):
    def __init__(self, md_text=" ", font_size=25):
        super().__init__()
        # 窗口置顶
        self.setWindowFlags(self.windowFlags() | Qt.WindowStaysOnTopHint) 
    
        # 设置窗口标题和大小
        self.setWindowTitle(' ')
        self.setGeometry(500, 500, 600, 400)
        # 创建一个 QWebEngineView 来显示HTML内容
        self.web_view = QWebEngineView(self)
        self.setCentralWidget(self.web_view)
        # 设置初始的字体大小
        self.font_size = font_size
        # 渲染初始的Markdown文本
        self.update_html_content(md_text)
        
        # 创建 QTextEdit 作为显示区域
        # self.text_edit = QTextEdit(self)
        # self.text_edit.setReadOnly(True)  # 设置为只读
        # self.setCentralWidget(self.text_edit)

        # self.text_edit.setMarkdown(md_text)


    def update_html_content(self, md_text):
        html_text = markdown.markdown(md_text, extensions=['fenced_code', 'tables'])
        html_template = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <script src="https://polyfill.io/v3/polyfill.min.js?features=es6"></script>
            <script id="MathJax-script" async
                src="https://cdn.jsdelivr.net/npm/mathjax@3/es5/tex-mml-chtml.js"></script>
            <style>
                body {{
                    font-family: Arial, sans-serif;
                    font-size: {self.font_size}px;  /* 设置整体字体大小 */
                    line-height: 1.6;
                    padding: 20px;
                }}
                h1, h2, h3, h4, h5, h6 {{
                    font-weight: bold;
                }}
                code {{
                    font-family: Consolas, "Courier New", monospace;
                    background-color: #f5f5f5;
                    padding: 2px 4px;
                    border-radius: 4px;
                }}
                pre {{
                    background-color: #f5f5f5;
                    padding: 10px;
                    border-radius: 4px;
                }}
                /* MathJax-specific styles */
                .MathJax {{
                    font-size: {self.font_size}px;  /* 设置公式字体大小 */
                }}
            </style>
        </head>
        <body>
            {html_text}
        </body>
        </html>
        """
        
        self.web_view.setHtml(html_template)
        # self.text_edit.setMarkdown(md_text)
        
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