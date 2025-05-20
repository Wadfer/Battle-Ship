from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                               QPushButton, QGridLayout, QGroupBox, QRadioButton, 
                               QButtonGroup)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont
from src.utils import get_image_path

class ShipSetupWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()

        # Заголовок
        title = QLabel("Размещение кораблей")
        title.setFont(QFont("Arial", 20, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)

        # Создаем сетку для кораблей
        grid = QGridLayout()
        grid.setSpacing(10)

        # Добавляем корабли
        self.setup_ships(grid)

        # Добавляем кнопки
        buttons_layout = QHBoxLayout()
        self.start_button = QPushButton("Начать игру")
        self.start_button.clicked.connect(self.start_game)
        buttons_layout.addWidget(self.start_button)

        layout.addLayout(grid)
        layout.addLayout(buttons_layout)
        self.setLayout(layout)

    def setup_ships(self, grid):
        # Создаем группы для кораблей
        ship_groups = []
        for i in range(4):
            group = QGroupBox(f"{4-i} палубный")
            group_layout = QVBoxLayout()
            
            # Создаем радиокнопки для каждого корабля
            button_group = QButtonGroup()
            for j in range(4-i):
                button = QRadioButton(f"Корабль {j+1}")
                button_group.addButton(button)
                group_layout.addWidget(button)
            
            group.setLayout(group_layout)
            grid.addWidget(group, i // 2, i % 2)
            ship_groups.append(button_group)

    def start_game(self):
        # Проверяем, выбраны ли все корабли
        if not self.check_ship_selection():
            return
        
        # Переходим к игре
        self.parent().show_game()

    def check_ship_selection(self) -> bool:
        # Проверяем, выбраны ли все корабли
        return True  # В реальной реализации нужно проверить выбор всех кораблей
