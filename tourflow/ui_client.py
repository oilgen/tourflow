from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QTableWidget, QTableWidgetItem, QMessageBox, QComboBox,
    QSpinBox, QTextEdit, QTabWidget, QInputDialog
)
from PyQt5.QtGui import QFont

from db import list_tours, list_vouchers, create_voucher, add_review


class ClientWindow(QWidget):
    def __init__(self, user_id, username):
        super().__init__()
        self.user_id = user_id
        self.username = username
        self.setWindowTitle(f"TourFlow — Клиент: {username}")
        self.resize(900, 600)
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()

        title = QLabel(f"Здравствуйте, {self.username}!")
        title.setFont(QFont("Arial", 16, QFont.Bold))
        layout.addWidget(title)

        tabs = QTabWidget()
        tabs.addTab(self.create_tours_tab(), "Каталог туров")
        tabs.addTab(self.create_reviews_tab(), "Оставить отзыв")

        layout.addWidget(tabs)
        self.setLayout(layout)

    # ---------- Каталог туров ----------
    def create_tours_tab(self):
        w = QWidget()
        layout = QVBoxLayout(w)

        self.tours_table = QTableWidget()
        self.tours_table.setColumnCount(6)
        self.tours_table.setHorizontalHeaderLabels(
            ["ID", "Название", "Направление", "Дата начала", "Дата окончания", "Цена"]
        )
        layout.addWidget(self.tours_table)

        btn_refresh = QPushButton("Обновить каталог")
        btn_refresh.clicked.connect(self.refresh_tours)
        layout.addWidget(btn_refresh)

        btn_order = QPushButton("Оформить заявку на тур")
        btn_order.clicked.connect(self.order_tour)
        layout.addWidget(btn_order)

        self.refresh_tours()
        return w

    def refresh_tours(self):
        tours = list_tours(only_active=True)
        self.tours_table.setRowCount(len(tours))
        for i, row in enumerate(tours):
            for j, value in enumerate(row):
                self.tours_table.setItem(i, j, QTableWidgetItem(str(value)))

    def order_tour(self):
        row = self.tours_table.currentRow()
        if row < 0:
            QMessageBox.warning(self, "Ошибка", "Выберите тур из таблицы.")
            return
        tour_id = int(self.tours_table.item(row, 0).text())
        price = float(self.tours_table.item(row, 5).text())

        # Упрощённо: используем фиктивного клиента (в реальной системе — по user_id)
        from db import get_connection
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("SELECT id FROM clients LIMIT 1")
        r = cur.fetchone()
        conn.close()
        if not r:
            QMessageBox.warning(self, "Ошибка", "Нет ни одного клиента в БД. Обратитесь к администратору.")
            return
        client_id = r[0]

        number = create_voucher(client_id, tour_id, price)
        QMessageBox.information(self, "Заявка создана",
                                f"Путёвка № {number} успешно оформлена.")

    # ---------- Отзывы ----------
    def create_reviews_tab(self):
        w = QWidget()
        layout = QVBoxLayout(w)

        layout.addWidget(QLabel("Выберите тур:"))
        self.review_tour_combo = QComboBox()
        layout.addWidget(self.review_tour_combo)

        layout.addWidget(QLabel("Оценка (1–5):"))
        self.rating_spin = QSpinBox()
        self.rating_spin.setRange(1, 5)
        self.rating_spin.setValue(5)
        layout.addWidget(self.rating_spin)

        layout.addWidget(QLabel("Текст отзыва:"))
        self.review_text = QTextEdit()
        layout.addWidget(self.review_text)

        btn_submit = QPushButton("Отправить отзыв")
        btn_submit.clicked.connect(self.submit_review)
        layout.addWidget(btn_submit)

        self.refresh_tour_combo()
        return w

    def refresh_tour_combo(self):
        self.review_tour_combo.clear()
        for tour in list_tours():
            self.review_tour_combo.addItem(tour[1], tour[0])

    def submit_review(self):
        tour_id = self.review_tour_combo.currentData()
        rating = self.rating_spin.value()
        text = self.review_text.toPlainText().strip()

        if not text:
            QMessageBox.warning(self, "Ошибка", "Введите текст отзыва.")
            return

        from db import get_connection
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("SELECT id FROM clients LIMIT 1")
        r = cur.fetchone()
        conn.close()
        if not r:
            QMessageBox.warning(self, "Ошибка", "Нет клиентов в БД.")
            return
        client_id = r[0]

        add_review(client_id, tour_id, rating, text)
        QMessageBox.information(self, "Спасибо", "Отзыв сохранён.")
        self.review_text.clear()