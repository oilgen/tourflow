import sys
from PyQt5.QtWidgets import QApplication

from ui_login import LoginWindow
from ui_admin import AdminWindow
from ui_manager import ManagerWindow
from ui_financier import FinancierWindow
from ui_client import ClientWindow


class AppRouter:
    def __init__(self):
        self.current_window = None
        self.show_login()

    def show_login(self):
        self.current_window = LoginWindow(on_login_success=self.on_login)
        self.current_window.show()

    def on_login(self, role, user_id, username):
        """Открывает окно в зависимости от роли."""
        self.current_window.close()

        if role == "admin":
            self.current_window = AdminWindow(user_id, username)
        elif role == "manager":
            self.current_window = ManagerWindow(user_id, username)
        elif role == "financier":
            self.current_window = FinancierWindow(user_id, username)
        else:  # client
            self.current_window = ClientWindow(user_id, username)

        self.current_window.show()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setApplicationName("TourFlow")
    router = AppRouter()
    sys.exit(app.exec_())