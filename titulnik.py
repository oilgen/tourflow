import sys
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QLabel
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont


class TitleWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("TripVibe")
        self.resize(700, 450)
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()

        title = QLabel("Trip(itropa)Vibe")
        title.setAlignment(Qt.AlignCenter)
        title.setFont(QFont("Arial", 32, QFont.Bold))

        subtitle = QLabel("Информационная система управления\nтуроператорской деятельностью")
        subtitle.setAlignment(Qt.AlignCenter)
        subtitle.setFont(QFont("Arial", 14))

        version = QLabel("Версия 1.0")
        version.setAlignment(Qt.AlignCenter)
        version.setFont(QFont("Arial", 10))

        author = QLabel("Разработчик: Бабичев Андрей Вячеславович\nГруппа: ИСП11-25П")
        author.setAlignment(Qt.AlignCenter)
        author.setFont(QFont("Arial", 11))

        layout.addStretch()
        layout.addWidget(title)
        layout.addSpacing(20)
        layout.addWidget(subtitle)
        layout.addSpacing(40)
        layout.addWidget(version)
        layout.addSpacing(20)
        layout.addWidget(author)
        layout.addStretch()

        self.setLayout(layout)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = TitleWindow()
    window.show()
    sys.exit(app.exec_())