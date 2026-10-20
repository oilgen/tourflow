from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QTabWidget, QTableWidget,
    QTableWidgetItem, QPushButton, QMessageBox, QFormLayout,
    QLineEdit, QComboBox
)
from PyQt5.QtGui import QFont

from db import (
    get_connection, add_tour, add_client, add_partner,
    list_tours, list_clients, list_partners, list_vouchers,
    list_payments, list_bookings, list_reviews
)


class AdminWindow(QWidget):
    def __init__(self, user_id, username):
        super().__init__()
        self.user_id = user_id
        self.username = username
        self.setWindowTitle(f"TourFlow — Администратор: {username}")
        self.resize(1100, 700)
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        title = QLabel(f"Панель администратора — {self.username}")
        title.setFont(QFont("Arial", 16, QFont.Bold))
        layout.addWidget(title)

        tabs = QTabWidget()
        tabs.addTab(self.create_users_tab(), "Пользователи")
        tabs.addTab(self.create_db_tab(), "Данные БД")
        tabs.addTab(self.create_add_tab(), "Добавить запись")

        layout.addWidget(tabs)
        self.setLayout(layout)

    # ---------- ПОЛЬЗОВАТЕЛИ ----------
    def create_users_tab(self):
        w = QWidget()
        layout = QVBoxLayout(w)

        self.users_table = QTableWidget()
        self.users_table.setColumnCount(4)
        self.users_table.setHorizontalHeaderLabels(["ID", "Логин", "Роль", "Создан"])
        layout.addWidget(self.users_table)

        btn_refresh = QPushButton("Обновить")
        btn_refresh.clicked.connect(self.refresh_users)
        layout.addWidget(btn_refresh)

        btn_delete = QPushButton("Удалить пользователя")
        btn_delete.clicked.connect(self.delete_user)
        layout.addWidget(btn_delete)

        self.refresh_users()
        return w

    def refresh_users(self):
        conn = get_connection()
        cur = conn.cursor()
        cur.execute('''
            SELECT u.id, u.username, r.name, u.created_at
            FROM users u JOIN roles r ON u.role_id = r.id
        ''')
        rows = cur.fetchall()
        conn.close()

        self.users_table.setRowCount(len(rows))
        for i, row in enumerate(rows):
            for j, v in enumerate(row):
                self.users_table.setItem(i, j, QTableWidgetItem(str(v)))

    def delete_user(self):
        row = self.users_table.currentRow()
        if row < 0:
            return
        uid = int(self.users_table.item(row, 0).text())
        if uid == self.user_id:
            QMessageBox.warning(self, "Ошибка", "Нельзя удалить самого себя.")
            return
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("DELETE FROM users WHERE id = ?", (uid,))
        conn.commit()
        conn.close()
        self.refresh_users()

    # ---------- ДАННЫЕ БД ----------
    def create_db_tab(self):
        w = QWidget()
        layout = QVBoxLayout(w)

        layout.addWidget(QLabel("Таблицы БД:"))
        self.table_combo = QComboBox()
        self.table_combo.addItems([
            "tours", "clients", "partners", "bookings",
            "vouchers", "payments", "reviews"
        ])
        self.table_combo.currentTextChanged.connect(self.load_table)
        layout.addWidget(self.table_combo)

        self.db_table = QTableWidget()
        layout.addWidget(self.db_table)

        self.load_table("tours")
        return w

    def load_table(self, table_name):
        """Загружает таблицу по имени."""
        allowed = {"tours", "clients", "partners", "bookings",
                   "vouchers", "payments", "reviews"}
        if table_name not in allowed:
            return

        conn = get_connection()
        cur = conn.cursor()
        cur.execute(f"SELECT * FROM {table_name}")
        rows = cur.fetchall()
        cols = [d[0] for d in cur.description]
        conn.close()

        self.db_table.setColumnCount(len(cols))
        self.db_table.setHorizontalHeaderLabels(cols)
        self.db_table.setRowCount(len(rows))
        for i, row in enumerate(rows):
            for j, v in enumerate(row):
                self.db_table.setItem(i, j, QTableWidgetItem(str(v)))

    # ---------- ДОБАВИТЬ ЗАПИСЬ ----------
    def create_add_tab(self):
        w = QWidget()
        layout = QVBoxLayout(w)

        # Тур
        layout.addWidget(QLabel("Добавить тур:"))
        form1 = QFormLayout()
        self.t_title = QLineEdit()
        self.t_dir = QLineEdit()
        self.t_start = QLineEdit("2026-07-01")
        self.t_end = QLineEdit("2026-07-10")
        self.t_price = QLineEdit("50000")
        self.t_cat = QComboBox()
        self.t_cat.addItems(["standard", "comfort", "vip"])
        form1.addRow("Название:", self.t_title)
        form1.addRow("Направление:", self.t_dir)
        form1.addRow("Начало:", self.t_start)
        form1.addRow("Конец:", self.t_end)
        form1.addRow("Цена:", self.t_price)
        form1.addRow("Категория:", self.t_cat)
        layout.addLayout(form1)

        btn_tour = QPushButton("Добавить тур")
        btn_tour.clicked.connect(self.admin_add_tour)
        layout.addWidget(btn_tour)

        # Клиент
        layout.addWidget(QLabel("Добавить клиента:"))
        form2 = QFormLayout()
        self.c_last = QLineEdit()
        self.c_first = QLineEdit()
        self.c_passport = QLineEdit()
        self.c_phone = QLineEdit()
        self.c_email = QLineEdit()
        form2.addRow("Фамилия:", self.c_last)
        form2.addRow("Имя:", self.c_first)
        form2.addRow("Паспорт:", self.c_passport)
        form2.addRow("Телефон:", self.c_phone)
        form2.addRow("Email:", self.c_email)
        layout.addLayout(form2)

        btn_cl = QPushButton("Добавить клиента")
        btn_cl.clicked.connect(self.admin_add_client)
        layout.addWidget(btn_cl)

        # Партнёр
        layout.addWidget(QLabel("Добавить партнёра:"))
        form3 = QFormLayout()
        self.p_name = QLineEdit()
        self.p_type = QComboBox()
        self.p_type.addItems(["hotel", "airline", "guide", "insurance", "transport"])
        self.p_inn = QLineEdit()
        self.p_phone = QLineEdit()
        self.p_email = QLineEdit()
        form3.addRow("Название:", self.p_name)
        form3.addRow("Тип:", self.p_type)
        form3.addRow("ИНН:", self.p_inn)
        form3.addRow("Телефон:", self.p_phone)
        form3.addRow("Email:", self.p_email)
        layout.addLayout(form3)

        btn_p = QPushButton("Добавить партнёра")
        btn_p.clicked.connect(self.admin_add_partner)
        layout.addWidget(btn_p)

        return w

    def admin_add_tour(self):
        try:
            add_tour(self.t_title.text(), self.t_dir.text(),
                     self.t_start.text(), self.t_end.text(),
                     float(self.t_price.text()), self.t_cat.currentText())
            QMessageBox.information(self, "OK", "Тур добавлен.")
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", str(e))

    def admin_add_client(self):
        try:
            add_client(self.c_last.text(), self.c_first.text(),
                       self.c_passport.text(), self.c_phone.text(),
                       self.c_email.text())
            QMessageBox.information(self, "OK", "Клиент добавлен.")
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", str(e))

    def admin_add_partner(self):
        try:
            add_partner(self.p_name.text(), self.p_type.currentText(),
                        self.p_inn.text(), self.p_phone.text(),
                        self.p_email.text())
            QMessageBox.information(self, "OK", "Партнёр добавлен.")
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", str(e))