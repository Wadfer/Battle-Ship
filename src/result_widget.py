from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton, QHBoxLayout
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont

class ResultWidget(QWidget):
    def __init__(self, winner, parent=None):
        super().__init__(parent)
        self.init_ui(winner)

    def init_ui(self, winner):
        layout = QVBoxLayout()
        
        # Заголовок игры
        title_label = QLabel("Морской бой")
        title_font = QFont()
        title_font.setPointSize(24)
        title_font.setBold(True)
        title_label.setFont(title_font)
        title_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(title_label)
        layout.addSpacing(30)
        
        # Результат игры
        result_label = QLabel(f"{winner} победил!")
        result_font = QFont()
        result_font.setPointSize(18)
        result_label.setFont(result_font)
        result_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(result_label)
        layout.addSpacing(20)
        
        # Кнопки
        buttons_layout = QHBoxLayout()
        
        # Кнопка "Назад"
        back_button = QPushButton("Назад")
        back_button.clicked.connect(self.back_clicked)
        buttons_layout.addWidget(back_button)
        
        # Кнопка "Новая игра"
        new_game_button = QPushButton("Новая игра")
        new_game_button.clicked.connect(self.new_game_clicked)
        buttons_layout.addWidget(new_game_button)
        
        layout.addLayout(buttons_layout)
        
        self.setLayout(layout)
        self.setStyleSheet("""
            QWidget {
                background-image: url(../images/result_background.jpg);
                background-repeat: no-repeat;
                background-position: center;
            }
            QLabel {
                color: black;
            }
            QPushButton {
                background-color: #4CAF50;
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 5px;
                min-width: 120px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
        """)

    def back_clicked(self):
        self.parent().show_menu()

    def new_game_clicked(self):
        self.parent().show_ship_setup()
