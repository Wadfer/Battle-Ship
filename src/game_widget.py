from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                               QPushButton, QGridLayout)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont
from src.utils import get_image_path

class GameWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()

        # Заголовок
        title = QLabel("Игровое поле")
        title.setFont(QFont("Arial", 20, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)

        # Создаем сетку для игрового поля
        grid = QGridLayout()
        grid.setSpacing(2)
        
        # Создаем кнопки для игрового поля
        self.setup_board(grid)

        layout.addLayout(grid)
        self.setLayout(layout)

    def setup_board(self, grid):
        # Создаем кнопки для игрового поля 10x10
        for row in range(10):
            for col in range(10):
                button = QPushButton()
                button.setFixedSize(30, 30)
                button.clicked.connect(lambda _, r=row, c=col: self.cell_clicked(r, c))
                grid.addWidget(button, row, col)

    def cell_clicked(self, row: int, col: int):
        # Обработка клика по ячейке
        pass
