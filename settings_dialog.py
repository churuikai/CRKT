# settings_dialog.py
from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton,
    QListWidget, QWidget, QTabWidget, QGroupBox, QFormLayout, QInputDialog,
    QMessageBox, QListWidgetItem, QSplitter, QTableWidget,
    QTableWidgetItem, QHeaderView, QPlainTextEdit, QStyledItemDelegate, 
    QAbstractItemView, QComboBox
)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QColor, QTextOption

class MultiLineDelegate(QStyledItemDelegate):
    """多行文本编辑委托"""
    def createEditor(self, parent, option, index):
        editor = QPlainTextEdit(parent)
        editor.setWordWrapMode(QTextOption.WordWrap)
        return editor
    
    def setEditorData(self, editor, index):
        value = index.model().data(index, Qt.EditRole)
        if value is not None:
            editor.setPlainText(str(value))
    
    def setModelData(self, editor, model, index):
        model.setData(index, editor.toPlainText(), Qt.EditRole)

class SettingsDialog(QDialog):
    """综合设置对话框"""
    skill_selected = pyqtSignal(dict)  # 传递选中的提示词
    
    def __init__(self, 
                api_profiles=None, 
                selected_api="", 
                models=None, 
                selected_model="", 
                skills=None, 
                selected_skill_name="",
                target_language="English",
                parent=None,
                save_callback=None):
        super().__init__(parent)
        self.setWindowTitle("设置")
        self.resize(850, 600)
        
        # 初始化数据
        self.api_profiles = api_profiles if api_profiles else []
        self.selected_api = selected_api
        self.models = models if models else []
        self.selected_model = selected_model
        self.skills = skills if skills else []
        self.selected_skill_name = selected_skill_name
        self.target_language = target_language  # 目标语言配置
        self.save_callback = save_callback  # 保存配置的回调函数
        
        # 定义配色
        self.colors = {
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
        
        # 应用样式表
        self._apply_stylesheet()
        
        # 创建界面
        self._create_ui()
        
    def _apply_stylesheet(self):
        """应用样式表"""
        self.setStyleSheet(f"""
            QDialog {{
                background-color: {self.colors["white"]};
                font-family: "Segoe UI", Arial, sans-serif;
            }}
            QTabWidget::pane {{
                border: 1px solid {self.colors["border"]};
                border-radius: 6px;
                background-color: {self.colors["white"]};
                margin-top: -1px;
            }}
            QTabBar::tab {{
                background-color: {self.colors["light_bg"]};
                border: 1px solid {self.colors["border"]};
                border-bottom-color: none;
                border-top-left-radius: 4px;
                border-top-right-radius: 4px;
                min-width: 8ex;
                padding: 8px 16px;
                margin-right: 2px;
                color: {self.colors["text"]};
            }}
            QTabBar::tab:selected {{
                background-color: {self.colors["white"]};
                border-bottom-color: {self.colors["white"]};
                color: {self.colors["primary"]};
                font-weight: bold;
            }}
            QTabBar::tab:hover:!selected {{
                background-color: {self.colors["lighter_bg"]};
            }}
            QPushButton {{
                background-color: {self.colors["primary_light"]};
                color: white;
                border: none;
                padding: 8px 12px;
                border-radius: 4px;
                min-width: 80px;
            }}
            QPushButton:hover {{
                background-color: {self.colors["primary"]};
            }}
            QPushButton:disabled {{
                background-color: #cccccc;
                color: #666666;
            }}
            QLineEdit, QPlainTextEdit {{
                padding: 8px;
                border: 1px solid {self.colors["border"]};
                border-radius: 4px;
                background-color: {self.colors["white"]};
            }}
            QLineEdit:focus, QPlainTextEdit:focus {{
                border: 1px solid {self.colors["primary"]};
            }}
            QListWidget, QTableWidget {{
                border: 1px solid {self.colors["border"]};
                border-radius: 4px;
                background-color: {self.colors["white"]};
                alternate-background-color: {self.colors["light_bg"]};
                selection-background-color: {self.colors["selected_bg"]};
            }}
            QTableWidget::item {{
                padding: 4px;
            }}
            QTableWidget::item:selected {{
                background-color: {self.colors["selected_bg"]};
                color: {self.colors["primary"]};
            }}
            QHeaderView::section {{
                background-color: {self.colors["light_bg"]};
                padding: 8px;
                border: 1px solid {self.colors["border"]};
                color: {self.colors["text"]};
            }}
            QGroupBox {{
                border: 1px solid {self.colors["border"]};
                border-radius: 4px;
                margin-top: 16px;
                padding-top: 16px;
                color: {self.colors["primary"]};
                font-weight: bold;
            }}
            QSplitter::handle {{
                background-color: {self.colors["lighter_bg"]};
                width: 2px;
            }}
        """)
        
    def _create_ui(self):
        """创建UI界面"""
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(12, 12, 12, 12)
        main_layout.setSpacing(10)
        
        # 创建标签页
        self.tab_widget = QTabWidget()
        self.tab_widget.setDocumentMode(True)
        
        # 添加标签页
        self.tab_widget.addTab(self._create_api_tab(), "API 设置")
        self.tab_widget.addTab(self._create_model_tab(), "模型设置")
        self.tab_widget.addTab(self._create_skill_tab(), "提示词管理")
        self.tab_widget.addTab(self._create_language_tab(), "语言设置")
        
        main_layout.addWidget(self.tab_widget)
        
        # 底部状态栏
        self.status_label = QLabel("准备就绪")
        self.status_label.setStyleSheet(f"color: {self.colors['light_text']}; padding: 8px;")
        main_layout.addWidget(self.status_label)
        
    def update_status(self, message):
        """更新状态信息"""
        self.status_label.setText(message)
        
    def _create_api_tab(self):
        """创建API设置标签页"""
        api_tab = QWidget()
        api_layout = QVBoxLayout(api_tab)
        api_layout.setContentsMargins(10, 15, 10, 10)
        
        # API管理区域
        api_splitter = QSplitter(Qt.Horizontal)
        
        # 左侧API列表
        api_list_widget = QWidget()
        api_list_layout = QVBoxLayout(api_list_widget)
        api_list_layout.setContentsMargins(0, 0, 0, 0)
        
        api_list_group = QGroupBox("API 配置列表")
        api_list_inner_layout = QVBoxLayout(api_list_group)
        
        self.api_list = QListWidget()
        self.api_list.setAlternatingRowColors(True)
        self.api_list.setSelectionMode(QAbstractItemView.SingleSelection)
        api_list_inner_layout.addWidget(self.api_list)
        
        # API列表按钮
        api_btn_layout = QHBoxLayout()
        self.add_api_btn = QPushButton("添加")
        self.remove_api_btn = QPushButton("删除")
        self.select_api_btn = QPushButton("设为默认")
        api_btn_layout.addWidget(self.add_api_btn)
        api_btn_layout.addWidget(self.remove_api_btn)
        api_btn_layout.addWidget(self.select_api_btn)
        api_list_inner_layout.addLayout(api_btn_layout)
        
        api_list_layout.addWidget(api_list_group)
        
        # 右侧API编辑区域
        api_edit_widget = QWidget()
        api_edit_layout = QVBoxLayout(api_edit_widget)
        api_edit_layout.setContentsMargins(0, 0, 0, 0)
        
        api_edit_group = QGroupBox("API 配置详情")
        api_edit_inner_layout = QFormLayout(api_edit_group)
        api_edit_inner_layout.setFieldGrowthPolicy(QFormLayout.AllNonFixedFieldsGrow)
        
        self.api_name_edit = QLineEdit()
        self.api_key_edit = QPlainTextEdit()
        self.api_key_edit.setFixedHeight(100)
        self.base_url_edit = QLineEdit()
        
        api_edit_inner_layout.addRow("配置名称:", self.api_name_edit)
        api_edit_inner_layout.addRow("API 密钥:", self.api_key_edit)
        api_edit_inner_layout.addRow("基础 URL:", self.base_url_edit)
        
        # 添加自动保存提示
        auto_save_label = QLabel("提示: 修改内容将自动保存")
        auto_save_label.setStyleSheet(f"color: {self.colors['light_text']}; font-style: italic;")
        api_edit_inner_layout.addRow("", auto_save_label)
        
        api_edit_layout.addWidget(api_edit_group)
        
        # 将左右面板添加到分割器
        api_splitter.addWidget(api_list_widget)
        api_splitter.addWidget(api_edit_widget)
        api_splitter.setSizes([300, 500])
        
        api_layout.addWidget(api_splitter)
        
        # 绑定API相关事件
        self.add_api_btn.clicked.connect(self._add_api)
        self.remove_api_btn.clicked.connect(self._remove_api)
        self.select_api_btn.clicked.connect(self._select_api)
        self.api_list.currentItemChanged.connect(self._api_selected)
        
        # 实时保存输入变化
        self.api_name_edit.textChanged.connect(self._update_current_api)
        self.api_key_edit.textChanged.connect(self._update_current_api)
        self.base_url_edit.textChanged.connect(self._update_current_api)
        
        # 加载API列表
        self._load_api_profiles()
        
        # 确保有选择项
        if self.api_list.count() > 0 and not self.api_list.currentItem():
            self.api_list.setCurrentRow(0)
        
        return api_tab
    
    def _create_model_tab(self):
        """创建模型设置标签页"""
        model_tab = QWidget()
        model_layout = QVBoxLayout(model_tab)
        model_layout.setContentsMargins(10, 15, 10, 10)
        
        # 显示当前选中模型
        model_header = QHBoxLayout()
        current_model_label = QLabel("当前选中模型:")
        current_model_value = QLabel(self.selected_model)
        current_model_value.setStyleSheet(f"font-weight: bold; color: {self.colors['primary']};")
        
        model_header.addWidget(current_model_label)
        model_header.addWidget(current_model_value)
        model_header.addStretch()
        model_layout.addLayout(model_header)
        
        # 模型列表组
        model_group = QGroupBox("可用模型")
        model_list_layout = QVBoxLayout(model_group)
        
        self.model_list = QListWidget()
        self.model_list.setAlternatingRowColors(True)
        self.model_list.setSelectionMode(QAbstractItemView.SingleSelection)
        model_list_layout.addWidget(self.model_list)
        
        # 模型按钮组
        model_btn_layout = QHBoxLayout()
        self.add_model_btn = QPushButton("添加模型")
        self.remove_model_btn = QPushButton("删除模型")
        self.select_model_btn = QPushButton("设为默认")
        model_btn_layout.addWidget(self.add_model_btn)
        model_btn_layout.addWidget(self.remove_model_btn)
        model_btn_layout.addWidget(self.select_model_btn)
        model_list_layout.addLayout(model_btn_layout)
        
        model_layout.addWidget(model_group)
        
        # 绑定模型相关事件
        self.add_model_btn.clicked.connect(self._add_model)
        self.remove_model_btn.clicked.connect(self._remove_model)
        self.select_model_btn.clicked.connect(self._select_model)
        
        # 加载模型列表
        self._load_models()
        
        return model_tab
    
    def _create_skill_tab(self):
        """创建提示词管理标签页"""
        skill_tab = QWidget()
        skill_layout = QVBoxLayout(skill_tab)
        skill_layout.setContentsMargins(10, 15, 10, 10)
        
        # 显示当前选中提示词
        skill_header = QHBoxLayout()
        current_skill_label = QLabel("当前选中提示词:")
        current_skill_value = QLabel(self.selected_skill_name)
        current_skill_value.setStyleSheet(f"font-weight: bold; color: {self.colors['primary']};")
        
        skill_header.addWidget(current_skill_label)
        skill_header.addWidget(current_skill_value)
        skill_header.addStretch()
        skill_layout.addLayout(skill_header)
        
        # 提示词表格
        self.skill_table = QTableWidget()
        self.skill_table.setColumnCount(2)
        self.skill_table.setHorizontalHeaderLabels(["提示词名称", "提示词模板"])
        self.skill_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeToContents)
        self.skill_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        self.skill_table.verticalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
        self.skill_table.setWordWrap(True)
        self.skill_table.setAlternatingRowColors(True)
        self.skill_table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.skill_table.setSelectionMode(QAbstractItemView.SingleSelection)
        
        # 为提示词列设置多行文本委托
        self.skill_table.setItemDelegateForColumn(1, MultiLineDelegate(self.skill_table))
        
        skill_layout.addWidget(self.skill_table)
        
        # 提示标签
        tip_label = QLabel("提示: 双击单元格可编辑内容。提示词中可使用占位符：\n"
                         "{selected_text}=选中的文本、{source_language}=当前语言、{source_language_en}=当前语言(英文)、\n"
                         "{target_language}=目标语言、{target_language_en}=目标语言(英文)")
        tip_label.setWordWrap(True)
        tip_label.setStyleSheet(f"color: {self.colors['light_text']}; font-style: italic;")
        skill_layout.addWidget(tip_label)
        
        # 按钮组
        skill_btn_layout = QHBoxLayout()
        self.add_skill_btn = QPushButton("添加提示词")
        self.remove_skill_btn = QPushButton("删除提示词")
        self.select_skill_btn = QPushButton("设为默认")
        
        skill_btn_layout.addWidget(self.add_skill_btn)
        skill_btn_layout.addWidget(self.remove_skill_btn)
        skill_btn_layout.addWidget(self.select_skill_btn)
        skill_layout.addLayout(skill_btn_layout)
        
        # 绑定提示词相关事件
        self.add_skill_btn.clicked.connect(self._add_skill)
        self.remove_skill_btn.clicked.connect(self._remove_skill)
        self.select_skill_btn.clicked.connect(self._select_skill)
        self.skill_table.itemChanged.connect(self._on_skill_item_changed)
        self.skill_table.setEditTriggers(QTableWidget.DoubleClicked | QTableWidget.EditKeyPressed)
        
        # 加载提示词列表
        self._load_skills()
        
        return skill_tab
    
    def _create_language_tab(self):
        """创建语言设置标签页"""
        language_tab = QWidget()
        language_layout = QVBoxLayout(language_tab)
        language_layout.setContentsMargins(10, 15, 10, 10)
        
        # 语言设置组
        language_group = QGroupBox("目标语言设置")
        language_form = QFormLayout(language_group)
        
        # 说明标签
        info_label = QLabel("源语言会自动检测\n"
                           "目标语言可配置，当与源语言一致时翻译为中文或英文")
        info_label.setWordWrap(True)
        info_label.setStyleSheet(f"color: {self.colors['light_text']}; font-style: italic; margin-bottom: 10px;")
        language_form.addRow(info_label)
        
        # 目标语言选择
        target_lang_label = QLabel("目标语言:")
        self.target_language_combo = QComboBox()
        self.target_language_combo.addItems([
            "English", "中文", "日本語", "한국어", 
            "Français", "Deutsch", "Español", "Русский"
        ])
        
        # 设置当前选中的目标语言
        index = self.target_language_combo.findText(self.target_language)
        if index >= 0:
            self.target_language_combo.setCurrentIndex(index)
        
        language_form.addRow(target_lang_label, self.target_language_combo)
        
        # 绑定变化事件
        self.target_language_combo.currentTextChanged.connect(self._on_target_language_changed)
        
        language_layout.addWidget(language_group)
        language_layout.addStretch()
        
        return language_tab
    
    def _on_target_language_changed(self, new_language):
        """目标语言改变时的处理"""
        self.target_language = new_language
        self.update_status(f"目标语言已设置为: {new_language}")
        self._save_config()
    
    # API相关方法
    def _load_api_profiles(self):
        """加载API配置到列表"""
        self.api_list.clear()
        for profile in self.api_profiles:
            item = QListWidgetItem(profile["name"])
            if profile["name"] == self.selected_api:
                item.setForeground(QColor(self.colors["primary"]))
                item.setSelected(True)
            self.api_list.addItem(item)
            
    def _api_selected(self, current, previous):
        """当选择API列表中的项目时，更新编辑区"""
        if not current:
            self.api_name_edit.clear()
            self.api_key_edit.clear()
            self.base_url_edit.clear()
            return
            
        name = current.text()
        for profile in self.api_profiles:
            if profile["name"] == name:
                # 更新字段但阻止触发更新事件
                self.api_name_edit.blockSignals(True)
                self.api_key_edit.blockSignals(True)
                self.base_url_edit.blockSignals(True)
                
                self.api_name_edit.setText(profile["name"])
                self.api_key_edit.setPlainText(profile["api_key"])
                self.base_url_edit.setText(profile["base_url"])
                
                self.api_name_edit.blockSignals(False)
                self.api_key_edit.blockSignals(False)
                self.base_url_edit.blockSignals(False)
                break
    
    def _update_current_api(self):
        """实时更新当前编辑的API配置"""
        current_item = self.api_list.currentItem()
        if not current_item:
            return
            
        old_name = current_item.text()
        new_name = self.api_name_edit.text().strip()
        api_key = self.api_key_edit.toPlainText().strip()
        base_url = self.base_url_edit.text().strip()
        
        # 名称不能为空
        if not new_name:
            return
            
        # 如果名称变了，检查重名
        if old_name != new_name:
            # 检查是否有重名冲突
            for i in range(self.api_list.count()):
                if i != self.api_list.currentRow() and self.api_list.item(i).text() == new_name:
                    # 恢复原名称并提示用户
                    self.api_name_edit.blockSignals(True)
                    self.api_name_edit.setText(old_name)
                    self.api_name_edit.blockSignals(False)
                    self.update_status(f"API名称 '{new_name}' 已存在")
                    return
        
        # 更新配置
        for profile in self.api_profiles:
            if profile["name"] == old_name:
                profile["name"] = new_name
                profile["api_key"] = api_key
                profile["base_url"] = base_url
                
                # 如果修改的是当前选中的API配置，更新selected_api
                if old_name == self.selected_api:
                    self.selected_api = new_name
                
                # 更新列表项
                current_item.setText(new_name)
                self.update_status("API配置已更新")
                
                # 保存配置
                self._save_config()
                break
    
    def _add_api(self):
        """添加新的API配置"""
        name, ok = QInputDialog.getText(
            self, "添加API配置", "请输入API配置名称:",
            flags=Qt.WindowCloseButtonHint | Qt.WindowTitleHint
        )
        
        if ok and name.strip():
            # 检查重名
            if any(profile["name"] == name for profile in self.api_profiles):
                self.update_status(f"API名称 '{name}' 已存在")
                return
                
            # 添加新配置
            new_profile = {
                "name": name,
                "api_key": "",
                "base_url": "https://api.openai.com/v1/"
            }
            self.api_profiles.append(new_profile)
            
            # 更新列表
            self.api_list.blockSignals(True)
            item = QListWidgetItem(name)
            self.api_list.addItem(item)
            self.api_list.setCurrentItem(item)
            self.api_list.blockSignals(False)
            
            # 清空编辑区，准备编辑新配置
            self.api_name_edit.setText(name)
            self.api_key_edit.clear()
            self.base_url_edit.setText("https://api.openai.com/v1/")
            
            self.update_status(f"已添加新API配置: {name}")
            
            # 保存配置
            self._save_config()
    
    def _remove_api(self):
        """删除选中的API配置"""
        current_item = self.api_list.currentItem()
        if not current_item:
            self.update_status("请先选择一个API配置")
            return
            
        name = current_item.text()
        if len(self.api_profiles) <= 1:
            self.update_status("至少需要保留一个API配置")
            return
            
        # 删除配置
        self.api_profiles = [p for p in self.api_profiles if p["name"] != name]
        self.api_list.takeItem(self.api_list.row(current_item))
        
        # 如果删除的是当前选中的API，则更新选中的API
        if name == self.selected_api and self.api_profiles:
            self.selected_api = self.api_profiles[0]["name"]
            
        # 如果还有项目，选择第一项
        if self.api_list.count() > 0:
            self.api_list.setCurrentRow(0)
        
        self.update_status(f"已删除API配置: {name}")
        
        # 保存配置
        self._save_config()
            
    def _select_api(self):
        """选择当前API配置为默认"""
        current_item = self.api_list.currentItem()
        if not current_item:
            self.update_status("请先选择一个API配置")
            return
            
        name = current_item.text()
        self.selected_api = name
        
        # 更新所有项的颜色
        for i in range(self.api_list.count()):
            list_item = self.api_list.item(i)
            if list_item.text() == name:
                list_item.setForeground(QColor(self.colors["primary"]))
            else:
                list_item.setForeground(QColor(self.colors["text"]))
                
        self.update_status(f"已将 {name} 设为默认API")
        
        # 保存配置
        self._save_config()
    
    # 模型相关方法
    def _load_models(self):
        """加载模型到列表"""
        self.model_list.clear()
        for model in self.models:
            item = QListWidgetItem(model)
            if model == self.selected_model:
                item.setForeground(QColor(self.colors["primary"]))
                item.setSelected(True)
            self.model_list.addItem(item)
    
    def _add_model(self):
        """添加新模型"""
        model_name, ok = QInputDialog.getText(
            self, "添加模型", "请输入模型名称:",
            flags=Qt.WindowCloseButtonHint | Qt.WindowTitleHint
        )
        
        if ok and model_name.strip():
            # 检查重名
            if model_name in self.models:
                self.update_status(f"模型名称 '{model_name}' 已存在")
                return
                
            # 添加模型
            self.models.append(model_name)
            
            # 更新列表
            item = QListWidgetItem(model_name)
            self.model_list.addItem(item)
            
            self.update_status(f"已添加新模型: {model_name}")
            
            # 保存配置
            self._save_config()
    
    def _remove_model(self):
        """删除选中的模型"""
        current_item = self.model_list.currentItem()
        if not current_item:
            self.update_status("请先选择一个模型")
            return
            
        model_name = current_item.text()
        if len(self.models) <= 1:
            self.update_status("至少需要保留一个模型")
            return
            
        # 删除模型
        self.models.remove(model_name)
        self.model_list.takeItem(self.model_list.row(current_item))
        
        # 如果删除的是当前选中的模型，则更新选中的模型
        if model_name == self.selected_model and self.models:
            self.selected_model = self.models[0]
            
        # 更新选择
        if self.model_list.count() > 0:
            self.model_list.setCurrentRow(0)
            
        self.update_status(f"已删除模型: {model_name}")
        
        # 保存配置
        self._save_config()
    
    def _select_model(self):
        """选择当前模型为默认"""
        current_item = self.model_list.currentItem()
        if not current_item:
            self.update_status("请先选择一个模型")
            return
            
        model_name = current_item.text()
        self.selected_model = model_name
        
        # 更新所有项的颜色
        for i in range(self.model_list.count()):
            list_item = self.model_list.item(i)
            if list_item.text() == model_name:
                list_item.setForeground(QColor(self.colors["primary"]))
            else:
                list_item.setForeground(QColor(self.colors["text"]))
                
        self.update_status(f"已将 {model_name} 设为默认模型")
        
        # 保存配置
        self._save_config()
    
    # 提示词相关方法
    def _load_skills(self):
        """加载提示词到表格"""
        self.skill_table.blockSignals(True)
        self.skill_table.setRowCount(len(self.skills))
        
        for row, skill in enumerate(self.skills):
            name_item = QTableWidgetItem(skill["name"])
            prompt_item = QTableWidgetItem(skill["prompt"])
            
            name_item.setTextAlignment(Qt.AlignLeft | Qt.AlignVCenter)
            prompt_item.setTextAlignment(Qt.AlignLeft | Qt.AlignVCenter)
            
            # 为当前选中的提示词添加标记
            if skill["name"] == self.selected_skill_name:
                name_item.setForeground(QColor(self.colors["primary"]))
                
            self.skill_table.setItem(row, 0, name_item)
            self.skill_table.setItem(row, 1, prompt_item)
            
        self.skill_table.blockSignals(False)
        
        # 选择当前选中的提示词行
        for row in range(self.skill_table.rowCount()):
            if self.skill_table.item(row, 0).text() == self.selected_skill_name:
                self.skill_table.selectRow(row)
                break
    
    def _add_skill(self):
        """添加新提示词"""
        # 创建添加提示词对话框
        dialog = QDialog(self)
        dialog.setWindowTitle("添加提示词")
        dialog.resize(600, 400)
        dialog.setStyleSheet(self.styleSheet())
        
        layout = QVBoxLayout(dialog)
        
        # 提示词名称
        name_label = QLabel("提示词名称:")
        name_edit = QLineEdit()
        layout.addWidget(name_label)
        layout.addWidget(name_edit)
        
        # 提示词
        prompt_label = QLabel("提示词模板:")
        prompt_edit = QPlainTextEdit()
        layout.addWidget(prompt_label)
        layout.addWidget(prompt_edit)
        
        # 提示信息
        tip = QLabel("提示: 提示词模板中可使用占位符：{selected_text}=选中的文本、{source_language}=当前语言、\n"
                    "{source_language_en}=当前语言(英文)、{target_language}=目标语言、{target_language_en}=目标语言(英文)")
        tip.setStyleSheet(f"color: {self.colors['light_text']}; font-style: italic;")
        tip.setWordWrap(True)
        layout.addWidget(tip)
        
        # 按钮
        btn_layout = QHBoxLayout()
        ok_btn = QPushButton("确定")
        cancel_btn = QPushButton("取消")
        btn_layout.addStretch()
        btn_layout.addWidget(ok_btn)
        btn_layout.addWidget(cancel_btn)
        layout.addLayout(btn_layout)
        
        ok_btn.clicked.connect(dialog.accept)
        cancel_btn.clicked.connect(dialog.reject)
        
        # 显示对话框
        if dialog.exec_() == QDialog.Accepted:
            name = name_edit.text().strip()
            prompt = prompt_edit.toPlainText().strip()
            
            if not name or not prompt:
                self.update_status("提示词名称和内容不能为空")
                return
                
            # 检查重名
            if any(skill["name"] == name for skill in self.skills):
                self.update_status(f"提示词名称 '{name}' 已存在")
                return
                
            # 添加新提示词
            new_skill = {"name": name, "prompt": prompt}
            self.skills.append(new_skill)
            
            # 更新表格
            row = self.skill_table.rowCount()
            self.skill_table.insertRow(row)
            
            name_item = QTableWidgetItem(name)
            prompt_item = QTableWidgetItem(prompt)
            
            name_item.setTextAlignment(Qt.AlignLeft | Qt.AlignVCenter)
            prompt_item.setTextAlignment(Qt.AlignLeft | Qt.AlignVCenter)
            
            self.skill_table.setItem(row, 0, name_item)
            self.skill_table.setItem(row, 1, prompt_item)
            self.skill_table.selectRow(row)
            
            self.update_status(f"已添加新提示词: {name}")
            
            # 保存配置
            self._save_config()
    
    def _remove_skill(self):
        """删除选中的提示词"""
        row = self.skill_table.currentRow()
        if row < 0:
            self.update_status("请先选择一个提示词")
            return
            
        if len(self.skills) <= 1:
            self.update_status("至少需要保留一个提示词")
            return
            
        # 获取提示词名称
        skill_name = self.skill_table.item(row, 0).text()
        
        # 从列表中移除
        self.skills.pop(row)
        
        # 从表格中移除
        self.skill_table.removeRow(row)
        
        # 如果删除的是当前选中的提示词，则更新选中的提示词
        if skill_name == self.selected_skill_name and self.skills:
            self.selected_skill_name = self.skills[0]["name"]
            self.skill_selected.emit(self.skills[0])
            
        # 如果还有项目，选择第一项
        if self.skill_table.rowCount() > 0:
            self.skill_table.selectRow(0)
            
        self.update_status(f"已删除提示词: {skill_name}")
        
        # 保存配置
        self._save_config()
    
    def _select_skill(self):
        """将当前选中的提示词设为默认"""
        row = self.skill_table.currentRow()
        if row < 0:
            self.update_status("请先选择一个提示词")
            return
            
        chosen_skill = self.skills[row]
        self.selected_skill_name = chosen_skill["name"]
        
        # 更新表格中所有项的颜色
        for r in range(self.skill_table.rowCount()):
            name_item = self.skill_table.item(r, 0)
            
            if r == row:
                name_item.setForeground(QColor(self.colors["primary"]))
            else:
                name_item.setForeground(QColor(self.colors["text"]))
        
        # 发射信号
        self.skill_selected.emit(chosen_skill)
        
        self.update_status(f"已将 {chosen_skill['name']} 设为默认提示词")
        
        # 保存配置
        self._save_config()
    
    def _on_skill_item_changed(self, item):
        """提示词表格内容变化处理"""
        row = item.row()
        column = item.column()
        new_value = item.text()
        
        if column == 0:  # 提示词名称
            # 检测重名
            for r in range(self.skill_table.rowCount()):
                if r != row and self.skill_table.item(r, 0).text() == new_value:
                    # 恢复原值
                    old_value = self.skills[row]["name"]
                    self.skill_table.blockSignals(True)
                    item.setText(old_value)
                    self.skill_table.blockSignals(False)
                    self.update_status(f"提示词名称 '{new_value}' 已存在")
                    return
             
            # 名称为空检查
            if not new_value.strip():
                old_value = self.skills[row]["name"]
                self.skill_table.blockSignals(True)
                item.setText(old_value)
                self.skill_table.blockSignals(False)
                self.update_status("提示词名称不能为空")
                return
                    
            # 更新提示词名称
            old_name = self.skills[row]["name"]
            self.skills[row]["name"] = new_value
            
            # 如果修改的是当前选中的提示词，则更新选中的提示词名称
            if self.selected_skill_name == old_name:
                self.selected_skill_name = new_value
                
        elif column == 1:  # 提示词
            if not new_value.strip():
                old_value = self.skills[row]["prompt"]
                self.skill_table.blockSignals(True)
                item.setText(old_value)
                self.skill_table.blockSignals(False)
                self.update_status("提示词不能为空")
                return
                
            self.skills[row]["prompt"] = new_value
        
        self.update_status("提示词已更新")
        
        # 保存配置
        self._save_config()
        
    def _save_config(self):
        """保存配置到文件"""
        if self.save_callback and callable(self.save_callback):
            config = {
                "api_profiles": self.api_profiles,
                "selected_api": self.selected_api,
                "models": self.models,
                "selected_model": self.selected_model,
                "skills": self.skills,
                "selected_skill": self.selected_skill_name,
                "target_language": self.target_language
            }
            self.save_callback(config)
    
    # 获取数据方法
    def get_api_profiles(self):
        return self.api_profiles
    
    def get_selected_api(self):
        return self.selected_api
    
    def get_models(self):
        return self.models
    
    def get_selected_model(self):
        return self.selected_model
    
    def get_skills(self):
        return self.skills
    
    def get_selected_skill_name(self):
        return self.selected_skill_name