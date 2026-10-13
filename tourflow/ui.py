from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QLineEdit,
    QPushButton, QMessageBox, QStackedWidget
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont

from tourflow.auth import register, login


# ============================================================
# ТИТУЛЬНЫЙ ЛИСТ
# ============================================================

class TitleWindow(QWidget):
    """Титульный экран с названием приложения."""

    def __init__(self, on_continue):
        super().__init__()
        self.on_continue = on_continue
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()

        title = QLabel("TourFlow")
        title.setAlignment(Qt.AlignCenter)
        title.setFont(QFont("Arial", 36, QFont.Bold))

        subtitle = QLabel("Информационная система управления\nтуроператорской деятельностью")
        subtitle.setAlignment(Qt.AlignCenter)
        subtitle.setFont(QFont("Arial", 14))

        version = QLabel("Версия 1.0")
        version.setAlignment(Qt.AlignCenter)
        version.setFont(QFont("Arial", 10))

        author = QLabel("Разработчик: Бабичев Андрей Вячеславович\nГруппа: ИСП11-25П")
        author.setAlignment(Qt.AlignCenter)
        author.setFont(QFont("Arial", 11))

        continue_btn = QPushButton("Продолжить")
        continue_btn.setFixedWidth(200)
        continue_btn.clicked.connect(self.on_continue)

        layout.addStretch()
        layout.addWidget(title)
        layout.addSpacing(20)
        layout.addWidget(subtitle)
        layout.addSpacing(40)
        layout.addWidget(version)
        layout.addSpacing(20)
        layout.addWidget(author)
        layout.addSpacing(40)
        layout.addWidget(continue_btn, alignment=Qt.AlignCenter)
        layout.addStretch()

        self.setLayout(layout)


# ============================================================
# ЭКРАН ВХОДА
# ============================================================

class LoginWindow(QWidget):
    def __init__(self, on_login_success, on_go_register):
        super().__init__()
        self.on_login_success = on_login_success
        self.on_go_register = on_go_register
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()

        title = QLabel("Вход в систему")
        title.setAlignment(Qt.AlignCenter)
        title.setFont(QFont("Arial", 20, QFont.Bold))

        self.username_edit = QLineEdit()
        self.username_edit.setPlaceholderText("Логин")

        self.password_edit = QLineEdit()
        self.password_edit.setPlaceholderText("Пароль")
        self.password_edit.setEchoMode(QLineEdit.Password)

        login_btn = QPushButton("Войти")
        login_btn.clicked.connect(self.handle_login)

        register_btn = QPushButton("Регистрация")
        register_btn.clicked.connect(self.on_go_register)

        layout.addStretch()
        layout.addWidget(title)
        layout.addSpacing(20)
        layout.addWidget(self.username_edit)
        layout.addWidget(self.password_edit)
        layout.addSpacing(10)
        layout.addWidget(login_btn)
        layout.addWidget(register_btn)
        layout.addStretch()

        self.setLayout(layout)

    def handle_login(self):
        username = self.username_edit.text()
        password = self.password_edit.text()

        ok, message = login(username, password)
        if ok:
            QMessageBox.information(self, "Успех", message)
            self.on_login_success(username)
        else:
            QMessageBox.warning(self, "Ошибка входа", message)


# ============================================================
# ЭКРАН РЕГИСТРАЦИИ
# ============================================================

class RegisterWindow(QWidget):
    def __init__(self, on_register_success, on_back):
        super().__init__()
        self.on_register_success = on_register_success
        self.on_back = on_back
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()

        title = QLabel("Регистрация")
        title.setAlignment(Qt.AlignCenter)
        title.setFont(QFont("Arial", 20, QFont.Bold))

        self.username_edit = QLineEdit()
        self.username_edit.setPlaceholderText("Придумайте логин")

        self.password_edit = QLineEdit()
        self.password_edit.setPlaceholderText("Придумайте пароль")
        self.password_edit.setEchoMode(QLineEdit.Password)

        self.password_confirm = QLineEdit()
        self.password_confirm.setPlaceholderText("Повторите пароль")
        self.password_confirm.setEchoMode(QLineEdit.Password)

        register_btn = QPushButton("Зарегистрироваться")
        register_btn.clicked.connect(self.handle_register)

        back_btn = QPushButton("Назад")
        back_btn.clicked.connect(self.on_back)

        layout.addStretch()
        layout.addWidget(title)
        layout.addSpacing(20)
        layout.addWidget(self.username_edit)
        layout.addWidget(self.password_edit)
        layout.addWidget(self.password_confirm)
        layout.addSpacing(10)
        layout.addWidget(register_btn)
        layout.addWidget(back_btn)
        layout.addStretch()

        self.setLayout(layout)

    def handle_register(self):
        username = self.username_edit.text()
        password = self.password_edit.text()
        confirm = self.password_confirm.text()

        if password != confirm:
            QMessageBox.warning(self, "Ошибка", "Пароли не совпадают.")
            return

        ok, message = register(username, password)
        if ok:
            QMessageBox.information(self, "Успех", message)
            self.on_register_success()
        else:
            QMessageBox.warning(self, "Ошибка регистрации", message)


# ============================================================
# ГЛАВНОЕ ОКНО (заглушка)
# ============================================================

class MainWindow(QWidget):
    def __init__(self, username):
        super().__init__()
        self.username = username
        self.setWindowTitle(f"TourFlow — {username}")
        self.resize(800, 600)
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()

        label = QLabel(f"Добро пожаловать в TourFlow, {self.username}!")
        label.setAlignment(Qt.AlignCenter)
        label.setFont(QFont("Arial", 16))

        layout.addStretch()
        layout.addWidget(label)
        layout.addStretch()

        self.setLayout(layout)


# ============================================================
# КОНТЕЙНЕР ЭКРАНОВ
# ============================================================

class AppRouter(QStackedWidget):
    """Управляет переключением экранов."""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("TourFlow")
        self.resize(700, 500)

        # Титульный лист
        self.title_window = TitleWindow(on_continue=self.show_login)
        # Вход
        self.login_window = LoginWindow(
            on_login_success=self.show_main,
            on_go_register=self.show_register
        )
        # Регистрация
        self.register_window = RegisterWindow(
            on_register_success=self.show_login,
            on_back=self.show_login
        )

        self.addWidget(self.title_window)    # index 0
        self.addWidget(self.login_window)    # index 1
        self.addWidget(self.register_window) # index 2

    def show_login(self):
        self.setCurrentIndex(1)

    def show_register(self):
        self.setCurrentIndex(2)

    def show_main(self, username):
        self.main_window = MainWindow(username)
        self.addWidget(self.main_window)
        self.setCurrentWidget(self.main_window)