import sys
import os

from PyQt5.QtWidgets import QApplication, QSystemTrayIcon, QMenu, QAction, QInputDialog, QMessageBox, QLineEdit
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import QSettings
from PyQt5.QtCore import Qt

from translator import Translator
from listener import Listener
from show import MarkdownWindow

class TranslatorApp(QApplication):
    def __init__(self, sys_argv):
        super().__init__(sys_argv)
        
        self.setQuitOnLastWindowClosed(False)

        icon_path =("icon.png")
        if not os.path.exists(icon_path):
            QMessageBox.critical(None, "Error", "Tray icon not found!")
            sys.exit()
        self.setWindowIcon(QIcon(icon_path))
        self.tray_icon = QSystemTrayIcon(QIcon(icon_path), self)
        self.tray_icon.setToolTip("CRK-Translator")

        # 右键菜单
        self.menu = QMenu()

        self.api_key_action = QAction("设置 api-Key", self)
        self.api_key_action.triggered.connect(self.set_api_key)
        self.menu.addAction(self.api_key_action)
        
        self.api_url = QAction("设置 base-url", self)
        self.api_url.triggered.connect(self.set_api_url)
        self.menu.addAction(self.api_url)
        
        self.api_headers = QAction("设置 api-headers", self)
        self.api_headers.triggered.connect(self.set_api_headers)
        self.menu.addAction(self.api_headers)
        
        self.menu.addSeparator()

        self.model_action = QAction("选择模型", self)
        self.model_action.triggered.connect(self.select_model)
        self.menu.addAction(self.model_action)

        self.menu.addSeparator()

        self.prompt_action = QAction("设置 Prompt", self)
        self.prompt_action.triggered.connect(self.edit_prompt)
        self.menu.addAction(self.prompt_action)

        self.menu.addSeparator()

        self.exit_action = QAction("退出", self)
        self.exit_action.triggered.connect(self.quit_app)
        self.menu.addAction(self.exit_action)

        self.tray_icon.setContextMenu(self.menu)
        self.tray_icon.show()  
        
        self.translator_window = None

        # QSettings
        self.settings = QSettings("config.ini", QSettings.IniFormat)
        if not self.settings.contains("prompt"):
            self.settings.setValue("prompt", '''你将作为一个专业的翻译助手，任务是将文本从英文翻译成中文。翻译时需要遵循以下要求：
1. 准确性：确保翻译内容的准确性，保留专业术语和专有名词，用反引号`标出。
2. 格式要求：使用 Markdown 语法输出内容。
3. 使用双$$：任何时候所有公式、数学字母都必须使用两个$$包围。
4. 公式格式: katex格式输出，例如：$$E = mc^2$$, 忽略任何tag和序号。
4. 使用常见字符: 任何公式中不常见的字符替换成常见标准的字符，输出latex代码，确保katex可以解析，例如:
   - '𝑆'换成'S', '𝐹'换成'F', '𝑛'换成'n', 'i'换成i
   - '...' 换成 '\cdots', '.'换成 '\cdot'
5. 注意，如果是单个单词或短语，你可以精炼地道的解释该单词/短语的含义，给出音标和简单例证。''')
        if not self.settings.contains("model"):
            self.settings.setValue("model", "gpt-3.5-turbo-0125")
        if not self.settings.contains("api_headers"):
            self.settings.setValue("api_headers", '{"x-foo": "true"}')

        # 全局热键监听线程
        self.listener = Listener()
        self.listener.signal.connect(self.translate_text)
        self.listener.start()
        
    def translate_text(self, text):
        try:
            if self.translator_window and self.translator_window.isVisible():
                self.translator_window.update_html_content('<h4 style="color: #82529d;">翻译中...</h4>')
            else:
                self.translator_window = MarkdownWindow('<h4 style="color: #82529d;">翻译中...</h4>')
                self.translator_window.display()
            self.transaltor = Translator(text, 
                                    api_key=self.settings.value("api_key"), 
                                    base_url=self.settings.value("api_url"),
                                    default_headers=eval(self.settings.value("api_headers")),
                                    model=self.settings.value("model"),
                                    prompt=self.settings.value("prompt"))
            self.transaltor.signal.connect(self.show_translation)
            self.transaltor.start()
        except Exception as e:
            print(e)
            QMessageBox.critical(None, "Error", f"An error occurred: {str(e)}")
    
    def show_translation(self, translated_text):
        try:
            if '@An error occurred:' in translated_text:
                QMessageBox.critical(None, "Error", translated_text)
                return
            print(f"Translated text: {translated_text}")
            if self.translator_window and self.translator_window.isVisible():
                self.translator_window.update_html_content(translated_text)
            else:
                self.translator_window = MarkdownWindow(translated_text)
                self.translator_window.display()
        except Exception as e:
            print(e)
            QMessageBox.critical(None, "Error", f"An error occurred: {str(e)}")

    def set_api_key(self):
        try:
            api_key = self.settings.value("api_key", "")
            api_key, ok = QInputDialog().getMultiLineText(None, " ", "API-Key", text=api_key, flags = Qt.WindowCloseButtonHint | Qt.WindowTitleHint | Qt.WindowStaysOnTopHint)
            if ok and api_key:
                self.api_key = api_key
                self.settings.setValue("api_key", api_key)  
                print(f"API Key{api_key} has been set.")
        except Exception as e:
            print(e)
            QMessageBox.critical(None, "Error", f"An error occurred: {str(e)}")
            
    def set_api_url(self):
        try:
            api_url = self.settings.value("api_url", "")
            api_url, ok = QInputDialog.getMultiLineText(None, " ", "Base-Url", text=api_url, flags = Qt.WindowCloseButtonHint | Qt.WindowTitleHint | Qt.WindowStaysOnTopHint)
            if ok and api_url:
                self.api_url = api_url
                self.settings.setValue("api_url", api_url)  
                print(f"API URL{api_url} has been set.")
        except Exception as e:
            print(e)
            QMessageBox.critical(None, "Error", f"An error occurred: {str(e)}")

    def set_api_headers(self):
        try:
            api_headers = self.settings.value("api_headers", dict())
            api_headers, ok = QInputDialog.getMultiLineText(None, " ", "API-Headers", text=api_headers, flags = Qt.WindowCloseButtonHint | Qt.WindowTitleHint | Qt.WindowStaysOnTopHint)
            if ok and api_headers:
                self.settings.setValue("api_headers", api_headers)  
                print(f"API Headers{api_headers} has been set.")
        except Exception as e:
            print(e)
            QMessageBox.critical(None, "Error", f"An error occurred: {str(e)}")
            
    def select_model(self):
        try:
            models = ["gpt-4o-mini", "gpt-3.5-turbo-0125", "gpt-3.5-turbo"]
            model = self.settings.value("model", "gpt-3.5-turbo")
            model, ok = QInputDialog.getItem(None, " ", "Model", models, models.index(model), False, flags = Qt.WindowCloseButtonHint | Qt.WindowTitleHint | Qt.WindowStaysOnTopHint)
            if ok:
                self.settings.setValue("model", model) 
                print(f"Model {model} has been selected.")
        except Exception as e:
            print(e)
            QMessageBox.critical(None, "Error", f"An error occurred: {str(e)}")

    def edit_prompt(self):
        try:
            prompt = self.settings.value("prompt", "Translate the following text to Chinese (Simplified), ensuring a professional and accurate tone. Format the translated text using Markdown, ensuring a clean and aesthetically pleasing layout.")
            prompt, ok = QInputDialog.getMultiLineText(None, " ", "Prompt", text=prompt, flags = Qt.WindowCloseButtonHint | Qt.WindowTitleHint | Qt.WindowStaysOnTopHint)
            if ok and prompt:
                self.settings.setValue("prompt", prompt) 
                print(f"Prompt {prompt} has been set.")
        except Exception as e:
            print(e)
            QMessageBox.critical(None, "Error", f"An error occurred: {str(e)}")

    def quit_app(self):
        print("Quitting the application...")
        self.quit()

if __name__ == "__main__":
    app = TranslatorApp(sys.argv)
    sys.exit(app.exec_())
