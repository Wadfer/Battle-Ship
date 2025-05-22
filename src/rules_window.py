from PyQt5.QtWidgets import (QWidget, QLabel, QVBoxLayout, QTextEdit, QDialog, QDialogButtonBox)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont

class RulesWindow(QDialog):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("Правила игры")
        self.setGeometry(100, 100, 800, 600)

        # Создаем основной layout
        layout = QVBoxLayout()

        # Заголовок
        title_label = QLabel("Правила игры Морской бой")
        title_font = QFont()
        title_font.setPointSize(24)
        title_font.setBold(True)
        title_label.setFont(title_font)
        title_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(title_label)

        # Текст с правилами
        rules_text = QTextEdit()
        rules_text.setReadOnly(True)
        rules_text.setFont(QFont("Arial", 12))
        
        rules_text.setText("""
        Правила игры Морской бой:

        1. Цель игры:
        Уничтожить все корабли противника, прежде чем он уничтожит ваши.

        2. Корабли:
        - 1-палубный ×4
        - 2-палубный ×3
        - 3-палубный ×2
        - 4-палубный ×1

        3. Расстановка кораблей:
        - Корабли не могут касаться друг друга
        - Корабли можно размещать горизонтально или вертикально
        - Корабли можно поворачивать

        4. Ход игры:
        - Игроки по очереди делают выстрелы
        - После выстрела ход переходит к противнику
        - При попадании в корабль ход остаётся у игрока

        5. Победа:
        Побеждает тот, кто первым уничтожит все корабли противника
        """)
        layout.addWidget(rules_text)

        # Кнопка закрытия
        button_box = QDialogButtonBox(QDialogButtonBox.Ok)
        button_box.accepted.connect(self.accept)
        layout.addWidget(button_box)

        self.setLayout(layout)
