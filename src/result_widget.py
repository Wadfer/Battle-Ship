from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton, QHBoxLayout
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont, QPalette, QPixmap
from src.utils import get_image_path, load_image_from_resource

class ResultWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        
        # Заголовок результата
        self.result_label = QLabel()
        self.result_label.setFont(QFont("Arial", 24, QFont.Bold))
        self.result_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.result_label)
        layout.addSpacing(30)
        
        # Кнопки
        buttons_layout = QHBoxLayout()
        
        # Кнопка "Начать заново"
        restart_button = QPushButton("Начать заново")
        restart_button.setFont(QFont("Arial", 16))
        restart_button.clicked.connect(self.parent().show_ship_setup)
        buttons_layout.addWidget(restart_button)

        # Кнопка "В главное меню"
        menu_button = QPushButton("В главное меню")
        menu_button.setFont(QFont("Arial", 16))
        menu_button.clicked.connect(self.parent().show_menu)
        buttons_layout.addWidget(menu_button)

        layout.addLayout(buttons_layout)
        layout.addSpacing(20)
        
        self.setLayout(layout)

        # Заголовок игры
        title_label = QLabel("Морской бой")
        title_font = QFont()
        title_font.setPointSize(24)
        title_font.setBold(True)
        title_label.setFont(title_font)
        title_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(title_label)
        
        # Загружаем фон из ресурсов
        pixmap = load_image_from_resource(':/images/result_background.jpg')
        if not pixmap.isNull():
            self.setStyleSheet("""
                QWidget { 
                    background-color: transparent;
                }
                QLabel { color: black }
                QPushButton { 
                    background-color: #4CAF50
                    color: white
                    border: none
                    padding: 10px 20px
                    border-radius: 5px
                    min-width: 120px
                }
                QPushButton:hover { background-color: #45a049 }
            """)
            self.setPalette(global_palette)
            self.setAutoFillBackground(True)

    def back_clicked(self):
        self.parent().show_menu()

    def new_game_clicked(self):
        self.parent().show_ship_setup()
