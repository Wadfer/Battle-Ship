from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
                             QSizePolicy, QStackedWidget)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QFont, QPixmap
from pathlib import Path
from src.utils import get_image_path
from src.ship_placement_widget import ShipPlacementWidget

class MenuWidget(QWidget):
    start_game = pyqtSignal()
    exit_game = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()
        self.ship_placement_widget = None

    def init_ui(self):
        # Устанавливаем прозрачный фон
        self.setStyleSheet("""
            QWidget {
                background-color: rgba(0, 0, 0, 0);
            }
        """)
        
        # Устанавливаем фиксированный размер виджета
        self.setFixedSize(1000, 600)
        
        # Создаем основной layout
        layout = QVBoxLayout()
        layout.setSpacing(50)
        layout.setContentsMargins(0, 100, 0, 100)  # Уменьшаем отступы для лучшего использования пространства
        
        # Создаем контейнер для элементов меню
        menu_container = QWidget()
        menu_container.setStyleSheet("""
            QWidget {
                background: transparent;
            }
            QLabel {
                color: rgba(255, 255, 255, 0.8);
                background: transparent;
            }
            QPushButton {
                color: rgba(255, 255, 255, 0.8);
                border: none;
                background: transparent;
                text-align: center;
                padding: 10px;
                min-width: 200px;
                min-height: 60px;
            }
            QPushButton:hover {
                color: rgba(255, 255, 255, 1);
            }
            QPushButton::pressed {
                color: rgba(255, 255, 255, 1);
            }
        """)
        
        # Создаем верхний контейнер для названия
        title_container = QWidget()
        title_layout = QHBoxLayout()
        title_layout.setContentsMargins(0, 10, 0, 0)  # Уменьшаем отступ сверху
        
        # Название игры
        title_label = QLabel("Морской бой")
        title_font = QFont()
        title_font.setPointSize(48)
        title_font.setBold(True)
        title_label.setFont(title_font)
        title_label.setAlignment(Qt.AlignCenter)
        title_layout.addWidget(title_label)
        title_container.setLayout(title_layout)
        
        # Создаем контейнер для кнопок
        buttons_container = QWidget()
        buttons_layout = QVBoxLayout()
        buttons_layout.setSpacing(20)
        buttons_layout.setContentsMargins(0, 0, 0, 0)
        
        # Кнопка "Начать игру"
        start_button = QPushButton("Начать игру")
        start_button.setFont(QFont("Arial", 24))
        start_button.clicked.connect(self.start_game.emit)
        buttons_layout.addWidget(start_button)

        # Кнопка "Выход"
        exit_button = QPushButton("Выход")
        exit_button.setFont(QFont("Arial", 24))
        exit_button.clicked.connect(self.exit_game.emit)
        buttons_layout.addWidget(exit_button)
        
        buttons_container.setLayout(buttons_layout)

        # Добавляем контейнеры в основной layout
        layout.addWidget(title_container)  # Название в самом верху
        layout.addStretch(1)  # Все оставшееся пространство
        layout.addWidget(buttons_container, alignment=Qt.AlignCenter)
        
        # Создаем фоновое изображение
        self.background = QLabel(self)
        image_path = "src/images/menu_background.jpg"
        if Path(image_path).exists():
            pixmap = QPixmap(image_path)
            if not pixmap.isNull():
                self.background.setPixmap(pixmap)
                self.background.setScaledContents(True)
                self.background.setGeometry(0, 0, self.width(), self.height())
            else:
                print(f"Ошибка: не удалось загрузить изображение из {image_path}")
        else:
            print(f"Ошибка: файл {image_path} не найден")

    def on_resize(self, event):
        """Обрабатывает изменение размера виджета"""
        if hasattr(self, 'background'):
            self.background.setGeometry(0, 0, self.width(), self.height())
        super().resizeEvent(event)

    def init_ui(self):
        # Устанавливаем прозрачный фон
        self.setStyleSheet("""
            QWidget {
                background-color: rgba(0, 0, 0, 0);
            }
        """)
        
        # Устанавливаем фиксированный размер виджета
        self.setFixedSize(1000, 600)
        
        # Создаем основной layout
        layout = QVBoxLayout()
        layout.setSpacing(50)
        layout.setContentsMargins(0, 100, 0, 100)  # Уменьшаем отступы для лучшего использования пространства
        
        # Создаем контейнер для элементов меню
        menu_container = QWidget()
        menu_container.setStyleSheet("""
            QWidget {
                background: transparent;
            }
            QLabel {
                color: rgba(255, 255, 255, 0.8);
                background: transparent;
            }
            QPushButton {
                color: rgba(255, 255, 255, 0.8);
                border: none;
                background: transparent;
                text-align: center;
                padding: 10px;
                min-width: 200px;
                min-height: 60px;
            }
            QPushButton:hover {
                color: rgba(255, 255, 255, 1);
            }
            QPushButton::pressed {
                color: rgba(255, 255, 255, 1);
            }
        """)
        
        # Создаем верхний контейнер для названия
        title_container = QWidget()
        title_layout = QHBoxLayout()
        title_layout.setContentsMargins(0, 10, 0, 0)  # Уменьшаем отступ сверху
        
        # Название игры
        title_label = QLabel("Морской бой")
        title_font = QFont()
        title_font.setPointSize(48)
        title_font.setBold(True)
        title_label.setFont(title_font)
        title_label.setAlignment(Qt.AlignCenter)
        title_layout.addWidget(title_label)
        title_container.setLayout(title_layout)
        
        # Создаем контейнер для кнопок
        buttons_container = QWidget()
        buttons_layout = QVBoxLayout()
        buttons_layout.setSpacing(20)
        buttons_layout.setContentsMargins(0, 0, 0, 0)
        
        # Кнопка "Начать игру"
        start_button = QPushButton("Начать игру")
        start_button.setFont(QFont("Arial", 24))
        start_button.clicked.connect(self.start_game.emit)
        buttons_layout.addWidget(start_button)

        # Кнопка "Выход"
        exit_button = QPushButton("Выход")
        exit_button.setFont(QFont("Arial", 24))
        exit_button.clicked.connect(self.exit_game.emit)
        buttons_layout.addWidget(exit_button)
        
        buttons_container.setLayout(buttons_layout)

        # Добавляем контейнеры в основной layout
        layout.addWidget(title_container)  # Название в самом верху
        layout.addStretch(1)  # Все оставшееся пространство
        layout.addWidget(buttons_container, alignment=Qt.AlignCenter)
        
        # Создаем фоновое изображение
        self.background = QLabel(self)
        image_path = "src/images/menu_background.jpg"
        if Path(image_path).exists():
            pixmap = QPixmap(image_path)
            if not pixmap.isNull():
                self.background.setPixmap(pixmap)
                self.background.setScaledContents(True)
                self.background.setGeometry(0, 0, self.width(), self.height())
            else:
                print(f"Ошибка: не удалось загрузить изображение из {image_path}")
        else:
            print(f"Ошибка: файл {image_path} не найден")

        self.setLayout(layout)

    def on_resize(self, event):
        """Обрабатывает изменение размера виджета"""
        if hasattr(self, 'background'):
            self.background.setGeometry(0, 0, self.width(), self.height())
        super().resizeEvent(event)
    def set_button_actions(self, start_game, exit_game):
        """Устанавливает обработчики для кнопок"""
        for button in self.findChildren(QPushButton):
            if button.text() == "Начать игру":
                button.clicked.connect(start_game)
            elif button.text() == "Выход":
                button.clicked.connect(exit_game)
