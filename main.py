import sys
import os
from PyQt5.QtWidgets import (QApplication, QMainWindow, QPushButton, 
                           QVBoxLayout, QWidget, QMessageBox, QLabel)
from PyQt5.QtGui import QPixmap, QPalette, QBrush, QFont
from PyQt5.QtCore import Qt
from ship_placement import ShipPlacementScreen

def resource_path(relative_path):
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath('.'), relative_path)

class MainMenu(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()
        
    def initUI(self):
        # Настройка свойств окна
        self.setWindowTitle('Морской бой')
        self.setFixedSize(1200, 700)
        
        # Создаем центральный виджет и макет
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        layout.setAlignment(Qt.AlignCenter)
        layout.setSpacing(20)
        
        # Добавил заголовок
        title_label = QLabel('МОРСКОЙ БОЙ', self)
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setStyleSheet("""
            QLabel {
                color: white;
                font-size: 48px;
                font-weight: bold;
                text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.5);
                margin-bottom: 40px;
            }
        """)
        layout.addWidget(title_label)
        
        # Создание кнопок
        new_game_btn = QPushButton('Новая игра', self)
        rules_btn = QPushButton('Правила', self)
        exit_btn = QPushButton('Выход', self)
        
        # стили кнопок
        button_style = """
            QPushButton {
                background-color: rgba(74, 74, 74, 180);
                color: white;
                border: 2px solid #666666;
                border-radius: 5px;
                padding: 15px;
                font-size: 18px;
                min-width: 250px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: rgba(102, 102, 102, 180);
            }
        """
        new_game_btn.setStyleSheet(button_style)
        rules_btn.setStyleSheet(button_style)
        exit_btn.setStyleSheet(button_style)
        
        # Add buttons to layout
        layout.addWidget(new_game_btn)
        layout.addWidget(rules_btn)
        layout.addWidget(exit_btn)
        
        # Connect buttons to functions
        new_game_btn.clicked.connect(self.start_new_game)
        rules_btn.clicked.connect(self.show_rules)
        exit_btn.clicked.connect(self.close)
        
        # Set background
        self.set_background()
        
    def set_background(self):
        try:
            # Try to load background from assets directory
            background_path = resource_path("assets/menu_background.jpg")
            if os.path.exists(background_path):
                palette = QPalette()
                pixmap = QPixmap(background_path)
                if not pixmap.isNull():
                    scaled_pixmap = pixmap.scaled(self.size(), Qt.KeepAspectRatioByExpanding, Qt.SmoothTransformation)
                    palette.setBrush(QPalette.Window, QBrush(scaled_pixmap))
                    self.setPalette(palette)
                    return
        except Exception as e:
            print(f"Error loading background: {e}")
        
        # If background loading fails, set default gradient background
        self.setStyleSheet("""
            QMainWindow {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                          stop:0 #1a237e, stop:1 #0d47a1);
            }
        """)
    
    def start_new_game(self):
        self.ship_placement = ShipPlacementScreen()
        self.ship_placement.show()
        self.hide()
    
    def show_rules(self):
        rules_text = """
        Правила игры "Морской бой":
        
        1. Игра ведется на двух квадратных полях 10x10.
        2. На своем поле игрок размещает корабли:
           - 1 корабль на 4 клетки
           - 2 корабля на 3 клетки
           - 3 корабля на 2 клетки
           - 4 корабля на 1 клетку

        3. Для поворота корабля нужно нажать на кнопку К.
        4. Корабли не могут соприкасаться друг с другом.
        5. Игроки по очереди делают выстрелы по полю противника.
        6. Если выстрел попал в корабль, игрок делает еще один ход.
        7. Побеждает тот, кто первым уничтожит все корабли противника.
        """
        msg = QMessageBox(self)
        msg.setWindowTitle("Правила игры")
        msg.setText(rules_text)
        msg.setStyleSheet("""
            QMessageBox {
                background-color: #2b2b2b;
                color: white;
            }
            QMessageBox QLabel {
                color: white;
                font-size: 14px;
            }
            QPushButton {
                background-color: #4a4a4a;
                color: white;
                border: 2px solid #666666;
                border-radius: 5px;
                padding: 5px 15px;
                min-width: 150px;
            }
            QPushButton:hover {
                background-color: #666666;
            }
        """)
        msg.exec_()

def main():
    app = QApplication(sys.argv)
    
    # Set application style
    app.setStyle('Fusion')
    
    # Create and show main menu
    menu = MainMenu()
    menu.show()
    
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()