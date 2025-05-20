import sys
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import QResource
from src.game_window import GameWindow

# Загружаем ресурсы
QResource.registerResource('resources.qrc')

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = GameWindow()
    window.show()
    sys.exit(app.exec_())
    