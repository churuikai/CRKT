"""Main application presenter module."""

import sys
from typing import Optional

from PyQt5.QtCore import Qt, QSettings
from PyQt5.QtWidgets import QSystemTrayIcon, QMessageBox

from core.logger import get_logger
from core.types import (
    AppConfig, TranslationRequest, TranslationResult, 
    HotkeyConfig, LanguageInfo,
)
from models.config_manager import ConfigManager
from models.cache_manager import CacheManager
from models.language_detector import LanguageDetector
from models.translation_service import TranslationService
from models.history_manager import HistoryManager
from views.tray_icon import TrayIconView
from views.display_window import DisplayWindowView

logger = get_logger("AppPresenter")


class AppPresenter:
    """应用程序主协调器，实现MVP模式中的Presenter角色。"""
    
    REG_RUN_PATH = "HKEY_CURRENT_USER\\Software\\Microsoft\\Windows\\CurrentVersion\\Run"
    APP_NAME_REG = "CRKT"
    
    def __init__(
        self,
        config_manager: ConfigManager,
        cache_manager: CacheManager,
        language_detector: LanguageDetector,
        translation_service: TranslationService,
        history_manager: HistoryManager,
        tray_view: TrayIconView,
        display_view: DisplayWindowView,
        listener,  # Listener类型，避免循环导入
        settings_dialog_factory,  # SettingsDialog工厂函数
    ):
        """
        初始化应用程序协调器。
        """
        self._config_manager = config_manager
        self._cache_manager = cache_manager
        self._language_detector = language_detector
        self._translation_service = translation_service
        self._history_manager = history_manager
        self._tray_view = tray_view
        self._display_view = display_view
        self._listener = listener
        self._settings_dialog_factory = settings_dialog_factory
        
        self._settings_dialog: Optional[object] = None
        self._user_minimized = False
        
        # 当前翻译上下文（用于翻译完成后创建记录）
        self._current_translation_context: Optional[dict] = None
        
        self._setup_bindings()
        logger.info("AppPresenter初始化完成")
    
    def _setup_bindings(self) -> None:
        """设置所有绑定和信号连接。"""
        config = self._config_manager.config
        
        # 托盘图标事件
        self._tray_view.set_on_settings_click(self._on_settings_click)
        self._tray_view.set_on_startup_toggle(self._on_startup_toggle)
        self._tray_view.set_on_source_comparison_toggle(self._on_source_comparison_toggle)
        self._tray_view.set_on_quit_click(self._on_quit)
        self._tray_view.set_on_tray_activated(self._on_tray_activated)
        
        # 设置托盘图标初始状态
        self._tray_view.set_startup_checked(config.start_on_boot)
        self._tray_view.set_source_comparison_checked(config.show_source_comparison)
        
        # 显示窗口事件
        self._display_view.window_state_changed.connect(self._on_window_state_changed)
        self._display_view.window_closed.connect(self._on_window_closed)
        self._display_view.text_ready.connect(self._on_translate_text)
        self._display_view.page_ready.connect(self._apply_initial_config)
        
        # 监听器事件
        self._listener.translate_triggered.connect(self._on_get_text)
        if config.append_hotkey.enabled:
            self._listener.append_triggered.connect(self._on_append_to_source)
    
    def _apply_initial_config(self) -> None:
        """应用初始配置。"""
        config = self._config_manager.config
        
        # 根据配置初始化编辑器
        self._display_view.set_comparison_mode(config.show_source_comparison)
    
    def start(self) -> None:
        """启动应用程序。"""
        self._tray_view.show()
        self._listener.start()
        logger.info("应用程序已启动")
    
    def stop(self) -> None:
        """停止应用程序。"""
        logger.info("正在退出应用程序...")
        self._translation_service.cancel()
        
        try:
            self._cache_manager.save()
        except Exception as e:
            logger.error(f"退出时保存缓存出错: {e}")
        
        try:
            self._history_manager.save()
        except Exception as e:
            logger.error(f"退出时保存历史记录出错: {e}")
        
        if hasattr(self._listener, 'stop') and callable(self._listener.stop):
            try:
                self._listener.stop()
                self._listener.wait(500)
            except Exception as e:
                logger.error(f"停止监听线程时出错: {e}")
    
    # 托盘图标事件处理
    def _on_settings_click(self) -> None:
        """打开设置对话框。"""
        if self._settings_dialog is not None and self._settings_dialog.isVisible():
            self._settings_dialog.activateWindow()
            self._settings_dialog.raise_()
            return
        
        config = self._config_manager.config
        
        def save_callback(data: dict) -> None:
            self._config_manager.update_from_dict(data)
        
        self._settings_dialog = self._settings_dialog_factory(
            api_profiles=[p.to_dict() for p in config.api_profiles],
            selected_api=config.selected_api,
            models=config.models.copy(),
            selected_model=config.selected_model,
            skills=[s.to_dict() for s in config.skills],
            selected_skill_name=config.selected_skill,
            target_language=config.target_language,
            translate_hotkey=config.translate_hotkey.to_dict(),
            append_hotkey=config.append_hotkey.to_dict(),
            parent=None,
            save_callback=save_callback,
        )
        
        self._settings_dialog.skill_selected.connect(self._on_skill_selected)
        self._settings_dialog.hotkey_changed.connect(self._on_hotkey_changed)
        self._settings_dialog.show()
        self._settings_dialog.raise_()
        self._settings_dialog.activateWindow()
    
    def _on_skill_selected(self, chosen_skill_dict: dict) -> None:
        """处理技能选择。"""
        if not chosen_skill_dict or "name" not in chosen_skill_dict or "prompt" not in chosen_skill_dict:
            return
        self._config_manager.update_config(
            selected_skill=chosen_skill_dict["name"],
            prompt=chosen_skill_dict["prompt"],
        )
    
    def _on_hotkey_changed(self, hotkey_type: str, key: str, enabled: bool) -> None:
        """处理热键配置变更。"""
        if hotkey_type == "translate":
            self._listener.set_translate_hotkey(key, enabled)
            self._config_manager.update_config(translate_hotkey=HotkeyConfig(key, enabled))
        elif hotkey_type == "append":
            self._listener.set_append_hotkey(key, enabled)
            self._config_manager.update_config(append_hotkey=HotkeyConfig(key, enabled))
            
            if enabled:
                try:
                    self._listener.append_triggered.connect(self._on_append_to_source)
                except TypeError:
                    pass
            else:
                try:
                    self._listener.append_triggered.disconnect(self._on_append_to_source)
                except TypeError:
                    pass
    
    def _on_source_comparison_toggle(self, checked: bool) -> None:
        """处理原文对照开关切换。"""
        self._config_manager.update_config(show_source_comparison=checked)
        self._display_view.set_comparison_mode(checked)
        logger.info(f"原文对照模式: {'开启' if checked else '关闭'}")
    
    def _on_startup_toggle(self, checked: bool) -> None:
        """处理开机自启动切换。"""
        self._config_manager.update_config(start_on_boot=checked)
        
        is_windows = sys.platform == "win32"
        is_frozen = getattr(sys, 'frozen', False)
        
        if is_windows and is_frozen:
            app_path = f'"{sys.executable}"'
            try:
                settings_reg = QSettings(self.REG_RUN_PATH, QSettings.NativeFormat)
                if checked:
                    settings_reg.setValue(self.APP_NAME_REG, app_path)
                    QMessageBox.information(None, "设置成功", "已设置为开机自启动。")
                else:
                    settings_reg.remove(self.APP_NAME_REG)
                    QMessageBox.information(None, "设置成功", "已取消开机自启动。")
                settings_reg.sync()
            except Exception as e:
                QMessageBox.warning(None, "设置失败", f"无法修改注册表: {e}\n请尝试以管理员身份运行。")
                self._tray_view.set_startup_checked(not checked)
                self._config_manager.update_config(start_on_boot=not checked)
        else:
            message = ""
            if not is_windows:
                message = ("自动设置开机自启动功能目前仅支持 Windows 系统。\n"
                          "如需在其他操作系统上设置，请参考您的系统文档手动添加启动项。")
            elif not is_frozen:
                message = ("自动设置开机自启动功能专为本应用的 EXE 版本设计。\n"
                          "当前您正在以 Python 脚本模式运行。\n"
                          "如果您希望打包后的 EXE 版本开机自启动，请在该 EXE 程序中勾选此选项。\n"
                          "若希望此脚本开机运行，请手动创建任务计划或启动脚本。")
            QMessageBox.information(None, "提示", message)
    
    def _on_quit(self) -> None:
        """处理退出请求。"""
        from PyQt5.QtWidgets import QApplication
        self.stop()
        QApplication.quit()
    
    def _on_tray_activated(self, reason: QSystemTrayIcon.ActivationReason) -> None:
        """处理托盘图标激活事件。"""
        if reason == QSystemTrayIcon.Trigger:
            if self._display_view.isVisible() and not self._display_view.isMinimized():
                self._display_view.hide()
                self._user_minimized = True
            else:
                self._display_view.show_and_activate()
                self._user_minimized = False
                self._display_view.user_closed = False
    
    # 显示窗口事件处理
    def _on_window_state_changed(self, state) -> None:
        """处理窗口状态改变。"""
        if state & Qt.WindowMinimized:
            self._user_minimized = True
        else:
            self._user_minimized = False
    
    def _on_window_closed(self) -> None:
        """处理窗口关闭事件。"""
        self._user_minimized = True
        self._translation_service.cancel()
    
    # 监听器事件处理
    def _on_append_to_source(self, text: str) -> None:
        """处理追加文本到原文区事件（附加热键触发）。"""
        try:
            self._user_minimized = False
            self._display_view.user_closed = False
            
            self._history_manager.append_source_text(text)
            self._display_view.append_source(text, show_window=True)
            
            logger.debug(f"文本已追加到原文区: {len(text)} 字符")
        except Exception as e:
            self._handle_error(f"添加文本到原文区时出错: {e}")
    
    def _on_get_text(self, text: str) -> None:
        """处理获取文本事件（翻译热键触发）。"""
        try:
            self._user_minimized = False
            self._display_view.user_closed = False
            
            # 获取当前状态并决定逻辑
            def on_locked(is_locked):
                def on_source_text(current_text):
                    if is_locked:
                        # 锁定：替换
                        final_text = text if text else current_text
                    else:
                        # 解锁：附加
                        if current_text and text:
                            final_text = current_text + "\n" + text
                        else:
                            final_text = text if text else current_text
                    
                    # 执行翻译
                    self._on_translate_text(final_text)
                
                self._display_view.get_source(on_source_text)
            
            self._display_view.is_locked(on_locked)
        except Exception as e:
            self._handle_error(f"获取文本时出错: {e}")
    
    def _on_translate_text(self, text: str) -> None:
        """处理翻译请求。"""
        try:
            if not text.strip():
                return
            
            # 设置当前原文
            self._history_manager.set_source_text(text)
            self._display_view.update_source(text, show_window=not self._user_minimized)
            
            # 显示等待状态
            if not self._user_minimized:
                self._display_view.update_translation(
                    '<h4 style="color: #82529d;">wait...</h4>'
                )
            
            # 获取API配置
            config = self._config_manager.config
            api_profile = config.get_selected_api_profile()
            
            if not api_profile:
                QMessageBox.warning(None, "API配置缺失", "没有可用的API配置，请在设置中添加。")
                self._display_view.update_content('<p style="color: red;">API配置缺失</p>')
                return
            
            if not api_profile.api_key and "无可用API" not in api_profile.name:
                QMessageBox.warning(
                    None,
                    "API密钥缺失",
                    f"API配置 '{api_profile.name}' 缺少 API Key。\n请在设置中配置。"
                )
                self._display_view.update_content('<p style="color: red;">API Key 未设置</p>')
                return
            
            # 检测语言
            source_lang = self._language_detector.detect(text)
            target_lang = self._language_detector.get_target_language(
                source_lang,
                config.target_language,
            )
            
            # 保存翻译上下文
            self._current_translation_context = {
                "source_text": text,
                "source_language": source_lang,
                "target_language": target_lang,
                "model": config.selected_model,
                "skill": config.selected_skill,
            }
            
            # 创建翻译请求
            request = TranslationRequest(
                text=text,
                source_language=source_lang,
                target_language=target_lang,
                prompt_template=config.prompt,
                api_key=api_profile.api_key,
                base_url=api_profile.base_url,
                model=config.selected_model,
            )
            
            # 开始翻译
            self._translation_service.translate(
                request,
                on_progress=self._on_translation_progress,
                on_complete=self._on_translation_complete,
            )
            
        except Exception as e:
            self._handle_error(f"翻译过程中出错: {e}")
    
    def _on_translation_progress(self, text: str) -> None:
        """处理翻译进度更新。"""
        if self._display_view.user_closed:
            return
        
        if text.startswith('@An error occurred:'):
            error_msg = text.replace('@An error occurred:', '').strip()
            QMessageBox.critical(None, "翻译错误", error_msg)
            if self._display_view.isVisible() or self._user_minimized:
                self._display_view.update_translation(
                    f'<p style="color: red;">翻译错误: {error_msg}</p>',
                    show_window=not self._user_minimized,
                )
        else:
            self._display_view.update_translation(text, show_window=not self._user_minimized)
    
    def _on_translation_complete(self, result: TranslationResult) -> None:
        """处理翻译完成，保存记录并锁定原文区（单栏/双栏统一）。"""
        if result.success and self._current_translation_context:
            ctx = self._current_translation_context
            
            # 保存翻译记录
            self._history_manager.add_record(
                source_text=ctx["source_text"],
                translated_text=result.content,
                source_language=ctx["source_language"].code,
                target_language=ctx["target_language"].code,
                model=ctx["model"],
                skill=ctx["skill"],
            )
            
            # 翻译完成后锁定原文区（单栏/双栏统一逻辑）
            self._display_view.lock_source_pane()
            
            logger.info(f"翻译完成并保存记录，来自缓存: {result.from_cache}")
        elif not result.success:
            logger.error(f"翻译失败: {result.error}")
        
        self._current_translation_context = None
    
    def _handle_error(self, error_msg: str) -> None:
        """统一错误处理。"""
        logger.error(error_msg)
        QMessageBox.critical(None, "应用程序错误", str(error_msg))
