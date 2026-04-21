"""Settings dialog module."""

from typing import List, Dict, Optional, Callable, Any

from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton,
    QListWidget, QWidget, QTabWidget, QGroupBox, QFormLayout, QInputDialog,
    QMessageBox, QListWidgetItem, QSplitter, QTableWidget,
    QTableWidgetItem, QHeaderView, QPlainTextEdit, QStyledItemDelegate,
    QAbstractItemView, QComboBox, QCheckBox
)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QColor, QTextOption

from core.logger import get_logger

logger = get_logger("SettingsDialog")


class MultiLineDelegate(QStyledItemDelegate):
    """多行文本编辑委托。"""
    
    def createEditor(
        self,
        parent: QWidget,
        option: Any,
        index: Any,
    ) -> QPlainTextEdit:
        editor = QPlainTextEdit(parent)
        editor.setWordWrapMode(QTextOption.WordWrap)
        return editor
    
    def setEditorData(self, editor: QPlainTextEdit, index: Any) -> None:
        value = index.model().data(index, Qt.EditRole)
        if value is not None:
            editor.setPlainText(str(value))
    
    def setModelData(
        self,
        editor: QPlainTextEdit,
        model: Any,
        index: Any,
    ) -> None:
        model.setData(index, editor.toPlainText(), Qt.EditRole)


