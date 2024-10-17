import sys
import os
# 获取当前文件路径
current_path = os.path.dirname(os.path.abspath(__file__))
# 将当前路径添加到系统路径中
sys.path.append(current_path)

from PyQt5.QtWidgets import QApplication, QSystemTrayIcon, QMenu, QAction, QInputDialog, QMessageBox
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import QSettings
from PyQt5.QtCore import Qt

from translator import Translator
from listener import Listener
from show import MarkdownWindow

class TranslatorApp(QApplication):
    def __init__(self, sys_argv):
        super().__init__(sys_argv)
        
        # 禁止所有窗口关闭后自动退出
        self.setQuitOnLastWindowClosed(False)
        
        # 设置托盘图标
        icon_path =("icon.png")
        if not os.path.exists(icon_path):
            QMessageBox.critical(None, "Error", "Tray icon not found!")
            sys.exit()
        self.setWindowIcon(QIcon(icon_path))
        self.tray_icon = QSystemTrayIcon(QIcon(icon_path), self)
        self.tray_icon.setToolTip("CRK-Translator")

        # 创建右键菜单
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
        self.tray_icon.show()  # 显示托盘图标
        
        self.translator_window = None

        # 使用 QSettings 存储和读取 API Key 和模型
        self.settings = QSettings("config.ini", QSettings.IniFormat)
        if not self.settings.contains("prompt"):
            self.settings.setValue("prompt", '''你是一名专业的翻译，请把给出的文本翻译成中文。一定注意输出格式为严格HTML格式，是<body>内的内容（不包括<body>标签），能够被正确解析。注意换行，注意灵活调整公式格式，仔细检查务必确保块公式和内联公式都能够被MathJax解析。''')
        if not self.settings.contains("model"):
            self.settings.setValue("model", "gpt-3.5-turbo-0125")
        if not self.settings.contains("api_headers"):
            self.settings.setValue("api_headers", '{"x-foo": "true"}')

        # 启动全局热键监听线程
        self.listener = Listener()
        self.listener.signal.connect(self.translate_text)
        self.listener.start()
        
    def translate_text(self, text):
        try:
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
    
    def show_translation(self, translated_text):
        try:
            print(f"Translated text: {translated_text}")
            if self.translator_window and self.translator_window.isVisible():
                self.translator_window.update_html_content(translated_text)
            else:
                self.translator_window = MarkdownWindow(translated_text)
                self.translator_window.display()
        except Exception as e:
            print(e)

    def set_api_key(self):
        try:
            api_key = self.settings.value("api_key", "")
            api_key, ok = QInputDialog.getText(None, " ", "API-Key", text=api_key, flags = Qt.WindowCloseButtonHint | Qt.WindowTitleHint)
            if ok and api_key:
                self.api_key = api_key
                self.settings.setValue("api_key", api_key)  # 保存 API Key
                print(f"API Key{api_key} has been set.")
        except Exception as e:
            print(e)
            QMessageBox.critical(None, "Error", f"An error occurred: {str(e)}")
            
    def set_api_url(self):
        try:
            api_url = self.settings.value("api_url", "")
            api_url, ok = QInputDialog.getText(None, " ", "Base-Url", text=api_url, flags = Qt.WindowCloseButtonHint | Qt.WindowTitleHint)
            if ok and api_url:
                self.api_url = api_url
                self.settings.setValue("api_url", api_url)  # 保存 API URL
                print(f"API URL{api_url} has been set.")
        except Exception as e:
            print(e)
            QMessageBox.critical(None, "Error", f"An error occurred: {str(e)}")

    def set_api_headers(self):
        try:
            api_headers = self.settings.value("api_headers", dict())
            api_headers, ok = QInputDialog.getText(None, " ", "API-Headers", text=api_headers, flags = Qt.WindowCloseButtonHint | Qt.WindowTitleHint)
            if ok and api_headers:
                self.settings.setValue("api_headers", api_headers)  # 保存 API Headers
                print(f"API Headers{api_headers} has been set.")
        except Exception as e:
            print(e)
            QMessageBox.critical(None, "Error", f"An error occurred: {str(e)}")
            
    def select_model(self):
        try:
            # 下拉框选择模型
            models = ["gpt-3.5-turbo-0125", "gpt-4o-mini", "gpt-3.5-turbo"]
            model = self.settings.value("model", "gpt-3.5-turbo")
            model, ok = QInputDialog.getItem(None, " ", "Model", models, models.index(model), False, flags = Qt.WindowCloseButtonHint | Qt.WindowTitleHint)
            if ok:
                self.settings.setValue("model", model) 
                print(f"Model {model} has been selected.")
        except Exception as e:
            print(e)
            QMessageBox.critical(None, "Error", f"An error occurred: {str(e)}")

    def edit_prompt(self):
        try:
            prompt = self.settings.value("prompt", "Translate the following text to Chinese (Simplified), ensuring a professional and accurate tone. Format the translated text using Markdown, ensuring a clean and aesthetically pleasing layout.")
            prompt, ok = QInputDialog.getText(None, " ", "Prompt", text=prompt, flags = Qt.WindowCloseButtonHint | Qt.WindowTitleHint)
            if ok and prompt:
                self.settings.setValue("prompt", prompt)  # 保存提示
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
