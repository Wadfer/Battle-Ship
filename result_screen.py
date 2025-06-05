from PyQt5.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                           QPushButton, QLabel, QGridLayout)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap, QPalette, QBrush
import os
from datetime import datetime

class ResultScreen(QMainWindow):
    def __init__(self, player_won, game_stats=None):
        super().__init__()
        self.player_won = player_won
        self.game_stats = game_stats or {
            'shots': 0,
            'hits': 0,
            'start_time': datetime.now(),
            'player_ships_destroyed': 0,
            'computer_ships_destroyed': 0
        }
        self.initUI()
        
    def initUI(self):
        self.setWindowTitle('Морской бой - Результат')
        self.setFixedSize(1000, 700)
        
        # Create central widget and main layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(50, 50, 50, 50)
        main_layout.setSpacing(30)
        
        # Result title
        result_title = QLabel("Победа!" if self.player_won else "Поражение!")
        result_title.setAlignment(Qt.AlignCenter)
        result_title.setStyleSheet("""
            QLabel {
                color: #ffffff;
                font-size: 48px;
                font-weight: bold;
                text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.8);
                background-color: rgba(0, 0, 0, 0.5);
                padding: 20px;
                border-radius: 10px;
            }
        """)
        main_layout.addWidget(result_title)
        
        # Statistics container
        stats_container = QWidget()
        stats_container.setStyleSheet("""
            QWidget {
                background-color: rgba(0, 0, 0, 0.7);
                border-radius: 10px;
                padding: 20px;
            }
        """)
        stats_layout = QVBoxLayout(stats_container)
        stats_layout.setSpacing(15)
        
        # Calculate statistics
        total_shots = self.game_stats['shots']
        hits = self.game_stats['hits']
        hit_percentage = (hits / total_shots * 100) if total_shots > 0 else 0
        game_duration = datetime.now() - self.game_stats['start_time']
        minutes = game_duration.seconds // 60
        seconds = game_duration.seconds % 60
        
        # Create statistics labels
        stats = [
            f"Всего выстрелов: {total_shots}",
            f"Попаданий: {hits}",
            f"Процент попаданий: {hit_percentage:.1f}%",
            f"Уничтожено кораблей противника: {self.game_stats['computer_ships_destroyed']}",
            f"Потеряно своих кораблей: {self.game_stats['player_ships_destroyed']}",
            f"Время игры: {minutes} мин. {seconds} сек."
        ]
        
        for stat in stats:
            label = QLabel(stat)
            label.setStyleSheet("""
                QLabel {
                    color: white;
                    font-size: 18px;
                    padding: 5px;
                }
            """)
            stats_layout.addWidget(label)
        
        main_layout.addWidget(stats_container)
        
        # Add back button
        back_btn = QPushButton("В главное меню")
        back_btn.setStyleSheet("""
            QPushButton {
                background-color: rgba(74, 74, 74, 180);
                color: white;
                border: 2px solid #666666;
                border-radius: 5px;
                padding: 12px;
                font-size: 16px;
                min-width: 200px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: rgba(102, 102, 102, 180);
            }
        """)
        back_btn.clicked.connect(self.go_back)
        main_layout.addWidget(back_btn, alignment=Qt.AlignCenter)
        
        # Set background
        self.set_background()
        
    def set_background(self):
        try:
            background_name = "win_result_background.jpg" if self.player_won else "loss_result_background.jpg"
            background_path = os.path.join("assets", background_name)
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
    
    def go_back(self):
        from main import MainMenu
        self.main_menu = MainMenu()
        self.main_menu.show()
        self.close() 