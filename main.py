import sys
import os
import json
import webbrowser
from PyQt5.QtWidgets import (
    QApplication, QSystemTrayIcon, QMenu, QAction, QMessageBox
)
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import QSettings, Qt
from translator import Translator  # 假设这些文件在同一目录或PYTHONPATH中
from listener import Listener
from show import DisplayWindow
from settings_dialog import SettingsDialog

class TranslatorApp(QApplication):
    # Windows自启动注册表路径
    REG_RUN_PATH = "HKEY_CURRENT_USER\\Software\\Microsoft\\Windows\\CurrentVersion\\Run"
    APP_NAME_REG = "CRKT"  # 注册表项的唯一名称
    
    def __init__(self, sys_argv):
        super().__init__(sys_argv)
        self.setQuitOnLastWindowClosed(False)
        
        # 初始化配置
        if not os.path.exists("data"):
            os.makedirs("data")
        self.config_path = "data/config.json"
        self.config = self._load_config()
        
        # 翻译线程
        self.translator = None
        
        # 用户是否手动最小化窗口
        self.user_minimized = False
        
        # 初始化UI组件
        self._init_components()
        
    def _load_config(self):
        """加载JSON配置文件"""
        default_config = {
            "skills": [
                {
                    "name": "通用翻译",
                    "prompt": (
                        "你将作为一个专业的翻译助手，任务是将文本从英文翻译成中文。\n"
                        "翻译时需要遵循以下要求：\n"
                        "1. 准确性：确保翻译内容的准确性，保留专业术语和专有名词，用反引号`标出。\n"
                        "2. 格式要求：使用 Markdown 语法输出内容。\n"
                        "3. 公式格式：任何时候所有公式、数学字母都必须使用四个$包围，忽略任何tag和序号。\n"
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
            ],
            "selected_skill": "通用翻译",
            "api_profiles": [
                {
                    "name": "默认API",
                    "api_key": "",
                    "base_url": "https://api.openai.com/v1/",
                }
            ],
            "selected_api": "默认API",
            "models": [
                "gpt-4.1-nano", "gpt-4o-mini", "gpt-4o",
                "gemini-2.5-flash", "doubao-lite-32k", 
                "deepseek-chat"
            ],
            "selected_model": "gpt-4.1-nano",
            "shift_listener": True,
            "start_on_boot": False,
            "prompt": ""  # 将由selected_skill自动填充
        }
        
        try:
            if os.path.exists(self.config_path):
                with open(self.config_path, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                # 确保配置中包含所有必要的字段
                for key, value in default_config.items():
                    if key not in config:
                        config[key] = value
            else:
                config = default_config
                self._save_config(config)
                
            # 确保prompt与selected_skill同步
            self._sync_selected_skill_prompt(config)
            return config
        except Exception as e:
            print(f"加载配置文件出错: {e}")
            return default_config
    
    def _save_config(self, config=None):
        """保存配置到JSON文件"""
        try:
            if config is None:
                config = self.config
            with open(self.config_path, 'w', encoding='utf-8') as f:
                json.dump(config, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"保存配置文件出错: {e}")
    
    def _sync_selected_skill_prompt(self, config=None):
        """同步当前选中技能的提示词到prompt配置"""
        if config is None:
            config = self.config
            
        skills = config.get("skills", [])
        selected_skill_name = config.get("selected_skill", "")
        
        found_skill = next((s for s in skills if s["name"] == selected_skill_name), None)
        
        if found_skill:
            config["prompt"] = found_skill["prompt"]
        elif skills:  # 如果当前选择无效，则使用第一个可用技能
            print(f"警告: 未找到选中的技能 '{selected_skill_name}'。将使用第一个可用技能。")
            config["selected_skill"] = skills[0]["name"]
            config["prompt"] = skills[0]["prompt"]
        else:  # 如果技能列表为空或损坏，使用绝对备用方案
            print("警告: 技能列表为空。将使用默认提示词。")
            default_prompt = "Translate the following text: {selected_text}"
            config["selected_skill"] = "通用翻译"
            config["prompt"] = default_prompt
            # 如果技能列表为空，重新初始化默认技能
            if not skills:
                config["skills"] = [{"name": "通用翻译", "prompt": default_prompt}]
    
    def _init_components(self):
        """初始化所有UI组件"""
        # 初始化图标
        if not self._init_icon():
            return  # 初始化图标失败，_init_icon中已调用sys.exit
            
        # 创建托盘图标和菜单
        self._init_tray_icon()
        
        # 创建信息显示窗口和热键监听
        self.display_window = DisplayWindow()
        # 监听窗口状态改变事件
        self.display_window.windowStateChanged.connect(self.on_window_state_changed)
        
        self.listener = Listener()
        self._init_listener_signals()
        
    def _init_icon(self):
        """初始化图标"""
        icon_path = "icon.png"  # 确保icon.png在脚本/EXE同目录下
 
        if not os.path.exists(icon_path):  # 最终检查
            QMessageBox.critical(None, "错误", f"托盘图标 {icon_path} 最终未找到！")
            sys.exit(1)
            return False
        self.setWindowIcon(QIcon(icon_path))
        return True
        
    def _init_tray_icon(self):
        """创建托盘图标和菜单"""
        self.tray_icon = QSystemTrayIcon(self.windowIcon(), self)
        self.tray_icon.setToolTip("CRK-Translator")
        
        # 创建菜单
        self.menu = QMenu()
        
        # 设置菜单项
        self.settings_action = QAction("设置", self)
        self.settings_action.triggered.connect(self.open_settings)
        
        self.shift_listener_action = QAction("启用双击shift", self)
        self.shift_listener_action.setCheckable(True)
        self.shift_listener_action.setChecked(self.config.get("shift_listener", True))
        self.shift_listener_action.triggered.connect(self.edit_shift_listener)
        
        self.startup_action = QAction("开机自启动", self)
        self.startup_action.setCheckable(True)
        self.startup_action.setChecked(self.config.get("start_on_boot", False))
        self.startup_action.triggered.connect(self.toggle_startup)
        
        self.about_action = QAction("关于", self)
        self.about_action.triggered.connect(lambda: webbrowser.open("https://github.com/churuikai/CRKT"))
        
        self.quit_action = QAction("退出", self)
        self.quit_action.triggered.connect(self.quit_app)
        
        # 添加菜单项
        self.menu.addAction(self.settings_action)
        self.menu.addSeparator()
        self.menu.addAction(self.shift_listener_action)
        self.menu.addAction(self.startup_action)
        self.menu.addSeparator()
        self.menu.addAction(self.about_action)
        self.menu.addSeparator()
        self.menu.addAction(self.quit_action)
        
        self.tray_icon.setContextMenu(self.menu)
        self.tray_icon.show()
    
    def _init_listener_signals(self):
        """绑定全局热键监听信号"""
        self.listener.double_ctrl.connect(self.get_text)
        
        # 根据配置设置shift监听
        if self.config.get("shift_listener", True):
            try:
                self.listener.double_shift.connect(self.append_text)
            except TypeError:
                pass  # 已连接
                
        self.display_window.append_text.connect(self.translate_text)
        self.listener.start()
    
    def on_window_state_changed(self, state):
        """监听窗口状态变化"""
        if state & Qt.WindowMinimized:
            self.user_minimized = True
        else:
            self.user_minimized = False
    
    def get_selected_api_profile(self):
        """获取当前选中的API配置"""
        profiles = self.config.get("api_profiles", [])
        selected_api_name = self.config.get("selected_api", "")
        
        selected_profile = next((p for p in profiles if p["name"] == selected_api_name), None)
        
        if not selected_profile and profiles:
            selected_profile = profiles[0]
            self.config["selected_api"] = selected_profile["name"]
            self._save_config()
        elif not selected_profile and not profiles:  # 不存在配置文件
            # 返回默认的非功能性配置结构
            return {"name": "无可用API", "api_key": "", "base_url": ""}
            
        return selected_profile or {"name": "默认API", "api_key": "", "base_url": "https://api.openai.com/v1/"}
            
    def open_settings(self):
        """打开综合设置对话框"""
        api_profiles = self.config.get("api_profiles", [])
        selected_api = self.config.get("selected_api", "")
        models = self.config.get("models", [])
        selected_model = self.config.get("selected_model", "")
        skills = self.config.get("skills", [])
        selected_skill_name = self.config.get("selected_skill", "")
        
        dlg = SettingsDialog(
            api_profiles=api_profiles,
            selected_api=selected_api,
            models=models,
            selected_model=selected_model,
            skills=skills,
            selected_skill_name=selected_skill_name,
            parent=None 
        )
        
        dlg.skill_selected.connect(self.on_skill_selected)
        
        if dlg.exec_() == SettingsDialog.Accepted:
            self.config["api_profiles"] = dlg.get_api_profiles()
            self.config["selected_api"] = dlg.get_selected_api()
            self.config["models"] = dlg.get_models()
            self.config["selected_model"] = dlg.get_selected_model()
            self.config["skills"] = dlg.get_skills()
            self.config["selected_skill"] = dlg.get_selected_skill_name()
            
            self._sync_selected_skill_prompt()  # 确保根据新选择的技能更新prompt
            self._save_config()
            
            QMessageBox.information(None, "成功", "设置已更新！")
            
    def on_skill_selected(self, chosen_skill_dict):
        """当选择技能时触发 (from SettingsDialog)"""
        if not chosen_skill_dict or "name" not in chosen_skill_dict or "prompt" not in chosen_skill_dict:
            return
        self.config["selected_skill"] = chosen_skill_dict["name"]
        self.config["prompt"] = chosen_skill_dict["prompt"]
        self._save_config()
    
    def edit_shift_listener(self, checked):
        """双击Shift监听开关"""
        self.config["shift_listener"] = checked
        self._save_config()
        
        if checked:
            try:
                self.listener.double_shift.connect(self.append_text)
            except TypeError:
                pass  # 已连接
        else:
            try:
                self.listener.double_shift.disconnect(self.append_text)
            except TypeError:
                pass  # 未连接或已断开连接
    
    def toggle_startup(self, checked):
        """切换开机自启动功能，主要适用于Windows EXE。"""
        # 首先在设置中存储用户的意图
        # 这确保即使自动设置失败或不适用，配置也能反映所需状态
        self.config["start_on_boot"] = checked
        self._save_config()
        
        is_windows = sys.platform == "win32"
        is_frozen = getattr(sys, 'frozen', False)  # 如果作为EXE运行（例如PyInstaller）则为True
        
        if is_windows and is_frozen:
            # 理想情况：Windows且作为EXE运行
            app_path_for_startup = sys.executable  # EXE的完整路径
            # 注册表Run键中的路径如果包含空格通常会被引号括起来
            registry_value_path = f'"{app_path_for_startup}"'
            try:
                settings_reg = QSettings(self.REG_RUN_PATH, QSettings.NativeFormat)
                if checked:
                    settings_reg.setValue(self.APP_NAME_REG, registry_value_path)
                    QMessageBox.information(None, "设置成功", "已设置为开机自启动。")
                else:
                    settings_reg.remove(self.APP_NAME_REG)
                    QMessageBox.information(None, "设置成功", "已取消开机自启动。")
                settings_reg.sync()  # 确保更改被写入
            except Exception as e:
                QMessageBox.warning(None, "设置失败", f"无法修改注册表: {e}\n请尝试以管理员身份运行。")
                # 如果注册表修改失败，恢复复选框状态和设置
                self.startup_action.setChecked(not checked)  # 恢复UI到先前状态
                self.config["start_on_boot"] = not checked  # 恢复设置到先前状态
                self._save_config()
        else:
            # 非理想情况（非Windows或非EXE），提供信息
            # 复选框状态（由checked参数驱动）和配置设置（已在上面设置）
            # 将反映用户的选择，但不会进行自动设置
            # 用户会得到关于手动设置的信息
            message = ""
            if not is_windows:
                message = ("自动设置开机自启动功能目前仅支持 Windows 系统。\n"
                          "如需在其他操作系统上设置，请参考您的系统文档手动添加启动项。")
            elif not is_frozen:  # 是Windows，但不是frozen（作为脚本运行）
                message = ("自动设置开机自启动功能专为本应用的 EXE 版本设计。\n"
                          "当前您正在以 Python 脚本模式运行。\n"
                          "如果您希望打包后的 EXE 版本开机自启动，请在该 EXE 程序中勾选此选项。\n"
                          "若希望此脚本开机运行，请手动创建任务计划或启动脚本。")
            
            QMessageBox.information(None, "提示", message)
            # 无需在此恢复复选框或设置，因为用户的意图已被记录
            # 菜单项文本"(仅Win EXE)"已经暗示了限制
    
    def append_text(self, text):
        """添加文本到暂存区"""
        try:
            if self.user_minimized:
                self.display_window.append_text_without_show(text)
            else:
                self.display_window.append_text_content(text)
        except Exception as e:
            self._handle_error(f"添加文本时出错: {e}")
            
    def get_text(self, text):
        """获取暂存区 + 选中的文本, 并显示窗口"""
        try:
            self.user_minimized = False  # 新的翻译请求意味着应该显示窗口
            self.display_window.get_text(text)  # 此方法应处理显示窗口
        except Exception as e:
            self._handle_error(f"获取文本时出错: {e}")
            
    def translate_text(self, text):
        """调用 Translator 线程，翻译文本"""
        try:
            if not text.strip():
                return
                
            self._cancel_previous_translation()
            
            if not self.user_minimized:
                self.display_window.update_html_content(
                    '<h4 style="color: #82529d;">wait...</h4>'
                )
            
            api_profile = self.get_selected_api_profile()
            api_key = api_profile.get("api_key", "")
            base_url = api_profile.get("base_url", "")
            
            if not api_key and "无可用API" not in api_profile.get("name", ""):  # 简单检查缺失的密钥
                QMessageBox.warning(None, "API 密钥缺失", f"API配置 '{api_profile.get('name')}' 缺少 API Key。\n请在设置中配置。")
                self.display_window.update_html_content('<p style="color: red;">API Key 未设置</p>')
                return
                
            self.translator = Translator(
                text,
                api_key=api_key,
                base_url=base_url,
                model=self.config.get("selected_model", "gpt-4o-mini"),
                prompt=self.config.get("prompt", "")
            )
            self.translator.signal.connect(self.show_translation)
            self.translator.start()
        except Exception as e:
            self._handle_error(f"翻译过程中出错: {e}")
    
    def _cancel_previous_translation(self):
        """取消之前的翻译线程"""
        if self.translator and self.translator.isRunning():
            try:
                self.translator.terminate() 
                self.translator.wait(500) 
                if self.translator.isRunning():  # 终止并等待后仍在运行
                    print("警告: 翻译线程未能立即终止。")
                # 尝试断开信号连接，以防它延迟发出
                try:
                    self.translator.signal.disconnect(self.show_translation)
                except TypeError:
                    pass  # 信号未连接或已断开连接
            except RuntimeError as e:
                print(f"信息: 终止线程时发生运行时错误 (可能已结束): {e}")
            except Exception as e:
                print(f"取消翻译线程时出错: {e}")
            finally:
                self.translator = None  # 清除引用
            
    def show_translation(self, translated_text):
        """显示翻译结果"""
        try:
            if translated_text.startswith('@An error occurred:'):
                error_msg = translated_text.replace('@An error occurred:', '').strip()
                # 不在这里关闭display_window，让用户看到错误或重试
                # self.display_window.close() 
                QMessageBox.critical(None, "翻译错误", error_msg)
                # 如果窗口打开，也在显示窗口中更新错误
                if self.display_window.isVisible() or self.user_minimized:  # user_minimized可能意味着它保存着内容
                    self.display_window.update_html_content(f'<p style="color: red;">翻译错误: {error_msg}</p>')
            else:
                if self.user_minimized:
                    self.display_window.update_html_without_show(translated_text)
                else:
                    self.display_window.update_html_content(translated_text)
        except Exception as e:
            self._handle_error(f"显示翻译结果时出错: {e}")
        finally:
            # self.translator应在_cancel_previous_translation中清除或在线程完成后清除
            # 如果从信号调用，线程已完成
            self.translator = None
            
    def quit_app(self):
        """退出程序"""
        print("正在退出应用程序...")
        try:
            self._cancel_previous_translation()
            if hasattr(Translator, 'cache') and Translator.cache is not None:
                Translator.cache.save()
        except Exception as e:
            print(f"退出时保存缓存出错: {e}")
        
        # 如果监听器线程有stop方法，干净地关闭它
        if hasattr(self.listener, 'stop') and callable(self.listener.stop):
            try:
                self.listener.stop()
                self.listener.wait(500)  # 等待监听器线程完成
            except Exception as e:
                print(f"停止监听线程时出错: {e}")
        self.quit()
        
    def _handle_error(self, error_msg):
        """统一错误处理"""
        print(f"错误: {error_msg}")
        # 避免在这里直接关闭display_window，让调用者决定或在其中显示错误
        QMessageBox.critical(None, "应用程序错误", str(error_msg))

if __name__ == "__main__":
    QApplication.setApplicationName("CRKTranslator")
    QApplication.setOrganizationName("CRK")  # 用于QSettings的默认位置（如果路径不明确）
    app = TranslatorApp(sys.argv)
    # 确保退出时清理托盘图标，尽管QApplication.quit()通常处理它
    app.aboutToQuit.connect(app.tray_icon.hide) 
    sys.exit(app.exec_())