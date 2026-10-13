from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QMessageBox, QComboBox
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont

from auth import register, login


class LoginWindow(QWidget):
    def __init__(self, on_login_success):
        super().__init__()
        self.on_login_success = on_login_success
        self.setWindowTitle("TourFlow — Вход")
        self.resize(400, 450)
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()

        title = QLabel("TourFlow")
        title.setAlignment(Qt.AlignCenter)
        title.setFont(QFont("Arial", 26, QFont.Bold))

        subtitle = QLabel("Система управления туроператором")
        subtitle.setAlignment(Qt.AlignCenter)

        self.username_edit = QLineEdit()
        self.username_edit.setPlaceholderText("Логин")

        self.password_edit = QLineEdit()
        self.password_edit.setPlaceholderText("Пароль")
        self.password_edit.setEchoMode(QLineEdit.Password)

        self.role_combo = QComboBox()
        self.role_combo.addItems(["client", "manager", "financier", "admin"])
        self.role_combo.setVisible(False)  # показывается только при регистрации

        self.login_btn = QPushButton("Войти")
        self.login_btn.clicked.connect(self.handle_login)

        self.register_btn = QPushButton("Регистрация")
        self.register_btn.clicked.connect(self.toggle_register_mode)

        self.register_confirm_btn = QPushButton("Зарегистрироваться")
        self.register_confirm_btn.clicked.connect(self.handle_register)
        self.register_confirm_btn.setVisible(False)

        self.back_btn = QPushButton("Назад к входу")
        self.back_btn.clicked.connect(self.toggle_register_mode)
        self.back_btn.setVisible(False)

        layout.addStretch()
        layout.addWidget(title)
        layout.addWidget(subtitle)
        layout.addSpacing(20)
        layout.addWidget(self.username_edit)
        layout.addWidget(self.password_edit)
        layout.addWidget(self.role_combo)
        layout.addSpacing(10)
        layout.addWidget(self.login_btn)
        layout.addWidget(self.register_btn)
        layout.addWidget(self.register_confirm_btn)
        layout.addWidget(self.back_btn)
        layout.addStretch()

        self.setLayout(layout)

    def toggle_register_mode(self):
        """Переключение между входом и регистрацией."""
        is_login = self.login_btn.isVisible()
        self.login_btn.setVisible(not is_login)
        self.register_btn.setVisible(not is_login)
        self.register_confirm_btn.setVisible(is_login)
        self.back_btn.setVisible(is_login)
        self.role_combo.setVisible(is_login)

    def handle_login(self):
        username = self.username_edit.text()
        password = self.password_edit.text()
        role, user_id, message = login(username, password)

        if role:
            QMessageBox.information(self, "Успех", message)
            self.on_login_success(role, user_id, username)
        else:
            QMessageBox.warning(self, "Ошибка входа", message)

    def handle_register(self):
        username = self.username_edit.text()
        password = self.password_edit.text()
        role = self.role_combo.currentText()

        ok, message = register(username, password, role)
        if ok:
            QMessageBox.information(self, "Успех", message)
            self.toggle_register_mode()
        else:
            QMessageBox.warning(self, "Ошибка регистрации", message)