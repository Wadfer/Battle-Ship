from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
                             QSizePolicy)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QFont
from pathlib import Path
from src.utils import get_image_path

class MenuWidget(QWidget):
    start_game = pyqtSignal()
    exit_game = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()

    def init_ui(self):
        # Создаем основной layout
        layout = QVBoxLayout()
        layout.setSpacing(20)
        layout.setContentsMargins(40, 40, 40, 40)
        
        # Название игры
        title_label = QLabel("Морской бой")
        title_font = QFont()
        title_font.setPointSize(48)
        title_font.setBold(True)
        title_label.setFont(title_font)
        title_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(title_label)

        # Кнопка "Начать игру"
        start_button = QPushButton("Начать игру")
        start_button.setFont(QFont("Arial", 24))
        start_button.setFixedSize(200, 60)
        start_button.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                border: none;
                border-radius: 10px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
        """)
        start_button.clicked.connect(self.start_game.emit)
        layout.addWidget(start_button)

        # Кнопка "Выход"
        exit_button = QPushButton("Выход")
        exit_button.setFont(QFont("Arial", 24))
        exit_button.setFixedSize(200, 60)
        exit_button.setStyleSheet("""
            QPushButton {
                background-color: #f44336;
                color: white;
                border: none;
                border-radius: 10px;
            }
            QPushButton:hover {
                background-color: #da190b;
            }
        """)
        exit_button.clicked.connect(self.exit_game.emit)
        layout.addWidget(exit_button)

        # Устанавливаем layout
        self.setLayout(layout)

        # Устанавливаем фон
        self.setStyleSheet("""
            QWidget {
                background-color: #f0f0f0;
            }
        """)
    def set_button_actions(self, start_game, exit_game):
        # Находим кнопки по тексту
        for button in self.findChildren(QPushButton):
            if button.text() == "Начать игру":
                button.clicked.connect(start_game)
            elif button.text() == "Выход":
                button.clicked.connect(exit_game)
