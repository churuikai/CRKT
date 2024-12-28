# api_settings_dialog.py
from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPlainTextEdit,
    QPushButton
)
from PyQt5.QtCore import Qt

class ApiSettingsDialog(QDialog):
    """
    用于统一设置 API-Key, Base-Url, API-Headers 的对话框
    """
    def __init__(self, api_key="", base_url="", api_headers="", parent=None):
        super().__init__(parent)
        self.setWindowTitle("设置 API")
        self.resize(600, 400)

        self.api_key = api_key
        self.base_url = base_url
        self.api_headers = api_headers

        # 主布局
        main_layout = QVBoxLayout(self)

        # API-Key
        lbl_key = QLabel("API-Key:", self)
        self.txt_api_key = QPlainTextEdit(self)
        self.txt_api_key.setPlainText(api_key)
        main_layout.addWidget(lbl_key)
        main_layout.addWidget(self.txt_api_key)

        # Base-URL
        lbl_url = QLabel("Base-Url:", self)
        self.txt_base_url = QLineEdit(self)
        self.txt_base_url.setText(base_url)
        main_layout.addWidget(lbl_url)
        main_layout.addWidget(self.txt_base_url)

        # API-Headers
        lbl_headers = QLabel("API-Headers:", self)
        self.txt_api_headers = QPlainTextEdit(self)
        self.txt_api_headers.setPlainText(api_headers)
        main_layout.addWidget(lbl_headers)
        main_layout.addWidget(self.txt_api_headers)

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

    def get_values(self):
        """
        在外部根据 exec_() == Accepted 判断后，使用此方法获取对话框中填入的数据
        """
        return (
            self.txt_api_key.toPlainText().strip(),
            self.txt_base_url.text().strip(),
            self.txt_api_headers.toPlainText().strip()
        )
