from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QPushButton, QLabel, QTabWidget,
    QTableWidget, QTableWidgetItem, QMessageBox, QFormLayout,
    QLineEdit, QDoubleSpinBox, QComboBox
)
from PyQt5.QtGui import QFont

from db import (
    list_tours, add_tour, delete_tour,
    list_clients, add_client,
    list_bookings, create_booking, confirm_booking,
    list_partners, list_vouchers
)


class ManagerWindow(QWidget):
    def __init__(self, user_id, username):
        super().__init__()
        self.user_id = user_id
        self.username = username
        self.setWindowTitle(f"TourFlow — Менеджер: {username}")
        self.resize(1000, 650)
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        layout.addWidget(QLabel(f"Панель менеджера — {self.username}"))

        tabs = QTabWidget()
        tabs.addTab(self.create_tours_tab(), "Туры")
        tabs.addTab(self.create_clients_tab(), "Клиенты")
        tabs.addTab(self.create_bookings_tab(), "Брони")
        tabs.addTab(self.create_vouchers_tab(), "Путёвки")

        layout.addWidget(tabs)
        self.setLayout(layout)

    # ---------- ТУРЫ ----------
    def create_tours_tab(self):
        w = QWidget()
        layout = QVBoxLayout(w)

        self.tours_table = QTableWidget()
        self.tours_table.setColumnCount(7)
        self.tours_table.setHorizontalHeaderLabels(
            ["ID", "Название", "Направление", "Начало", "Конец", "Цена", "Категория"]
        )
        layout.addWidget(self.tours_table)

        form = QFormLayout()
        self.t_title = QLineEdit()
        self.t_dir = QLineEdit()
        self.t_start = QLineEdit("2026-06-01")
        self.t_end = QLineEdit("2026-06-10")
        self.t_price = QDoubleSpinBox()
        self.t_price.setRange(0, 1_000_000)
        self.t_cat = QComboBox()
        self.t_cat.addItems(["standard", "comfort", "vip"])

        form.addRow("Название:", self.t_title)
        form.addRow("Направление:", self.t_dir)
        form.addRow("Начало (ГГГГ-ММ-ДД):", self.t_start)
        form.addRow("Конец:", self.t_end)
        form.addRow("Цена:", self.t_price)
        form.addRow("Категория:", self.t_cat)
        layout.addLayout(form)

        btn_add = QPushButton("Добавить тур")
        btn_add.clicked.connect(self.add_tour)
        layout.addWidget(btn_add)

        btn_del = QPushButton("Удалить выбранный тур")
        btn_del.clicked.connect(self.delete_tour)
        layout.addWidget(btn_del)

        btn_refresh = QPushButton("Обновить")
        btn_refresh.clicked.connect(self.refresh_tours)
        layout.addWidget(btn_refresh)

        self.refresh_tours()
        return w

    def refresh_tours(self):
        tours = list_tours(only_active=False)
        self.tours_table.setRowCount(len(tours))
        for i, row in enumerate(tours):
            for j, v in enumerate(row):
                self.tours_table.setItem(i, j, QTableWidgetItem(str(v)))

    def add_tour(self):
        if not self.t_title.text() or not self.t_dir.text():
            QMessageBox.warning(self, "Ошибка", "Заполните название и направление.")
            return
        add_tour(
            self.t_title.text(), self.t_dir.text(),
            self.t_start.text(), self.t_end.text(),
            self.t_price.value(), self.t_cat.currentText()
        )
        self.refresh_tours()
        QMessageBox.information(self, "OK", "Тур добавлен.")

    def delete_tour(self):
        row = self.tours_table.currentRow()
        if row < 0:
            return
        tour_id = int(self.tours_table.item(row, 0).text())
        delete_tour(tour_id)
        self.refresh_tours()

    # ---------- КЛИЕНТЫ ----------
    def create_clients_tab(self):
        w = QWidget()
        layout = QVBoxLayout(w)

        self.clients_table = QTableWidget()
        self.clients_table.setColumnCount(5)
        self.clients_table.setHorizontalHeaderLabels(
            ["ID", "Фамилия", "Имя", "Телефон", "Email"]
        )
        layout.addWidget(self.clients_table)

        form = QFormLayout()
        self.c_last = QLineEdit()
        self.c_first = QLineEdit()
        self.c_passport = QLineEdit()
        self.c_phone = QLineEdit()
        self.c_email = QLineEdit()

        form.addRow("Фамилия:", self.c_last)
        form.addRow("Имя:", self.c_first)
        form.addRow("Паспорт:", self.c_passport)
        form.addRow("Телефон:", self.c_phone)
        form.addRow("Email:", self.c_email)
        layout.addLayout(form)

        btn_add = QPushButton("Добавить клиента")
        btn_add.clicked.connect(self.add_client)
        layout.addWidget(btn_add)

        btn_refresh = QPushButton("Обновить")
        btn_refresh.clicked.connect(self.refresh_clients)
        layout.addWidget(btn_refresh)

        self.refresh_clients()
        return w

    def refresh_clients(self):
        clients = list_clients()
        self.clients_table.setRowCount(len(clients))
        for i, row in enumerate(clients):
            for j, v in enumerate(row):
                self.clients_table.setItem(i, j, QTableWidgetItem(str(v)))

    def add_client(self):
        if not (self.c_last.text() and self.c_first.text() and self.c_passport.text()):
            QMessageBox.warning(self, "Ошибка", "Заполните обязательные поля.")
            return
        try:
            add_client(self.c_last.text(), self.c_first.text(),
                       self.c_passport.text(), self.c_phone.text(),
                       self.c_email.text())
            self.refresh_clients()
            QMessageBox.information(self, "OK", "Клиент добавлен.")
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", str(e))

    # ---------- БРОНИ ----------
    def create_bookings_tab(self):
        w = QWidget()
        layout = QVBoxLayout(w)

        self.bookings_table = QTableWidget()
        self.bookings_table.setColumnCount(5)
        self.bookings_table.setHorizontalHeaderLabels(
            ["ID", "Тур", "Партнёр", "Услуга", "Статус"]
        )
        layout.addWidget(self.bookings_table)

        form = QFormLayout()
        self.b_tour = QComboBox()
        self.b_partner = QComboBox()
        self.b_service = QComboBox()
        self.b_service.addItems(["hotel", "flight", "excursion", "transfer"])

        for t in list_tours():
            self.b_tour.addItem(t[1], t[0])
        for p in list_partners():
            self.b_partner.addItem(p[1], p[0])

        form.addRow("Тур:", self.b_tour)
        form.addRow("Партнёр:", self.b_partner)
        form.addRow("Услуга:", self.b_service)
        layout.addLayout(form)

        btn_add = QPushButton("Создать бронь")
        btn_add.clicked.connect(self.create_booking)
        layout.addWidget(btn_add)

        btn_confirm = QPushButton("Подтвердить бронь")
        btn_confirm.clicked.connect(self.confirm_booking)
        layout.addWidget(btn_confirm)

        btn_refresh = QPushButton("Обновить")
        btn_refresh.clicked.connect(self.refresh_bookings)
        layout.addWidget(btn_refresh)

        self.refresh_bookings()
        return w

    def refresh_bookings(self):
        rows = list_bookings()
        self.bookings_table.setRowCount(len(rows))
        for i, row in enumerate(rows):
            for j, v in enumerate(row):
                self.bookings_table.setItem(i, j, QTableWidgetItem(str(v)))

    def create_booking(self):
        create_booking(self.b_tour.currentData(),
                       self.b_partner.currentData(),
                       self.b_service.currentText())
        self.refresh_bookings()

    def confirm_booking(self):
        row = self.bookings_table.currentRow()
        if row < 0:
            return
        bid = int(self.bookings_table.item(row, 0).text())
        confirm_booking(bid)
        self.refresh_bookings()

    # ---------- ПУТЁВКИ ----------
    def create_vouchers_tab(self):
        w = QWidget()
        layout = QVBoxLayout(w)

        self.vouchers_table = QTableWidget()
        self.vouchers_table.setColumnCount(6)
        self.vouchers_table.setHorizontalHeaderLabels(
            ["ID", "Номер", "Клиент", "Тур", "Стоимость", "Статус"]
        )
        layout.addWidget(self.vouchers_table)

        btn_refresh = QPushButton("Обновить")
        btn_refresh.clicked.connect(self.refresh_vouchers)
        layout.addWidget(btn_refresh)

        self.refresh_vouchers()
        return w

    def refresh_vouchers(self):
        rows = list_vouchers()
        self.vouchers_table.setRowCount(len(rows))
        for i, row in enumerate(rows):
            for j, v in enumerate(row):
                self.vouchers_table.setItem(i, j, QTableWidgetItem(str(v)))