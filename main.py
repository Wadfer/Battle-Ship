import sys
from PyQt5.QtWidgets import QApplication
from src.game_window import GameWindow

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = GameWindow()
    window.show()
    sys.exit(app.exec_())