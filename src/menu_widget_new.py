from PyQt5.QtWidgets import (QWidget, QLabel, QPushButton, QVBoxLayout)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QFont, QPixmap
from pathlib import Path
from src.rules_window import RulesWindow

class MenuWidget(QWidget):
    start_game = pyqtSignal()
    exit_game = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        # Создаем фоновое изображение
        self.background = QLabel(self)
        self.background.setGeometry(0, 0, 1000, 600)
        self.background.setScaledContents(True)
        self.background.lower()  # Отправляем фон на задний план
        
        # Загружаем фоновое изображение
        image_path = Path("src/images/menu_background.jpg")
        if image_path.exists():
            pixmap = QPixmap(str(image_path))
            if not pixmap.isNull():
                self.background.setPixmap(pixmap)
            else:
                print(f"Ошибка: не удалось загрузить изображение из {image_path}")
        else:
            print(f"Ошибка: файл {image_path} не найден")

        # Создаем основной layout
        layout = QVBoxLayout()
        
        # Название игры
        title_label = QLabel("Морской бой")
        title_font = QFont()
        title_font.setPointSize(48)
        title_font.setBold(True)
        title_label.setFont(title_font)
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setStyleSheet("color: white;")
        layout.addWidget(title_label)
        
        # Добавляем вертикальный spacer для центрирования кнопок
        layout.addStretch(1)
        
        # Кнопка "Начать игру"
        start_button = QPushButton("Начать игру")
        start_button.setFont(QFont("Arial", 24))
        start_button.setStyleSheet("""
            QPushButton {
                color: white;
                border: none;
                background: transparent;
                text-align: center;
                padding: 10px;
                min-width: 200px;
                min-height: 60px;
            }
            QPushButton:hover {
                color: #FFD700;
            }
            QPushButton::pressed {
                color: #FFA500;
            }
        """)
        start_button.clicked.connect(self.show_ship_placement)
        layout.addWidget(start_button)

        # Кнопка "Правила"
        rules_button = QPushButton("Правила")
        rules_button.setFont(QFont("Arial", 24))
        rules_button.setStyleSheet("""
            QPushButton {
                color: white;
                border: none;
                background: transparent;
                text-align: center;
                padding: 10px;
                min-width: 200px;
                min-height: 60px;
            }
            QPushButton:hover {
                color: #FFD700;
            }
            QPushButton::pressed {
                color: #FFA500;
            }
        """)
        rules_button.clicked.connect(self.show_rules)
        layout.addWidget(rules_button)

        # Кнопка "Выход"
        exit_button = QPushButton("Выход")
        exit_button.setFont(QFont("Arial", 24))
        exit_button.setStyleSheet("""
            QPushButton {
                color: white;
                border: none;
                background: transparent;
                text-align: center;
                padding: 10px;
                min-width: 200px;
                min-height: 60px;
            }
            QPushButton:hover {
                color: #FFD700;
            }
            QPushButton::pressed {
                color: #FFA500;
            }
        """)
        exit_button.clicked.connect(self.exit_game.emit)
        layout.addWidget(exit_button)
        
        # Добавляем вертикальный spacer для центрирования кнопок
        layout.addStretch(1)

        # Устанавливаем layout для MenuWidget
        self.setLayout(layout)

    def show_ship_placement(self):
        """Показывает экран расстановки кораблей"""
        self.start_game.emit()

    def show_rules(self):
        """Показывает окно с правилами игры"""
        self.rules_window = RulesWindow()
        self.rules_window.show()

    def show_game(self):
        """Показывает игровое поле"""
        if self.ship_placement_widget:
            self.ship_placement_widget.hide()
        self.start_game.emit()

    def resizeEvent(self, event):
        """Обрабатывает изменение размера виджета"""
        # Обновляем размеры всех дочерних элементов
        for child in self.children():
            if hasattr(child, 'setGeometry'):
                child.setGeometry(0, 0, self.width(), self.height())
        super().resizeEvent(event)

    def update_background_size(self):
        """Обновляет размер фона и контейнера"""
        if hasattr(self, 'background'):
            self.background.setGeometry(0, 0, self.width(), self.height())
        
        # Обновляем размер контейнера
        if hasattr(self, 'container'):
            self.container.setGeometry(0, 0, self.width(), self.height())

    def resizeEvent(self, event):
        """Обрабатывает изменение размера виджета"""
        self.update_background_size()
        super().resizeEvent(event)


