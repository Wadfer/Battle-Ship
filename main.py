import sys
import os
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import QResource

# Добавляем путь к src в PYTHONPATH
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from src.game_window import GameWindow

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = GameWindow()
    window.show()
    sys.exit(app.exec_())
    