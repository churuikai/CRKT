"""
CRKT - CRK Translator
主入口文件，负责应用程序初始化和依赖注入。
"""

import sys
import os

from PyQt5.QtWidgets import QApplication, QMessageBox
from PyQt5.QtGui import QIcon

from core.logger import setup_logging, get_logger
from core.types import AppConfig
from core.listener import Listener
from models.config_manager import ConfigManager
from models.cache_manager import CacheManager
from models.language_detector import LanguageDetector
from models.translation_service import TranslationService
from models.history_manager import HistoryManager
from views.tray_icon import TrayIconView
from views.display_window import DisplayWindowView
from views.settings_dialog import SettingsDialog
from presenters.app_presenter import AppPresenter


def get_app_directory() -> str:
    """获取应用程序目录。"""
    if getattr(sys, 'frozen', False):
        return os.path.dirname(sys.executable)
    else:
        return os.path.dirname(os.path.abspath(__file__))


def create_application() -> tuple:
    """
    创建并配置应用程序实例。
    
    Returns:
        (QApplication, AppPresenter) 元组
    """
    # 获取应用目录
    app_dir = get_app_directory()
    data_dir = os.path.join(app_dir, "data")
    
    # 确保数据目录存在
    if not os.path.exists(data_dir):
        os.makedirs(data_dir)
    
    # 初始化日志系统
    log_file = os.path.join(data_dir, "app.log")
    logger = setup_logging(log_file=log_file)
    logger.info("=" * 50)
    logger.info("CRKT 应用程序启动")
    logger.info(f"应用目录: {app_dir}")
    
    # 创建Qt应用
    QApplication.setApplicationName("CRKTranslator")
    QApplication.setOrganizationName("CRK")
    qt_app = QApplication(sys.argv)
    qt_app.setQuitOnLastWindowClosed(False)
    
    # 初始化图标
    icon_path = os.path.join(app_dir, "icon.png")
    if not os.path.exists(icon_path):
        QMessageBox.critical(None, "错误", f"托盘图标 {icon_path} 未找到！")
        sys.exit(1)
    
    app_icon = QIcon(icon_path)
    qt_app.setWindowIcon(app_icon)
    
    # 创建Model层组件
    config_manager = ConfigManager(app_dir)
    cache_path = os.path.join(data_dir, "cache.pkl")
    cache_manager = CacheManager(cache_path)
    history_path = os.path.join(data_dir, "history.json")
    history_manager = HistoryManager(history_path)
    language_detector = LanguageDetector()
    translation_service = TranslationService(cache_manager)
    
    # 创建View层组件
    tray_view = TrayIconView(app_icon)
    display_view = DisplayWindowView(app_dir)
    
    # 创建监听器（使用配置中的热键设置）
    config = config_manager.config
    listener = Listener(
        translate_key=config.translate_hotkey.key,
        append_key=config.append_hotkey.key,
        translate_enabled=config.translate_hotkey.enabled,
        append_enabled=config.append_hotkey.enabled,
    )
        
    # 设置对话框工厂函数（依赖注入）
    def settings_dialog_factory(**kwargs):
        return SettingsDialog(**kwargs)
    
    # 创建Presenter
    presenter = AppPresenter(
        config_manager=config_manager,
        cache_manager=cache_manager,
        language_detector=language_detector,
        translation_service=translation_service,
        history_manager=history_manager,
        tray_view=tray_view,
        display_view=display_view,
        listener=listener,
        settings_dialog_factory=settings_dialog_factory,
    )
    
    # 连接退出信号
    qt_app.aboutToQuit.connect(tray_view.hide)
    
    return qt_app, presenter


def main() -> int:
    """
    应用程序主入口。
    
    Returns:
        退出码
    """
    try:
        qt_app, presenter = create_application()
        presenter.start()
        return qt_app.exec_()
        
    except Exception as e:
        import traceback
        error_msg = f"启动错误: {e}\n{traceback.format_exc()}"
        
        logger = get_logger()
        logger.critical(error_msg)
        
        # 写入错误日志
        app_dir = get_app_directory()
        error_log_path = os.path.join(app_dir, "startup_error.log")
        with open(error_log_path, "w", encoding="utf-8") as f:
            f.write(error_msg)
            
        # 显示错误消息
        if getattr(sys, 'frozen', False):
            QMessageBox.critical(None, "启动错误", error_msg)
        else:
            print(error_msg)
        
        return 1


if __name__ == "__main__":
    sys.exit(main())
