import sys
import os
import json
from PyQt5.QtWidgets import (
    QApplication, QSystemTrayIcon, QMenu, QAction, QInputDialog,
    QMessageBox
)
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import QSettings, Qt, QTextCodec

from translator import Translator
from listener import Listener
from show import DisplayWindow
from skill_manager import SkillManager
from api_settings_dialog import ApiSettingsDialog

class TranslatorApp(QApplication):
    def __init__(self, sys_argv):
        super().__init__(sys_argv)
        self.setQuitOnLastWindowClosed(False)

        # 初始化图标与菜单
        self._init_icon()
        self._init_tray_icon()
        
        # 创建信息显示窗口和热键监听
        self.display_window = DisplayWindow()
        self.listener = Listener()
        self._init_listener_signals()

        # 初始化菜单
        self.menu = QMenu()
        self._create_menu_actions()
        self.tray_icon.setContextMenu(self.menu)
        self.tray_icon.show()

        # 加载/初始化配置
        self.settings = QSettings("config.ini", QSettings.IniFormat)
        self.settings.setIniCodec(QTextCodec.codecForName("UTF-8"))
        self._init_settings()

    # --------------------------
    # 初始化/设置相关的辅助方法
    # --------------------------
    def _init_icon(self):
        """初始化图标"""
        icon_path = "icon.png"
        if not os.path.exists(icon_path):
            QMessageBox.critical(None, "Error", "Tray icon not found!")
            sys.exit()
        self.setWindowIcon(QIcon(icon_path))

    def _init_tray_icon(self):
        """创建托盘图标"""
        self.tray_icon = QSystemTrayIcon(self.windowIcon(), self)
        self.tray_icon.setToolTip("CRK-Translator")

    def _init_listener_signals(self):
        """绑定全局热键监听信号"""
        self.listener.double_ctrl.connect(self.get_text)
        self.listener.double_shift.connect(self.append_text)
        self.listener.start()
        self.display_window.append_text.connect(self.translate_text)

    def _init_settings(self):
        """
        加载并初始化配置
        注意把 JSON 序列化时 ensure_ascii=False, 并使用 UTF-8 编码
        """
        if not self.settings.contains("skills"):
            default_skills = [
                {
                    "name": "通用翻译",
                    "prompt": (
                        "你将作为一个专业的翻译助手，任务是将文本从英文翻译成中文。\n"
                        "翻译时需要遵循以下要求：\n"
                        "1. 准确性：确保翻译内容的准确性，保留专业术语和专有名词，用反引号`标出。\n"
                        "2. 格式要求：使用 Markdown 语法输出内容。\n"
                        "3. 公式格式：任何时候所有公式、数学字母都必须使用四个$$$$包围，忽略任何tag和序号。\n"
                        "4. 使用常见字符: 任何公式中不常见的字符替换成常见标准的字符，输出latex代码，确保katex可以解析，例如:\n"
                        "   - '𝑆'换成'S', '𝐹'换成'F', '𝑛'换成'n', 'i'换成i\n"
                        "   - '...' 换成 '\\cdots', '.'换成 '\\cdot'\n"
                        "5. 注意，如果是单个单词或短语，你可以精炼地道的解释该单词/短语的含义，给出音标和简单例证。\n"
                        "6. 如果是代码或注释，解释代码含义或补全代码\n\n"
                        "下面是需要翻译的内容：{selected_text}"
                    )
                },
                {
                    "name": "代码助手",
                    "prompt": "请逐行解释代码，下面是代码：{selected_text}"
                },
            ]
            self.settings.setValue("skills", json.dumps(default_skills, ensure_ascii=False))


        if not self.settings.contains("selected_skill"):
            self.settings.setValue("selected_skill", "通用翻译")  

        # 注意：选中的技能，需要将其 prompt 同步到 self.settings.value("prompt")
        self.sync_selected_skill_prompt()

        # 默认模型
        if not self.settings.contains("model"):
            self.settings.setValue("model", "gpt-4o-mini")

        # 默认 Headers
        if not self.settings.contains("api_headers"):
            self.settings.setValue("api_headers", '{"x-foo": "true"}')

        # 默认 URL
        if not self.settings.contains("api_url"):
            self.settings.setValue("api_url", "例如https://api.gpt.ge/v1/，注意一般需要附加'/v1/'")

        # 默认监听开关
        if not self.settings.contains("shift_listener"):
            self.settings.setValue("shift_listener", "1")
        
        # 更新 shift 监听开关
        self.shift_listener_action.setChecked(
            self.settings.value("shift_listener", "1") == "1"
        )
        
    def sync_selected_skill_prompt(self):
        """
        根据当前 selected_skill，从 skills 列表里找出对应 prompt，
        并更新到 self.settings["prompt"]。
        """
        skills_str = self.settings.value("skills", "[]")
        try:
            skills_list = json.loads(skills_str)
        except:
            skills_list = []

        selected_skill_name = self.settings.value("selected_skill", "")
        found = next((s for s in skills_list if s["name"] == selected_skill_name), None)
        if found:
            self.settings.setValue("prompt", found["prompt"])
        else:
            # 找不到说明配置可能被手动改了，可以设置个默认prompt
            self.settings.setValue("prompt", "Translate the following text...")
            
            
    def _create_menu_actions(self):
        """创建托盘菜单中的所有操作并添加到菜单"""
        # 设置 API
        self.api_settings_action = QAction("设置 API", self)
        self.api_settings_action.triggered.connect(self.open_api_settings)
        self.menu.addAction(self.api_settings_action)
        self.menu.addSeparator()

        # 模型选择
        self.model_action = QAction("选择模型", self)
        self.model_action.triggered.connect(self.select_model)
        self.menu.addAction(self.model_action)

        self.menu.addSeparator()

        # 替换成“选择技能”功能
        self.prompt_action = QAction("选择技能", self)
        self.prompt_action.triggered.connect(self.open_skill_manager)
        self.menu.addAction(self.prompt_action)

        self.menu.addSeparator()

        # 监听开关
        self.shift_listener_action = QAction("启用双击shift", self)
        self.shift_listener_action.setCheckable(True)
        self.shift_listener_action.triggered.connect(self.edit_shift_listener)
        self.menu.addAction(self.shift_listener_action)

        self.menu.addSeparator()

        # 退出
        self.exit_action = QAction("退出", self)
        self.exit_action.triggered.connect(self.quit_app)
        self.menu.addAction(self.exit_action)

    # --------------------------
    # 监听事件与功能相关方法
    # --------------------------
    
    def open_skill_manager(self):
        """ 打开技能管理窗口 """
        skills_str = self.settings.value("skills", "[]")
        try:
            skills_list = json.loads(skills_str)
        except:
            skills_list = []
        selected_skill_name = self.settings.value("selected_skill", "")

        dlg = SkillManager(skills=skills_list, selected_skill_name=selected_skill_name)
        # 监听 skill_selected 信号
        dlg.skill_selected.connect(self.on_skill_selected)

        if dlg.exec_() == dlg.Accepted:
            # 窗口关闭并保存时，将最新的技能列表存回 config
            self.settings.setValue("skills", json.dumps(dlg.skills))
            # 重新同步一次，以防默认技能被修改等情况
            self.sync_selected_skill_prompt()

    def on_skill_selected(self, chosen_skill):
        """
        当在SkillManager中选择了某个技能(点击“设为默认”)时会触发此槽函数。
        写回到config，然后即时更新提示词
        """
        self.settings.setValue("selected_skill", chosen_skill["name"])
        self.settings.setValue("prompt", chosen_skill["prompt"])
        print(f"Skill '{chosen_skill['name']}' is selected. Prompt is updated.")
    
    def edit_shift_listener(self):
        """双击Shift监听开关"""
        if self.settings.value("shift_listener", True) == "1":
            self.shift_listener_action.setChecked(False)
            self.settings.setValue("shift_listener", "0")
            self.listener.double_shift.disconnect(self.append_text)
        else:
            self.shift_listener_action.setChecked(True)
            self.settings.setValue("shift_listener", "1")
            self.listener.double_shift.connect(self.append_text)

    def append_text(self, text):
        """添加文本到暂存区"""
        try:
            self.display_window.append_text_content(text)
        except Exception as e:
            self._handle_error(e)

    def get_text(self, text):
        """获取暂存区 + 选中的文本"""
        self.display_window.get_text(text)

    # --------------------------
    # 翻译相关方法
    # --------------------------
    def translate_text(self, text):
        """调用 Translator 线程，翻译文本"""
        try:
            self.display_window.update_html_content(
                '<h4 style="color: #82529d;">翻译中...</h4>'
            )
            self.transaltor = Translator(
                text,
                api_key=self.settings.value("api_key"),
                base_url=self.settings.value("api_url"),
                default_headers=eval(self.settings.value("api_headers")),
                model=self.settings.value("model"),
                prompt=self.settings.value("prompt")
            )
            self.transaltor.signal.connect(self.show_translation)
            self.transaltor.start()
        except Exception as e:
            self._handle_error(e)

    def show_translation(self, translated_text):
        """显示翻译结果"""
        try:
            if '@An error occurred:' in translated_text:
                self.display_window.close()
                QMessageBox.critical(None, "Error", translated_text)
            else:
                self.display_window.update_html_content(translated_text)
        except Exception as e:
            self._handle_error(e)

    # --------------------------
    # 设置项编辑相关方法
    # --------------------------

    def open_api_settings(self):
        """
        打开“设置 API”的对话框，可同时编辑 api_key / base_url / api_headers
        """
        current_key = self.settings.value("api_key", "")
        current_url = self.settings.value("api_url", "")
        current_headers = self.settings.value("api_headers", "")

        dlg = ApiSettingsDialog(
            api_key=current_key,
            base_url=current_url,
            api_headers=current_headers,
            parent=None
        )
        if dlg.exec_() == dlg.Accepted:
            new_key, new_url, new_headers = dlg.get_values()
            self.settings.setValue("api_key", new_key)
            self.settings.setValue("api_url", new_url)
            self.settings.setValue("api_headers", new_headers)
            QMessageBox.information(
                None, "提示", "API 设置已更新成功！"
            )

    def select_model(self):
        """选择模型"""
        try:
            models = [
                "gpt-4o-mini", "gpt-3.5-turbo", "claude-3-haiku-20240307",
                "gemini-1.5-flash", "doubao-lite-32k", "glm-4-air",
                "deepseek-chat", "deepseek-coder"
            ]
            current_model = self.settings.value("model", "gpt-4o-mini")
            chosen, ok = QInputDialog.getItem(
                None, " ", "Model", models, models.index(current_model),
                False, flags=Qt.WindowCloseButtonHint | Qt.WindowTitleHint | Qt.WindowStaysOnTopHint
            )
            if ok:
                self.settings.setValue("model", chosen)
                print(f"Model {chosen} has been selected.")
        except Exception as e:
            self._handle_error(e)

    # --------------------------
    # 退出与错误处理
    # --------------------------
    def quit_app(self):
        """退出程序"""
        print("Quitting the application...")
        # 缓存持久化
        Translator.cache.save()
        self.quit()

    def _handle_error(self, error):
        """统一错误处理"""
        print(error)
        self.display_window.close()
        QMessageBox.critical(None, "Error", f"An error occurred: {str(error)}")


if __name__ == "__main__":
    app = TranslatorApp(sys.argv)
    sys.exit(app.exec_())
