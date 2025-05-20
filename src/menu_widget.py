from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
                             QSizePolicy)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont
from pathlib import Path
from src.utils import get_image_path

class MenuWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()

    def init_ui(self):
        # Создаем основной layout
        layout = QVBoxLayout()
        
        # Название игры
        title_label = QLabel("Морской бой")
        title_font = QFont()
        title_font.setPointSize(24)
        title_font.setBold(True)
        title_label.setFont(title_font)
        title_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(title_label)
        layout.addSpacing(30)
        
        # Кнопки
        buttons_layout = QVBoxLayout()
        buttons_layout.setAlignment(Qt.AlignCenter)
        buttons_layout.setSpacing(20)
        
        # Кнопка "Начать игру"
        start_button = QPushButton("Начать игру")
        start_button.setFixedSize(200, 50)
        start_button.setFont(QFont("Arial", 12))
        buttons_layout.addWidget(start_button)
        
        # Кнопка "Выход"
        exit_button = QPushButton("Выход")
        exit_button.setFixedSize(200, 50)
        exit_button.setFont(QFont("Arial", 12))
        exit_button.setStyleSheet("""
            QPushButton {
                background-color: #f44336;
                color: white;
                border: none;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #da190b;
            }
        """)
        
        # Добавляем кнопки в layout
        buttons_layout.addWidget(start_button)
        buttons_layout.addWidget(exit_button)
        
        # Добавляем все элементы в основной layout
        layout.addWidget(title_label)
        layout.addStretch(1)
        layout.addLayout(buttons_layout)
        layout.addStretch(1)
        
        # Устанавливаем background
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
