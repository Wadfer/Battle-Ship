from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QPushButton,
                             QLabel, QRadioButton, QButtonGroup)
from PyQt5.QtCore import Qt
from .game_logic import Ship

class ShipPlacementDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Размещение кораблей")
        self.setModal(True)
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)

        # Ship orientation selection
        orientation_layout = QHBoxLayout()
        self.horizontal_radio = QRadioButton("Горизонтально")
        self.vertical_radio = QRadioButton("Вертикально")
        self.horizontal_radio.setChecked(True)
        
        orientation_group = QButtonGroup(self)
        orientation_group.addButton(self.horizontal_radio)
        orientation_group.addButton(self.vertical_radio)
        
        orientation_layout.addWidget(self.horizontal_radio)
        orientation_layout.addWidget(self.vertical_radio)
        layout.addLayout(orientation_layout)

        # Instructions
        instructions = QLabel("Выберите ориентацию корабля и кликните на поле для размещения")
        instructions.setAlignment(Qt.AlignCenter)
        layout.addWidget(instructions)

        # Buttons
        button_layout = QHBoxLayout()
        self.done_button = QPushButton("Готово")
        self.done_button.clicked.connect(self.accept)
        button_layout.addWidget(self.done_button)
        layout.addLayout(button_layout)

    def get_orientation(self) -> bool:
        return self.horizontal_radio.isChecked() 