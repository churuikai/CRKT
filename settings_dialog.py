# settings_dialog.py
from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton,
    QListWidget, QWidget, QTabWidget, QGroupBox, QFormLayout, QInputDialog,
    QMessageBox, QListWidgetItem, QSplitter, QTableWidget,
    QTableWidgetItem, QHeaderView, QPlainTextEdit, QStyledItemDelegate
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
    skill_selected = pyqtSignal(dict)  # 传递选中的技能
    
    def __init__(self, 
                api_profiles=None, 
                selected_api="", 
                models=None, 
                selected_model="", 
                skills=None, 
                selected_skill_name="",
                parent=None):
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
        
        # 定义配色
        self.colors = {
            "primary": "#82529d",         # 主色调 - 紫色
            "primary_light": "#a371ba",   # 浅紫色 (按钮)
            "light_bg": "#f2f0fb",        # 浅色背景
            "lighter_bg": "#dfddf5",      # 更浅色背景
            "white": "#ffffff",           # 白色
            "text": "#333333",            # 文字颜色
            "light_text": "#666666",      # 浅色文字
            "border": "#d0c9e3",          # 边框颜色
            "selected_bg": "#e8e6f8",     # 选中背景
        }
        
        # 设置样式表
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
            }}
            QTableWidget::item {{
                background-color: transparent;
                color: {self.colors["text"]};
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
            }}
            QSplitter::handle {{
                background-color: {self.colors["lighter_bg"]};
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
        self.tab_widget.addTab(self._create_skill_tab(), "技能管理")
        
        main_layout.addWidget(self.tab_widget)
        
        # 底部按钮
        button_layout = QHBoxLayout()
        self.ok_button = QPushButton("确定")
        self.cancel_button = QPushButton("取消")
        
        button_layout.addStretch()
        button_layout.addWidget(self.ok_button)
        button_layout.addWidget(self.cancel_button)
        
        main_layout.addLayout(button_layout)
        
        # 绑定事件
        self.ok_button.clicked.connect(self.accept)
        self.cancel_button.clicked.connect(self.reject)
        
    def _create_api_tab(self):
        """创建API设置标签页"""
        api_tab = QWidget()
        api_layout = QVBoxLayout(api_tab)
        api_layout.setContentsMargins(10, 15, 10, 10)
        
        # API管理区域
        api_splitter = QSplitter(Qt.Horizontal)
        api_splitter.setContentsMargins(0, 0, 0, 0)
        
        # 左侧API列表
        api_list_widget = QWidget()
        api_list_layout = QVBoxLayout(api_list_widget)
        api_list_layout.setContentsMargins(0, 0, 0, 0)
        
        api_list_group = QGroupBox("API 配置列表")
        api_list_inner_layout = QVBoxLayout(api_list_group)
        
        self.api_list = QListWidget()
        self.api_list.setAlternatingRowColors(True)
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
        
        self.api_name_edit = QLineEdit()
        self.api_key_edit = QPlainTextEdit()
        self.api_key_edit.setFixedHeight(100)
        self.base_url_edit = QLineEdit()
        
        api_edit_inner_layout.addRow("配置名称:", self.api_name_edit)
        api_edit_inner_layout.addRow("API 密钥:", self.api_key_edit)
        api_edit_inner_layout.addRow("基础 URL:", self.base_url_edit)
        
        # 保存API按钮
        save_btn_layout = QHBoxLayout()
        self.save_api_btn = QPushButton("保存")
        save_btn_layout.addStretch()
        save_btn_layout.addWidget(self.save_api_btn)
        api_edit_inner_layout.addRow("", save_btn_layout)
        
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
        self.save_api_btn.clicked.connect(self._save_current_api)
        
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
        if self.selected_model:
            current_model_label = QLabel(f"当前模型: <b>{self.selected_model}</b>")
            current_model_label.setStyleSheet(f"color: {self.colors['primary']};")
            model_layout.addWidget(current_model_label)
        
        # 模型列表组
        model_group = QGroupBox("可用模型")
        model_list_layout = QVBoxLayout(model_group)
        
        self.model_list = QListWidget()
        self.model_list.setAlternatingRowColors(True)
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
        """创建技能管理标签页"""
        skill_tab = QWidget()
        skill_layout = QVBoxLayout(skill_tab)
        skill_layout.setContentsMargins(10, 15, 10, 10)
        
        # 显示当前选中技能
        if self.selected_skill_name:
            current_skill_label = QLabel(f"当前技能: <b>{self.selected_skill_name}</b>")
            current_skill_label.setStyleSheet(f"color: {self.colors['primary']};")
            skill_layout.addWidget(current_skill_label)
        
        # 技能表格
        self.skill_table = QTableWidget()
        self.skill_table.setColumnCount(2)
        self.skill_table.setHorizontalHeaderLabels(["技能名称", "提示词模板"])
        self.skill_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeToContents)
        self.skill_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        self.skill_table.verticalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
        self.skill_table.setWordWrap(True)
        self.skill_table.setAlternatingRowColors(True)
        self.skill_table.setItemDelegateForColumn(1, MultiLineDelegate(self.skill_table))
        self.skill_table.setEditTriggers(QTableWidget.DoubleClicked | QTableWidget.SelectedClicked)
        
        skill_layout.addWidget(self.skill_table)
        
        # 提示标签
        tip_label = QLabel("提示: 双击单元格可编辑内容。提示词中可使用{selected_text}代表选中的文本。")
        tip_label.setWordWrap(True)
        tip_label.setStyleSheet(f"color: {self.colors['light_text']}; font-style: italic;")
        skill_layout.addWidget(tip_label)
        
        # 按钮组
        skill_btn_layout = QHBoxLayout()
        self.add_skill_btn = QPushButton("添加技能")
        self.remove_skill_btn = QPushButton("删除技能")
        self.select_skill_btn = QPushButton("设为默认")
        
        skill_btn_layout.addWidget(self.add_skill_btn)
        skill_btn_layout.addWidget(self.remove_skill_btn)
        skill_btn_layout.addWidget(self.select_skill_btn)
        skill_layout.addLayout(skill_btn_layout)
        
        # 绑定技能相关事件
        self.add_skill_btn.clicked.connect(self._add_skill)
        self.remove_skill_btn.clicked.connect(self._remove_skill)
        self.select_skill_btn.clicked.connect(self._select_skill)
        self.skill_table.itemChanged.connect(self._on_skill_item_changed)
        
        # 加载技能列表
        self._load_skills()
        
        return skill_tab
    
    # API相关方法
    def _load_api_profiles(self):
        """加载API配置到列表"""
        self.api_list.clear()
        for profile in self.api_profiles:
            item = QListWidgetItem(profile["name"])
            # 为当前选中的API添加标记
            if profile["name"] == self.selected_api:
                item.setSelected(True)
                item.setForeground(QColor(self.colors["primary"]))
                # 载入选中的API配置到编辑区
                self.api_name_edit.setText(profile["name"])
                self.api_key_edit.setPlainText(profile["api_key"])
                self.base_url_edit.setText(profile["base_url"])
            self.api_list.addItem(item)
    
    def _add_api(self):
        """添加新的API配置"""
        name, ok = QInputDialog.getText(
            self, "添加API配置", "请输入API配置名称:",
            flags=Qt.WindowCloseButtonHint | Qt.WindowTitleHint
        )
        
        if ok and name.strip():
            # 检查重名
            if any(profile["name"] == name for profile in self.api_profiles):
                QMessageBox.warning(self, "错误", "该API配置名称已存在！")
                return
                
            # 添加新配置
            new_profile = {
                "name": name,
                "api_key": "",
                "base_url": "https://api.openai.com/v1/"
            }
            self.api_profiles.append(new_profile)
            
            # 更新列表
            item = QListWidgetItem(name)
            self.api_list.addItem(item)
            self.api_list.setCurrentItem(item)
            
            # 清空编辑区，准备编辑新配置
            self.api_name_edit.setText(name)
            self.api_key_edit.clear()
            self.base_url_edit.setText("https://api.openai.com/v1/")
    
    def _remove_api(self):
        """删除选中的API配置"""
        current_item = self.api_list.currentItem()
        if not current_item:
            QMessageBox.warning(self, "警告", "请先选择一个API配置！")
            return
            
        name = current_item.text()
        if len(self.api_profiles) <= 1:
            QMessageBox.warning(self, "警告", "至少需要保留一个API配置！")
            return
            
        # 删除配置
        self.api_profiles = [p for p in self.api_profiles if p["name"] != name]
        self.api_list.takeItem(self.api_list.row(current_item))
        
        # 如果删除的是当前选中的API，则更新选中的API
        if name == self.selected_api and self.api_profiles:
            self.selected_api = self.api_profiles[0]["name"]
            
            # 更新编辑区
            self.api_name_edit.setText(self.api_profiles[0]["name"])
            self.api_key_edit.setPlainText(self.api_profiles[0]["api_key"])
            self.base_url_edit.setText(self.api_profiles[0]["base_url"])
            
            # 更新列表选中状态
            self.api_list.setCurrentRow(0)
            
    def _select_api(self):
        """选择当前API配置为默认"""
        current_item = self.api_list.currentItem()
        if not current_item:
            QMessageBox.warning(self, "警告", "请先选择一个API配置！")
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
                
        # 通知用户
        QMessageBox.information(self, "成功", f"已将 {name} 设为默认API！")
    
    def _save_current_api(self):
        """保存当前编辑区的API配置"""
        current_item = self.api_list.currentItem()
        if not current_item:
            QMessageBox.warning(self, "警告", "请先选择一个API配置！")
            return
            
        old_name = current_item.text()
        new_name = self.api_name_edit.text().strip()
        api_key = self.api_key_edit.toPlainText().strip()
        base_url = self.base_url_edit.text().strip()
        
        if not new_name:
            QMessageBox.warning(self, "警告", "API配置名称不能为空！")
            return
            
        # 如果名称变了，检查重名
        if old_name != new_name and any(p["name"] == new_name for p in self.api_profiles):
            QMessageBox.warning(self, "错误", "该API配置名称已存在！")
            return
            
        # 更新配置
        for profile in self.api_profiles:
            if profile["name"] == old_name:
                profile["name"] = new_name
                profile["api_key"] = api_key
                profile["base_url"] = base_url
                break
                
        # 如果修改的是当前选中的API配置，更新selected_api
        if old_name == self.selected_api:
            self.selected_api = new_name
            
        # 更新列表项
        current_item.setText(new_name)
        
        QMessageBox.information(self, "成功", "API配置已保存！")
    
    def _api_selected(self, current, previous):
        """当选择API列表中的项目时，更新编辑区"""
        if not current:
            return
            
        name = current.text()
        for profile in self.api_profiles:
            if profile["name"] == name:
                self.api_name_edit.setText(profile["name"])
                self.api_key_edit.setPlainText(profile["api_key"])
                self.base_url_edit.setText(profile["base_url"])
                break
    
    # 模型相关方法
    def _load_models(self):
        """加载模型到列表"""
        self.model_list.clear()
        for model in self.models:
            item = QListWidgetItem(model)
            # 为当前选中的模型添加标记
            if model == self.selected_model:
                item.setSelected(True)
                item.setForeground(QColor(self.colors["primary"]))
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
                QMessageBox.warning(self, "错误", "该模型已存在！")
                return
                
            # 添加模型
            self.models.append(model_name)
            
            # 更新列表
            item = QListWidgetItem(model_name)
            self.model_list.addItem(item)
    
    def _remove_model(self):
        """删除选中的模型"""
        current_item = self.model_list.currentItem()
        if not current_item:
            QMessageBox.warning(self, "警告", "请先选择一个模型！")
            return
            
        model_name = current_item.text()
        if len(self.models) <= 1:
            QMessageBox.warning(self, "警告", "至少需要保留一个模型！")
            return
            
        # 删除模型
        self.models.remove(model_name)
        self.model_list.takeItem(self.model_list.row(current_item))
        
        # 如果删除的是当前选中的模型，则更新选中的模型
        if model_name == self.selected_model and self.models:
            self.selected_model = self.models[0]
            self.model_list.setCurrentRow(0)
    
    def _select_model(self):
        """选择当前模型为默认"""
        current_item = self.model_list.currentItem()
        if not current_item:
            QMessageBox.warning(self, "警告", "请先选择一个模型！")
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
                
        # 通知用户
        QMessageBox.information(self, "成功", f"已将 {model_name} 设为默认模型！")
    
    # 技能相关方法
    def _load_skills(self):
        """加载技能到表格"""
        self.skill_table.blockSignals(True)
        self.skill_table.setRowCount(len(self.skills))
        
        for row, skill in enumerate(self.skills):
            name_item = QTableWidgetItem(skill["name"])
            prompt_item = QTableWidgetItem(skill["prompt"])
            
            name_item.setTextAlignment(Qt.AlignLeft | Qt.AlignTop)
            prompt_item.setTextAlignment(Qt.AlignLeft | Qt.AlignTop)
            
            # 为当前选中的技能添加标记
            if skill["name"] == self.selected_skill_name:
                name_item.setForeground(QColor(self.colors["primary"]))
                
            self.skill_table.setItem(row, 0, name_item)
            self.skill_table.setItem(row, 1, prompt_item)
            
        self.skill_table.blockSignals(False)
    
    def _add_skill(self):
        """添加新技能"""
        # 创建添加技能对话框
        dialog = QDialog(self)
        dialog.setWindowTitle("添加技能")
        dialog.resize(600, 400)
        dialog.setStyleSheet(self.styleSheet())
        
        layout = QVBoxLayout(dialog)
        
        # 技能名称
        name_label = QLabel("技能名称:")
        name_edit = QLineEdit()
        layout.addWidget(name_label)
        layout.addWidget(name_edit)
        
        # 提示词
        prompt_label = QLabel("提示词模板:")
        prompt_edit = QPlainTextEdit()
        layout.addWidget(prompt_label)
        layout.addWidget(prompt_edit)
        
        # 提示信息
        tip = QLabel("提示: 提示词模板中可以使用 {selected_text} 占位符表示选中的文本")
        tip.setStyleSheet(f"color: {self.colors['light_text']}; font-style: italic;")
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
                QMessageBox.warning(self, "警告", "技能名称和提示词不能为空！")
                return
                
            # 检查重名
            if any(skill["name"] == name for skill in self.skills):
                QMessageBox.warning(self, "警告", "技能名称已存在！")
                return
                
            # 添加新技能
            self.skills.append({"name": name, "prompt": prompt})
            
            # 更新表格
            row = self.skill_table.rowCount()
            self.skill_table.insertRow(row)
            
            name_item = QTableWidgetItem(name)
            prompt_item = QTableWidgetItem(prompt)
            
            name_item.setTextAlignment(Qt.AlignLeft | Qt.AlignTop)
            prompt_item.setTextAlignment(Qt.AlignLeft | Qt.AlignTop)
            
            self.skill_table.setItem(row, 0, name_item)
            self.skill_table.setItem(row, 1, prompt_item)
    
    def _remove_skill(self):
        """删除选中的技能"""
        row = self.skill_table.currentRow()
        if row < 0:
            QMessageBox.warning(self, "警告", "请先选择一个技能！")
            return
            
        if len(self.skills) <= 1:
            QMessageBox.warning(self, "警告", "至少需要保留一个技能！")
            return
            
        # 获取技能名称
        skill_name = self.skill_table.item(row, 0).text()
        
        # 从列表中移除
        self.skills.pop(row)
        
        # 从表格中移除
        self.skill_table.removeRow(row)
        
        # 如果删除的是当前选中的技能，则更新选中的技能
        if skill_name == self.selected_skill_name and self.skills:
            self.selected_skill_name = self.skills[0]["name"]
            self.skill_selected.emit(self.skills[0])
            
            # 更新表格中第一行的标记
            if self.skill_table.rowCount() > 0:
                name_item = self.skill_table.item(0, 0)
                name_item.setForeground(QColor(self.colors["primary"]))
    
    def _select_skill(self):
        """将当前选中的技能设为默认"""
        row = self.skill_table.currentRow()
        if row < 0:
            QMessageBox.warning(self, "警告", "请先选择一个技能！")
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
            
        # 通知用户
        QMessageBox.information(self, "成功", f"已将 {chosen_skill['name']} 设为默认技能！")
    
    def _on_skill_item_changed(self, item):
        """技能表格内容变化处理"""
        row = item.row()
        column = item.column()
        new_value = item.text()
        
        if column == 0:  # 技能名称
            # 检测重名
            for r in range(self.skill_table.rowCount()):
                if r != row and self.skill_table.item(r, 0).text() == new_value:
                    QMessageBox.warning(self, "警告", "技能名称已存在！")
                    
                    # 恢复原值
                    old_value = self.skills[row]["name"]
                    self.skill_table.blockSignals(True)
                    item.setText(old_value)
                    self.skill_table.blockSignals(False)
                    return
                    
            # 更新技能名称
            old_name = self.skills[row]["name"]
            self.skills[row]["name"] = new_value
            
            # 如果修改的是当前选中的技能，则更新选中的技能名称
            if self.selected_skill_name == old_name:
                self.selected_skill_name = new_value
                
        elif column == 1:  # 提示词
            self.skills[row]["prompt"] = new_value
    
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