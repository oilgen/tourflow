from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QTableWidget, QTableWidgetItem,
    QPushButton, QFormLayout, QComboBox, QDoubleSpinBox, QMessageBox,
    QTabWidget
)
from PyQt5.QtGui import QFont

from db import list_payments, add_payment, list_vouchers


class FinancierWindow(QWidget):
    def __init__(self, user_id, username):
        super().__init__()
        self.user_id = user_id
        self.username = username
        self.setWindowTitle(f"TourFlow — Финансист: {username}")
        self.resize(900, 600)
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        layout.addWidget(QLabel(f"Финансовый отдел — {self.username}"))

        tabs = QTabWidget()
        tabs.addTab(self.create_payments_tab(), "Платежи")
        tabs.addTab(self.create_add_payment_tab(), "Добавить платёж")
        layout.addWidget(tabs)
        self.setLayout(layout)

    def create_payments_tab(self):
        w = QWidget()
        layout = QVBoxLayout(w)
        self.payments_table = QTableWidget()
        self.payments_table.setColumnCount(6)
        self.payments_table.setHorizontalHeaderLabels(
            ["ID", "Путёвка", "Сумма", "Способ", "Дата", "Статус"]
        )
        layout.addWidget(self.payments_table)

        btn = QPushButton("Обновить")
        btn.clicked.connect(self.refresh_payments)
        layout.addWidget(btn)

        self.refresh_payments()
        return w

    def refresh_payments(self):
        rows = list_payments()
        self.payments_table.setRowCount(len(rows))
        for i, row in enumerate(rows):
            for j, v in enumerate(row):
                self.payments_table.setItem(i, j, QTableWidgetItem(str(v)))

    def create_add_payment_tab(self):
        w = QWidget()
        form = QFormLayout(w)

        self.voucher_combo = QComboBox()
        for v in list_vouchers():
            self.voucher_combo.addItem(f"{v[1]} — {v[2]} ({v[4]} руб.)", v[0])

        self.amount_spin = QDoubleSpinBox()
        self.amount_spin.setRange(0, 1_000_000)
        self.amount_spin.setDecimals(2)

        self.method_combo = QComboBox()
        self.method_combo.addItems(["cash", "card", "transfer"])

        form.addRow("Путёвка:", self.voucher_combo)
        form.addRow("Сумма:", self.amount_spin)
        form.addRow("Способ:", self.method_combo)

        btn = QPushButton("Добавить платёж")
        btn.clicked.connect(self.add_payment)
        form.addRow(btn)
        return w

    def add_payment(self):
        vid = self.voucher_combo.currentData()
        amount = self.amount_spin.value()
        if amount <= 0:
            QMessageBox.warning(self, "Ошибка", "Сумма должна быть больше нуля.")
            return
        add_payment(vid, amount, self.method_combo.currentText())
        QMessageBox.information(self, "OK", "Платёж добавлен.")
        self.refresh_payments()