class SettingsDialog(QDialog):
    """综合设置对话框。"""
    
    skill_selected = pyqtSignal(dict)
    
    # 颜色配置
    COLORS: Dict[str, str] = {
        "primary": "#82529d",
        "primary_light": "#a371ba",
        "light_bg": "#f2f0fb",
        "lighter_bg": "#dfddf5",
        "white": "#ffffff",
        "text": "#333333",
        "light_text": "#666666",
        "border": "#d0c9e3",
        "selected_bg": "#e8e6f8"
    }
    
    # 热键配置变更信号
    hotkey_changed = pyqtSignal(str, str, bool)  # hotkey_type, key, enabled
    
    def __init__(
        self,
        api_profiles: Optional[List[Dict]] = None,
        selected_api: str = "",
        models: Optional[List[str]] = None,
        selected_model: str = "",
        skills: Optional[List[Dict]] = None,
        selected_skill_name: str = "",
        target_language: str = "English",
        translate_hotkey: Optional[Dict] = None,
        append_hotkey: Optional[Dict] = None,
        parent: Optional[QWidget] = None,
        save_callback: Optional[Callable[[Dict], None]] = None,
    ):
        super().__init__(parent)
        self.setWindowTitle("设置")
        self.resize(850, 600)
        
        # 初始化数据
        self._api_profiles = api_profiles if api_profiles else []
        self._selected_api = selected_api
        self._models = models if models else []
        self._selected_model = selected_model
        self._skills = skills if skills else []
        self._selected_skill_name = selected_skill_name
        self._target_language = target_language
        self._translate_hotkey = translate_hotkey if translate_hotkey else {"key": "ctrl", "enabled": True}
        self._append_hotkey = append_hotkey if append_hotkey else {"key": "shift", "enabled": True}
        self._save_callback = save_callback
        
        self._apply_stylesheet()
        self._create_ui()
        
        logger.info("设置对话框已创建")
    
    def _apply_stylesheet(self) -> None:
        """应用样式表。"""
        self.setStyleSheet(f"""
            QDialog {{
                background-color: {self.COLORS["white"]};
                font-family: "Segoe UI", Arial, sans-serif;
            }}
            QTabWidget::pane {{
                border: 1px solid {self.COLORS["border"]};
                border-radius: 6px;
                background-color: {self.COLORS["white"]};
                margin-top: -1px;
            }}
            QTabBar::tab {{
                background-color: {self.COLORS["light_bg"]};
                border: 1px solid {self.COLORS["border"]};
                border-bottom-color: none;
                border-top-left-radius: 4px;
                border-top-right-radius: 4px;
                min-width: 8ex;
                padding: 8px 16px;
                margin-right: 2px;
                color: {self.COLORS["text"]};
            }}
            QTabBar::tab:selected {{
                background-color: {self.COLORS["white"]};
                border-bottom-color: {self.COLORS["white"]};
                color: {self.COLORS["primary"]};
                font-weight: bold;
            }}
            QTabBar::tab:hover:!selected {{
                background-color: {self.COLORS["lighter_bg"]};
            }}
            QPushButton {{
                background-color: {self.COLORS["primary_light"]};
                color: white;
                border: none;
                padding: 8px 12px;
                border-radius: 4px;
                min-width: 80px;
            }}
            QPushButton:hover {{
                background-color: {self.COLORS["primary"]};
            }}
            QPushButton:disabled {{
                background-color: #cccccc;
                color: #666666;
            }}
            QLineEdit, QPlainTextEdit {{
                padding: 8px;
                border: 1px solid {self.COLORS["border"]};
                border-radius: 4px;
                background-color: {self.COLORS["white"]};
            }}
            QLineEdit:focus, QPlainTextEdit:focus {{
                border: 1px solid {self.COLORS["primary"]};
            }}
            QListWidget, QTableWidget {{
                border: 1px solid {self.COLORS["border"]};
                border-radius: 4px;
                background-color: {self.COLORS["white"]};
                alternate-background-color: {self.COLORS["light_bg"]};
                selection-background-color: {self.COLORS["selected_bg"]};
            }}
            QTableWidget::item {{
                padding: 4px;
            }}
            QTableWidget::item:selected {{
                background-color: {self.COLORS["selected_bg"]};
                color: {self.COLORS["primary"]};
            }}
            QHeaderView::section {{
                background-color: {self.COLORS["light_bg"]};
                padding: 8px;
                border: 1px solid {self.COLORS["border"]};
                color: {self.COLORS["text"]};
            }}
            QGroupBox {{
                border: 1px solid {self.COLORS["border"]};
                border-radius: 4px;
                margin-top: 16px;
                padding-top: 16px;
                color: {self.COLORS["primary"]};
                font-weight: bold;
            }}
            QSplitter::handle {{
                background-color: {self.COLORS["lighter_bg"]};
                width: 2px;
            }}
        """)
    
    def _create_ui(self) -> None:
        """创建UI界面。"""
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(12, 12, 12, 12)
        main_layout.setSpacing(10)
        
        # 创建标签页
        self._tab_widget = QTabWidget()
        self._tab_widget.setDocumentMode(True)
        
        self._tab_widget.addTab(self._create_api_tab(), "API 设置")
        self._tab_widget.addTab(self._create_model_tab(), "模型设置")
        self._tab_widget.addTab(self._create_skill_tab(), "提示词管理")
        self._tab_widget.addTab(self._create_translation_tab(), "翻译设置")
        
        main_layout.addWidget(self._tab_widget)
        
        # 底部状态栏
        self._status_label = QLabel("准备就绪")
        self._status_label.setStyleSheet(
            f"color: {self.COLORS['light_text']}; padding: 8px;"
        )
        main_layout.addWidget(self._status_label)
    
    def _update_status(self, message: str) -> None:
        """更新状态信息。"""
        self._status_label.setText(message)
        logger.debug(f"状态更新: {message}")
    
    def _save_config(self) -> None:
        """保存配置到文件。"""
        if self._save_callback and callable(self._save_callback):
            config = {
                "api_profiles": self._api_profiles,
                "selected_api": self._selected_api,
                "models": self._models,
                "selected_model": self._selected_model,
                "skills": self._skills,
                "selected_skill": self._selected_skill_name,
                "target_language": self._target_language,
                "translate_hotkey": self._translate_hotkey,
                "append_hotkey": self._append_hotkey,
            }
            self._save_callback(config)
    
    # ==================== API Tab ====================
    def _create_api_tab(self) -> QWidget:
        """创建API设置标签页。"""
        api_tab = QWidget()
        api_layout = QVBoxLayout(api_tab)
        api_layout.setContentsMargins(10, 15, 10, 10)
        
        api_splitter = QSplitter(Qt.Horizontal)
        
        # 左侧API列表
        api_list_widget = QWidget()
        api_list_layout = QVBoxLayout(api_list_widget)
        api_list_layout.setContentsMargins(0, 0, 0, 0)
        
        api_list_group = QGroupBox("API 配置列表")
        api_list_inner_layout = QVBoxLayout(api_list_group)
        
        self._api_list = QListWidget()
        self._api_list.setAlternatingRowColors(True)
        self._api_list.setSelectionMode(QAbstractItemView.SingleSelection)
        api_list_inner_layout.addWidget(self._api_list)
        
        api_btn_layout = QHBoxLayout()
        self._add_api_btn = QPushButton("添加")
        self._remove_api_btn = QPushButton("删除")
        self._select_api_btn = QPushButton("设为默认")
        api_btn_layout.addWidget(self._add_api_btn)
        api_btn_layout.addWidget(self._remove_api_btn)
        api_btn_layout.addWidget(self._select_api_btn)
        api_list_inner_layout.addLayout(api_btn_layout)
        
        api_list_layout.addWidget(api_list_group)
        
        # 右侧API编辑区域
        api_edit_widget = QWidget()
        api_edit_layout = QVBoxLayout(api_edit_widget)
        api_edit_layout.setContentsMargins(0, 0, 0, 0)
        
        api_edit_group = QGroupBox("API 配置详情")
        api_edit_inner_layout = QFormLayout(api_edit_group)
        api_edit_inner_layout.setFieldGrowthPolicy(QFormLayout.AllNonFixedFieldsGrow)
        
        self._api_name_edit = QLineEdit()
        self._api_key_edit = QPlainTextEdit()
        self._api_key_edit.setFixedHeight(100)
        self._base_url_edit = QLineEdit()
        
        api_edit_inner_layout.addRow("配置名称:", self._api_name_edit)
        api_edit_inner_layout.addRow("API 密钥:", self._api_key_edit)
        api_edit_inner_layout.addRow("基础 URL:", self._base_url_edit)
        
        auto_save_label = QLabel("提示: 修改内容将自动保存")
        auto_save_label.setStyleSheet(
            f"color: {self.COLORS['light_text']}; font-style: italic;"
        )
        api_edit_inner_layout.addRow("", auto_save_label)
        
        api_edit_layout.addWidget(api_edit_group)
        
        api_splitter.addWidget(api_list_widget)
        api_splitter.addWidget(api_edit_widget)
        api_splitter.setSizes([300, 500])
        
        api_layout.addWidget(api_splitter)
        
        # 绑定事件
        self._add_api_btn.clicked.connect(self._add_api)
        self._remove_api_btn.clicked.connect(self._remove_api)
        self._select_api_btn.clicked.connect(self._select_api)
        self._api_list.currentItemChanged.connect(self._api_selected)
        self._api_name_edit.textChanged.connect(self._update_current_api)
        self._api_key_edit.textChanged.connect(self._update_current_api)
        self._base_url_edit.textChanged.connect(self._update_current_api)
        
        self._load_api_profiles()
        
        if self._api_list.count() > 0 and not self._api_list.currentItem():
            self._api_list.setCurrentRow(0)
        
        return api_tab
    
    def _load_api_profiles(self) -> None:
        """加载API配置到列表。"""
        self._api_list.clear()
        for profile in self._api_profiles:
            item = QListWidgetItem(profile["name"])
            if profile["name"] == self._selected_api:
                item.setForeground(QColor(self.COLORS["primary"]))
                item.setSelected(True)
            self._api_list.addItem(item)
    
    def _api_selected(
        self,
        current: Optional[QListWidgetItem],
        previous: Optional[QListWidgetItem],
    ) -> None:
        """当选择API列表中的项目时更新编辑区。"""
        if not current:
            self._api_name_edit.clear()
            self._api_key_edit.clear()
            self._base_url_edit.clear()
            return
        
        name = current.text()
        for profile in self._api_profiles:
            if profile["name"] == name:
                self._api_name_edit.blockSignals(True)
                self._api_key_edit.blockSignals(True)
                self._base_url_edit.blockSignals(True)
                
                self._api_name_edit.setText(profile["name"])
                self._api_key_edit.setPlainText(profile["api_key"])
                self._base_url_edit.setText(profile["base_url"])
                
                self._api_name_edit.blockSignals(False)
                self._api_key_edit.blockSignals(False)
                self._base_url_edit.blockSignals(False)
                break
    
    def _update_current_api(self) -> None:
        """实时更新当前编辑的API配置。"""
        current_item = self._api_list.currentItem()
        if not current_item:
            return
        
        old_name = current_item.text()
        new_name = self._api_name_edit.text().strip()
        api_key = self._api_key_edit.toPlainText().strip()
        base_url = self._base_url_edit.text().strip()
        
        if not new_name:
            return
        
        # 检查重名
        if old_name != new_name:
            for i in range(self._api_list.count()):
                if i != self._api_list.currentRow() and self._api_list.item(i).text() == new_name:
                    self._api_name_edit.blockSignals(True)
                    self._api_name_edit.setText(old_name)
                    self._api_name_edit.blockSignals(False)
                    self._update_status(f"API名称 '{new_name}' 已存在")
                    return
        
        # 更新配置
        for profile in self._api_profiles:
            if profile["name"] == old_name:
                profile["name"] = new_name
                profile["api_key"] = api_key
                profile["base_url"] = base_url
                
                if old_name == self._selected_api:
                    self._selected_api = new_name
                
                current_item.setText(new_name)
                self._update_status("API配置已更新")
                self._save_config()
                break
    
    def _add_api(self) -> None:
        """添加新的API配置。"""
        name, ok = QInputDialog.getText(
            self, "添加API配置", "请输入API配置名称:",
            flags=Qt.WindowCloseButtonHint | Qt.WindowTitleHint
        )
        
        if ok and name.strip():
            if any(profile["name"] == name for profile in self._api_profiles):
                self._update_status(f"API名称 '{name}' 已存在")
                return
            
            new_profile = {
                "name": name,
                "api_key": "",
                "base_url": "https://api.openai.com/v1/"
            }
            self._api_profiles.append(new_profile)
            
            self._api_list.blockSignals(True)
            item = QListWidgetItem(name)
            self._api_list.addItem(item)
            self._api_list.setCurrentItem(item)
            self._api_list.blockSignals(False)
            
            self._api_name_edit.setText(name)
            self._api_key_edit.clear()
            self._base_url_edit.setText("https://api.openai.com/v1/")
            
            self._update_status(f"已添加新API配置: {name}")
            self._save_config()
    
    def _remove_api(self) -> None:
        """删除选中的API配置。"""
        current_item = self._api_list.currentItem()
        if not current_item:
            self._update_status("请先选择一个API配置")
            return
        
        name = current_item.text()
        if len(self._api_profiles) <= 1:
            self._update_status("至少需要保留一个API配置")
            return
        
        self._api_profiles = [p for p in self._api_profiles if p["name"] != name]
        self._api_list.takeItem(self._api_list.row(current_item))
        
        if name == self._selected_api and self._api_profiles:
            self._selected_api = self._api_profiles[0]["name"]
        
        if self._api_list.count() > 0:
            self._api_list.setCurrentRow(0)
        
        self._update_status(f"已删除API配置: {name}")
        self._save_config()
    
    def _select_api(self) -> None:
        """选择当前API配置为默认。"""
        current_item = self._api_list.currentItem()
        if not current_item:
            self._update_status("请先选择一个API配置")
            return
        
        name = current_item.text()
        self._selected_api = name
        
        for i in range(self._api_list.count()):
            list_item = self._api_list.item(i)
            if list_item.text() == name:
                list_item.setForeground(QColor(self.COLORS["primary"]))
            else:
                list_item.setForeground(QColor(self.COLORS["text"]))
        
        self._update_status(f"已将 {name} 设为默认API")
        self._save_config()
    
    # ==================== Model Tab ====================
    def _create_model_tab(self) -> QWidget:
        """创建模型设置标签页。"""
        model_tab = QWidget()
        model_layout = QVBoxLayout(model_tab)
        model_layout.setContentsMargins(10, 15, 10, 10)
        
        model_header = QHBoxLayout()
        current_model_label = QLabel("当前选中模型:")
        self._current_model_value = QLabel(self._selected_model)
        self._current_model_value.setStyleSheet(
            f"font-weight: bold; color: {self.COLORS['primary']};"
        )
        
        model_header.addWidget(current_model_label)
        model_header.addWidget(self._current_model_value)
        model_header.addStretch()
        model_layout.addLayout(model_header)
        
        model_group = QGroupBox("可用模型")
        model_list_layout = QVBoxLayout(model_group)
        
        self._model_list = QListWidget()
        self._model_list.setAlternatingRowColors(True)
        self._model_list.setSelectionMode(QAbstractItemView.SingleSelection)
        model_list_layout.addWidget(self._model_list)
        
        model_btn_layout = QHBoxLayout()
        self._add_model_btn = QPushButton("添加模型")
        self._remove_model_btn = QPushButton("删除模型")
        self._select_model_btn = QPushButton("设为默认")
        model_btn_layout.addWidget(self._add_model_btn)
        model_btn_layout.addWidget(self._remove_model_btn)
        model_btn_layout.addWidget(self._select_model_btn)
        model_list_layout.addLayout(model_btn_layout)
        
        model_layout.addWidget(model_group)
        
        self._add_model_btn.clicked.connect(self._add_model)
        self._remove_model_btn.clicked.connect(self._remove_model)
        self._select_model_btn.clicked.connect(self._select_model)
        
        self._load_models()
        
        return model_tab
    
    def _load_models(self) -> None:
        """加载模型到列表。"""
        self._model_list.clear()
        for model in self._models:
            item = QListWidgetItem(model)
            if model == self._selected_model:
                item.setForeground(QColor(self.COLORS["primary"]))
                item.setSelected(True)
            self._model_list.addItem(item)
    
    def _add_model(self) -> None:
        """添加新模型。"""
        model_name, ok = QInputDialog.getText(
            self, "添加模型", "请输入模型名称:",
            flags=Qt.WindowCloseButtonHint | Qt.WindowTitleHint
        )
        
        if ok and model_name.strip():
            if model_name in self._models:
                self._update_status(f"模型名称 '{model_name}' 已存在")
                return
            
            self._models.append(model_name)
            item = QListWidgetItem(model_name)
            self._model_list.addItem(item)
            
            self._update_status(f"已添加新模型: {model_name}")
            self._save_config()
    
    def _remove_model(self) -> None:
        """删除选中的模型。"""
        current_item = self._model_list.currentItem()
        if not current_item:
            self._update_status("请先选择一个模型")
            return
        
        model_name = current_item.text()
        if len(self._models) <= 1:
            self._update_status("至少需要保留一个模型")
            return
        
        self._models.remove(model_name)
        self._model_list.takeItem(self._model_list.row(current_item))
        
        if model_name == self._selected_model and self._models:
            self._selected_model = self._models[0]
            self._current_model_value.setText(self._selected_model)
        
        if self._model_list.count() > 0:
            self._model_list.setCurrentRow(0)
        
        self._update_status(f"已删除模型: {model_name}")
        self._save_config()
    
    def _select_model(self) -> None:
        """选择当前模型为默认。"""
        current_item = self._model_list.currentItem()
        if not current_item:
            self._update_status("请先选择一个模型")
            return
        
        model_name = current_item.text()
        self._selected_model = model_name
        self._current_model_value.setText(model_name)
        
        for i in range(self._model_list.count()):
            list_item = self._model_list.item(i)
            if list_item.text() == model_name:
                list_item.setForeground(QColor(self.COLORS["primary"]))
            else:
                list_item.setForeground(QColor(self.COLORS["text"]))
        
        self._update_status(f"已将 {model_name} 设为默认模型")
        self._save_config()
    
    # ==================== Skill Tab ====================
    def _create_skill_tab(self) -> QWidget:
        """创建提示词管理标签页。"""
        skill_tab = QWidget()
        skill_layout = QVBoxLayout(skill_tab)
        skill_layout.setContentsMargins(10, 15, 10, 10)
        
        skill_header = QHBoxLayout()
        current_skill_label = QLabel("当前选中提示词:")
        self._current_skill_value = QLabel(self._selected_skill_name)
        self._current_skill_value.setStyleSheet(
            f"font-weight: bold; color: {self.COLORS['primary']};"
        )
        
        skill_header.addWidget(current_skill_label)
        skill_header.addWidget(self._current_skill_value)
        skill_header.addStretch()
        skill_layout.addLayout(skill_header)
        
        self._skill_table = QTableWidget()
        self._skill_table.setColumnCount(2)
        self._skill_table.setHorizontalHeaderLabels(["提示词名称", "提示词模板"])
        self._skill_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeToContents)
        self._skill_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        self._skill_table.verticalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
        self._skill_table.setWordWrap(True)
        self._skill_table.setAlternatingRowColors(True)
        self._skill_table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self._skill_table.setSelectionMode(QAbstractItemView.SingleSelection)
        self._skill_table.setItemDelegateForColumn(1, MultiLineDelegate(self._skill_table))
        
        skill_layout.addWidget(self._skill_table)
        
        tip_label = QLabel(
            "提示: 双击单元格可编辑内容。提示词中可使用占位符：\n"
            "{text}=选中的文本、{source_language}=当前语言、{source_language_en}=当前语言(英文)、\n"
            "{target_language}=目标语言、{target_language_en}=目标语言(英文)"
        )
        tip_label.setWordWrap(True)
        tip_label.setStyleSheet(
            f"color: {self.COLORS['light_text']}; font-style: italic;"
        )
        skill_layout.addWidget(tip_label)
        
        skill_btn_layout = QHBoxLayout()
        self._add_skill_btn = QPushButton("添加提示词")
        self._remove_skill_btn = QPushButton("删除提示词")
        self._select_skill_btn = QPushButton("设为默认")
        
        skill_btn_layout.addWidget(self._add_skill_btn)
        skill_btn_layout.addWidget(self._remove_skill_btn)
        skill_btn_layout.addWidget(self._select_skill_btn)
        skill_layout.addLayout(skill_btn_layout)
        
        self._add_skill_btn.clicked.connect(self._add_skill)
        self._remove_skill_btn.clicked.connect(self._remove_skill)
        self._select_skill_btn.clicked.connect(self._select_skill)
        self._skill_table.itemChanged.connect(self._on_skill_item_changed)
        self._skill_table.setEditTriggers(
            QTableWidget.DoubleClicked | QTableWidget.EditKeyPressed
        )
        
        self._load_skills()
        
        return skill_tab
    
    def _load_skills(self) -> None:
        """加载提示词到表格。"""
        self._skill_table.blockSignals(True)
        self._skill_table.setRowCount(len(self._skills))
        
        for row, skill in enumerate(self._skills):
            name_item = QTableWidgetItem(skill["name"])
            prompt_item = QTableWidgetItem(skill["prompt"])
            
            name_item.setTextAlignment(Qt.AlignLeft | Qt.AlignVCenter)
            prompt_item.setTextAlignment(Qt.AlignLeft | Qt.AlignVCenter)
            
            if skill["name"] == self._selected_skill_name:
                name_item.setForeground(QColor(self.COLORS["primary"]))
            
            self._skill_table.setItem(row, 0, name_item)
            self._skill_table.setItem(row, 1, prompt_item)
        
        self._skill_table.blockSignals(False)
        
        for row in range(self._skill_table.rowCount()):
            if self._skill_table.item(row, 0).text() == self._selected_skill_name:
                self._skill_table.selectRow(row)
                break
    
    def _add_skill(self) -> None:
        """添加新提示词。"""
        dialog = QDialog(self)
        dialog.setWindowTitle("添加提示词")
        dialog.resize(600, 400)
        dialog.setStyleSheet(self.styleSheet())
        
        layout = QVBoxLayout(dialog)
        
        name_label = QLabel("提示词名称:")
        name_edit = QLineEdit()
        layout.addWidget(name_label)
        layout.addWidget(name_edit)
        
        prompt_label = QLabel("提示词模板:")
        prompt_edit = QPlainTextEdit()
        layout.addWidget(prompt_label)
        layout.addWidget(prompt_edit)
        
        tip = QLabel(
            "提示: 提示词模板中可使用占位符：{text}=选中的文本、{source_language}=当前语言、\n"
            "{source_language_en}=当前语言(英文)、{target_language}=目标语言、{target_language_en}=目标语言(英文)"
        )
        tip.setStyleSheet(f"color: {self.COLORS['light_text']}; font-style: italic;")
        tip.setWordWrap(True)
        layout.addWidget(tip)
        
        btn_layout = QHBoxLayout()
        ok_btn = QPushButton("确定")
        cancel_btn = QPushButton("取消")
        btn_layout.addStretch()
        btn_layout.addWidget(ok_btn)
        btn_layout.addWidget(cancel_btn)
        layout.addLayout(btn_layout)
        
        ok_btn.clicked.connect(dialog.accept)
        cancel_btn.clicked.connect(dialog.reject)
        
        if dialog.exec_() == QDialog.Accepted:
            name = name_edit.text().strip()
            prompt = prompt_edit.toPlainText().strip()
            
            if not name or not prompt:
                self._update_status("提示词名称和内容不能为空")
                return
            
            if any(skill["name"] == name for skill in self._skills):
                self._update_status(f"提示词名称 '{name}' 已存在")
                return
            
            new_skill = {"name": name, "prompt": prompt}
            self._skills.append(new_skill)
            
            row = self._skill_table.rowCount()
            self._skill_table.insertRow(row)
            
            name_item = QTableWidgetItem(name)
            prompt_item = QTableWidgetItem(prompt)
            
            name_item.setTextAlignment(Qt.AlignLeft | Qt.AlignVCenter)
            prompt_item.setTextAlignment(Qt.AlignLeft | Qt.AlignVCenter)
            
            self._skill_table.setItem(row, 0, name_item)
            self._skill_table.setItem(row, 1, prompt_item)
            self._skill_table.selectRow(row)
            
            self._update_status(f"已添加新提示词: {name}")
            self._save_config()
    
    def _remove_skill(self) -> None:
        """删除选中的提示词。"""
        row = self._skill_table.currentRow()
        if row < 0:
            self._update_status("请先选择一个提示词")
            return
        
        if len(self._skills) <= 1:
            self._update_status("至少需要保留一个提示词")
            return
        
        skill_name = self._skill_table.item(row, 0).text()
        self._skills.pop(row)
        self._skill_table.removeRow(row)
        
        if skill_name == self._selected_skill_name and self._skills:
            self._selected_skill_name = self._skills[0]["name"]
            self._current_skill_value.setText(self._selected_skill_name)
            self.skill_selected.emit(self._skills[0])
        
        if self._skill_table.rowCount() > 0:
            self._skill_table.selectRow(0)
        
        self._update_status(f"已删除提示词: {skill_name}")
        self._save_config()
    
    def _select_skill(self) -> None:
        """将当前选中的提示词设为默认。"""
        row = self._skill_table.currentRow()
        if row < 0:
            self._update_status("请先选择一个提示词")
            return
        
        chosen_skill = self._skills[row]
        self._selected_skill_name = chosen_skill["name"]
        self._current_skill_value.setText(self._selected_skill_name)
        
        for r in range(self._skill_table.rowCount()):
            name_item = self._skill_table.item(r, 0)
            if r == row:
                name_item.setForeground(QColor(self.COLORS["primary"]))
            else:
                name_item.setForeground(QColor(self.COLORS["text"]))
        
        self.skill_selected.emit(chosen_skill)
        self._update_status(f"已将 {chosen_skill['name']} 设为默认提示词")
        self._save_config()
    
    def _on_skill_item_changed(self, item: QTableWidgetItem) -> None:
        """提示词表格内容变化处理。"""
        row = item.row()
        column = item.column()
        new_value = item.text()
        
        if column == 0:  # 提示词名称
            for r in range(self._skill_table.rowCount()):
                if r != row and self._skill_table.item(r, 0).text() == new_value:
                    old_value = self._skills[row]["name"]
                    self._skill_table.blockSignals(True)
                    item.setText(old_value)
                    self._skill_table.blockSignals(False)
                    self._update_status(f"提示词名称 '{new_value}' 已存在")
                    return
            
            if not new_value.strip():
                old_value = self._skills[row]["name"]
                self._skill_table.blockSignals(True)
                item.setText(old_value)
                self._skill_table.blockSignals(False)
                self._update_status("提示词名称不能为空")
                return
            
            old_name = self._skills[row]["name"]
            self._skills[row]["name"] = new_value
            
            if self._selected_skill_name == old_name:
                self._selected_skill_name = new_value
                self._current_skill_value.setText(new_value)
                
        elif column == 1:  # 提示词
            if not new_value.strip():
                old_value = self._skills[row]["prompt"]
                self._skill_table.blockSignals(True)
                item.setText(old_value)
                self._skill_table.blockSignals(False)
                self._update_status("提示词不能为空")
                return
            
            self._skills[row]["prompt"] = new_value
        
        self._update_status("提示词已更新")
        self._save_config()
    
    # ==================== Translation Tab ====================
    def _create_translation_tab(self) -> QWidget:
        """创建翻译设置标签页。"""
        translation_tab = QWidget()
        translation_layout = QVBoxLayout(translation_tab)
        translation_layout.setContentsMargins(10, 15, 10, 10)
        
        # 目标语言设置组
        language_group = QGroupBox("目标语言")
        language_form = QFormLayout(language_group)
        
        info_label = QLabel(
            "源语言会自动检测，当与目标语言一致时自动翻译为中文或英文"
        )
        info_label.setWordWrap(True)
        info_label.setStyleSheet(
            f"color: {self.COLORS['light_text']}; font-style: italic; margin-bottom: 5px;"
        )
        language_form.addRow(info_label)
        
        target_lang_label = QLabel("目标语言:")
        self._target_language_combo = QComboBox()
        self._target_language_combo.addItems([
            "English", "Chinese", "中文", "Japanese", "日本語", 
            "Korean", "한국어", "French", "Français", 
            "German", "Deutsch", "Spanish", "Español", 
            "Russian", "Русский"
        ])
        
        index = self._target_language_combo.findText(self._target_language)
        if index >= 0:
            self._target_language_combo.setCurrentIndex(index)
        
        language_form.addRow(target_lang_label, self._target_language_combo)
        self._target_language_combo.currentTextChanged.connect(self._on_target_language_changed)
        
        translation_layout.addWidget(language_group)
        
        # 热键设置组
        hotkey_group = QGroupBox("热键设置")
        hotkey_layout = QVBoxLayout(hotkey_group)
        
        hotkey_info = QLabel("双击对应按键触发功能，翻译热键获取选中文本并翻译，附加热键将选中文本添加到原文区")
        hotkey_info.setWordWrap(True)
        hotkey_info.setStyleSheet(
            f"color: {self.COLORS['light_text']}; font-style: italic; margin-bottom: 10px;"
        )
        hotkey_layout.addWidget(hotkey_info)
        
        # 翻译热键
        translate_layout = QHBoxLayout()
        self._translate_enabled_cb = QCheckBox("启用翻译热键")
        self._translate_enabled_cb.setChecked(self._translate_hotkey.get("enabled", True))
        translate_layout.addWidget(self._translate_enabled_cb)
        
        translate_layout.addWidget(QLabel("双击"))
        self._translate_key_combo = QComboBox()
        self._translate_key_combo.addItems(["Ctrl", "Shift", "Alt"])
        current_translate_key = self._translate_hotkey.get("key", "ctrl").capitalize()
        idx = self._translate_key_combo.findText(current_translate_key)
        if idx >= 0:
            self._translate_key_combo.setCurrentIndex(idx)
        translate_layout.addWidget(self._translate_key_combo)
        translate_layout.addWidget(QLabel("执行翻译"))
        translate_layout.addStretch()
        hotkey_layout.addLayout(translate_layout)
        
        # 附加热键
        append_layout = QHBoxLayout()
        self._append_enabled_cb = QCheckBox("启用附加热键")
        self._append_enabled_cb.setChecked(self._append_hotkey.get("enabled", True))
        append_layout.addWidget(self._append_enabled_cb)
        
        append_layout.addWidget(QLabel("双击"))
        self._append_key_combo = QComboBox()
        self._append_key_combo.addItems(["Ctrl", "Shift", "Alt"])
        current_append_key = self._append_hotkey.get("key", "shift").capitalize()
        idx = self._append_key_combo.findText(current_append_key)
        if idx >= 0:
            self._append_key_combo.setCurrentIndex(idx)
        append_layout.addWidget(self._append_key_combo)
        append_layout.addWidget(QLabel("添加到原文区"))
        append_layout.addStretch()
        hotkey_layout.addLayout(append_layout)
        
        # 热键冲突提示
        self._hotkey_warning = QLabel("")
        self._hotkey_warning.setStyleSheet("color: #e74c3c; font-weight: bold;")
        self._hotkey_warning.setVisible(False)
        hotkey_layout.addWidget(self._hotkey_warning)
        
        # 绑定热键变更事件
        self._translate_enabled_cb.stateChanged.connect(self._on_hotkey_changed)
        self._translate_key_combo.currentTextChanged.connect(self._on_hotkey_changed)
        self._append_enabled_cb.stateChanged.connect(self._on_hotkey_changed)
        self._append_key_combo.currentTextChanged.connect(self._on_hotkey_changed)
        
        translation_layout.addWidget(hotkey_group)
        translation_layout.addStretch()
        
        return translation_tab
    
    def _on_target_language_changed(self, new_language: str) -> None:
        """目标语言改变时的处理。"""
        self._target_language = new_language
        self._update_status(f"目标语言已设置为: {new_language}")
        self._save_config()
    
    def _on_hotkey_changed(self) -> None:
        """热键配置变更处理。"""
        translate_key = self._translate_key_combo.currentText().lower()
        translate_enabled = self._translate_enabled_cb.isChecked()
        append_key = self._append_key_combo.currentText().lower()
        append_enabled = self._append_enabled_cb.isChecked()
        
        # 检查热键冲突
        if translate_enabled and append_enabled and translate_key == append_key:
            self._hotkey_warning.setText("⚠ 警告：翻译热键和附加热键相同，可能导致冲突")
            self._hotkey_warning.setVisible(True)
        else:
            self._hotkey_warning.setVisible(False)
        
        # 更新配置
        self._translate_hotkey = {"key": translate_key, "enabled": translate_enabled}
        self._append_hotkey = {"key": append_key, "enabled": append_enabled}
        
        # 发送热键变更信号
        self.hotkey_changed.emit("translate", translate_key, translate_enabled)
        self.hotkey_changed.emit("append", append_key, append_enabled)
        
        self._update_status(f"热键配置已更新")
        self._save_config()
    
    # ==================== Public Methods ====================
    def get_api_profiles(self) -> List[Dict]:
        return self._api_profiles
    
    def get_selected_api(self) -> str:
        return self._selected_api
    
    def get_models(self) -> List[str]:
        return self._models
    
    def get_selected_model(self) -> str:
        return self._selected_model
    
    def get_skills(self) -> List[Dict]:
        return self._skills
    
    def get_selected_skill_name(self) -> str:
        return self._selected_skill_name

