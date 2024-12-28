import json
from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QTableWidget, QTableWidgetItem,
    QPushButton, QLineEdit, QMessageBox, QHeaderView, QLabel, QPlainTextEdit,
    QStyledItemDelegate
)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QTextOption


class MultiLineDelegate(QStyledItemDelegate):
    """
    自定义委托，用于在单元格中使用多行文本编辑器（QPlainTextEdit）。
    当用户双击编辑时，可以方便地编辑多行内容。
    """
    def createEditor(self, parent, option, index):
        editor = QPlainTextEdit(parent)
        # 启用自动换行
        editor.setWordWrapMode(QTextOption.WordWrap)
        return editor

    def setEditorData(self, editor, index):
        value = index.model().data(index, Qt.EditRole)
        if value is not None:
            editor.setPlainText(str(value))

    def setModelData(self, editor, model, index):
        model.setData(index, editor.toPlainText(), Qt.EditRole)


class AddSkillDialog(QDialog):
    """
    自定义对话框，用于添加技能（名称、提示词）
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("添加技能")
        self.resize(600, 400)

        # 布局
        main_layout = QVBoxLayout(self)
        
        # 技能名称
        name_label = QLabel("技能名称：", self)
        self.name_edit = QLineEdit(self)
        main_layout.addWidget(name_label)
        main_layout.addWidget(self.name_edit)

        # 提示词
        prompt_label = QLabel("提示词：", self)
        self.prompt_edit = QPlainTextEdit(self)
        # 给出提示
        tip_label = QLabel("说明：可使用特殊字符串 {selected_text} 代表划词选中的文字。", self)
        tip_label.setStyleSheet("color: gray; font-style: italic;")

        main_layout.addWidget(prompt_label)
        main_layout.addWidget(self.prompt_edit)
        main_layout.addWidget(tip_label)

        # 按钮区域
        btn_layout = QHBoxLayout()
        self.btn_ok = QPushButton("确定", self)
        self.btn_cancel = QPushButton("取消", self)
        btn_layout.addWidget(self.btn_ok)
        btn_layout.addWidget(self.btn_cancel)
        main_layout.addLayout(btn_layout)

        # 绑定事件
        self.btn_ok.clicked.connect(self.accept)
        self.btn_cancel.clicked.connect(self.reject)

    def get_data(self):
        """
        在外部对 exec_() == Accepted 做判断后再取数据
        """
        name = self.name_edit.text().strip()
        prompt = self.prompt_edit.toPlainText().strip()
        return name, prompt


class SkillManager(QDialog):
    """
    技能管理窗口：
    - 可添加、删除技能（技能包含：name, prompt）
    - 直接双击表格修改技能名称或提示词，实时生效
    - 可选择某个技能作为当前默认技能
    - 选择后发射信号 skill_selected，外部捕捉此信号并进行持久化
    """
    skill_selected = pyqtSignal(dict)  # 传递选中的技能 { "name":..., "prompt":... }

    def __init__(self, skills=None, selected_skill_name=None, parent=None):
        """
        :param skills: [{'name': 'xx', 'prompt': 'xx'}, ...]
        :param selected_skill_name: 当前已选技能的名称
        """
        super().__init__(parent)
        self.setWindowTitle("技能管理")
        self.skills = skills if skills else []
        self.selected_skill_name = selected_skill_name

        self.resize(600, 400)
        layout = QVBoxLayout()
        self.setLayout(layout)

        self.table = QTableWidget()
        self.table.setColumnCount(2)
        self.table.setHorizontalHeaderLabels(["技能名称", "提示词"])

        # 设置列宽模式: 第一列根据内容宽度，第二列随窗口宽度自适应
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)

        # 自动根据内容调整行高
        self.table.verticalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
        # 表格里启用自动换行
        self.table.setWordWrap(True)

        # 对第二列（提示词）使用多行编辑委托
        self.table.setItemDelegateForColumn(1, MultiLineDelegate(self.table))

        # 允许双击可编辑
        self.table.setEditTriggers(
            QTableWidget.DoubleClicked | QTableWidget.SelectedClicked
        )
        layout.addWidget(self.table)

        # 按钮区（去掉“修改技能”按钮）
        btn_layout = QHBoxLayout()
        self.btn_add = QPushButton("添加技能")
        self.btn_remove = QPushButton("删除技能")
        self.btn_select = QPushButton("设为默认")
        self.btn_save = QPushButton("关闭并保存")

        btn_layout.addWidget(self.btn_add)
        btn_layout.addWidget(self.btn_remove)
        btn_layout.addWidget(self.btn_select)
        btn_layout.addWidget(self.btn_save)
        layout.addLayout(btn_layout)

        # 绑定事件
        self.btn_add.clicked.connect(self.on_add_skill)
        self.btn_remove.clicked.connect(self.on_remove_skill)
        self.btn_select.clicked.connect(self.on_select_skill)
        self.btn_save.clicked.connect(self.accept)
        
        # 表格内容变化事件
        self.table.itemChanged.connect(self.on_item_changed)

        # 初始化表格数据
        self._load_skills_into_table()

    # ------------------------------------------------------------------------
    # 表格加载 & 编辑事件
    # ------------------------------------------------------------------------
    def _load_skills_into_table(self):
        """将 self.skills 中的数据加载到 QTableWidget"""
        self.table.blockSignals(True)  # 防止在填充时触发 itemChanged
        self.table.setRowCount(len(self.skills))
        for row_idx, skill in enumerate(self.skills):
            name_item = QTableWidgetItem(skill["name"])
            prompt_item = QTableWidgetItem(skill["prompt"])

            # 多行文本左上对齐
            name_item.setTextAlignment(Qt.AlignLeft | Qt.AlignTop)
            prompt_item.setTextAlignment(Qt.AlignLeft | Qt.AlignTop)

            self.table.setItem(row_idx, 0, name_item)
            self.table.setItem(row_idx, 1, prompt_item)
        self.table.blockSignals(False)

    def on_item_changed(self, item):
        """
        当用户直接在表格中编辑某个单元格时触发。
        col=0 -> 技能名称
        col=1 -> 技能提示词
        """
        row = item.row()
        col = item.column()
        new_value = item.text()

        if col == 0:
            # 检测重名
            for r in range(self.table.rowCount()):
                if r != row:
                    other_name = self.table.item(r, 0).text()
                    if other_name == new_value:
                        QMessageBox.warning(self, "警告", "技能名称已存在，请修改。")
                        # 直接恢复为旧值
                        old_val = self.skills[row]["name"]
                        self.table.blockSignals(True)
                        item.setText(old_val)
                        self.table.blockSignals(False)
                        return

            # 更新 self.skills
            self.skills[row]["name"] = new_value

        elif col == 1:
            self.skills[row]["prompt"] = new_value

        # 重新调整行高，以适应更改后的文本
        self.table.resizeRowToContents(row)

    # ------------------------------------------------------------------------
    # 按钮事件
    # ------------------------------------------------------------------------
    def on_add_skill(self):
        """添加新技能（弹窗输入名称和提示词）"""
        dlg = AddSkillDialog(self)
        if dlg.exec_() == dlg.Accepted:
            name, prompt = dlg.get_data()
            if not name or not prompt:
                return
            
            # 重名检测
            for skill in self.skills:
                if skill["name"] == name:
                    QMessageBox.warning(self, "警告", "技能名称已存在，请修改。")
                    return

            # 新增
            self.skills.append({"name": name, "prompt": prompt})
            # 在表格末尾添加一行
            row_idx = self.table.rowCount()
            self.table.blockSignals(True)
            self.table.insertRow(row_idx)

            name_item = QTableWidgetItem(name)
            prompt_item = QTableWidgetItem(prompt)

            # 多行文本左上对齐
            name_item.setTextAlignment(Qt.AlignLeft | Qt.AlignTop)
            prompt_item.setTextAlignment(Qt.AlignLeft | Qt.AlignTop)

            self.table.setItem(row_idx, 0, name_item)
            self.table.setItem(row_idx, 1, prompt_item)

            self.table.blockSignals(False)

            # 自适应新行行高
            self.table.resizeRowToContents(row_idx)

    def on_remove_skill(self):
        """删除选中的技能"""
        row = self.table.currentRow()
        if row < 0 or row >= len(self.skills):
            QMessageBox.warning(self, "警告", "请先选中要删除的技能行。")
            return

        # 从 self.skills 中移除
        self.skills.pop(row)

        # 从表格删除该行
        self.table.blockSignals(True)
        self.table.removeRow(row)
        self.table.blockSignals(False)

    def on_select_skill(self):
        """
        选中某个技能后发射信号，这里只是将选中的技能信息发射出去，
        在外部进行持久化操作（或也可在此处写入QSettings）。
        """
        row = self.table.currentRow()
        if row < 0 or row >= len(self.skills):
            QMessageBox.warning(self, "警告", "请先选中要设置的技能行。")
            return

        chosen_skill = self.skills[row]
        self.selected_skill_name = chosen_skill["name"]
        QMessageBox.information(self, "成功", f"已将 [{self.selected_skill_name}] 设为默认技能。")
        self.skill_selected.emit(chosen_skill)

    # ------------------------------------------------------------------------
    # 关闭并保存
    # ------------------------------------------------------------------------
    def accept(self):
        """
        点击 '关闭并保存' 按钮时，先从表格中再取一次最新数据（以防万一）；
        然后关闭对话框。
        """
        self._sync_table_to_skills()
        super().accept()

    def _sync_table_to_skills(self):
        """将表格里的最新数据同步回 self.skills"""
        for row_idx in range(self.table.rowCount()):
            name_item = self.table.item(row_idx, 0)
            prompt_item = self.table.item(row_idx, 1)
            self.skills[row_idx]["name"] = name_item.text().strip() if name_item else ""
            self.skills[row_idx]["prompt"] = prompt_item.text().strip() if prompt_item else ""
