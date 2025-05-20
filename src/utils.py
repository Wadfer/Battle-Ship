import os
from pathlib import Path
from PyQt5.QtGui import QPalette, QPixmap
from PyQt5.QtWidgets import QApplication

global_palette = QPalette()

def get_image_path(filename):
    """Возвращает абсолютный путь к изображению"""
    base_path = Path(__file__).parent.parent  # Получаем путь к директории проекта
    path = base_path / 'images' / filename
    # Приводим путь к формату Windows
    return os.path.normpath(str(path))

def load_image_from_resource(path: str) -> QPixmap:
    """Загружает изображение из ресурсов"""
    pixmap = QPixmap(path)
    if not pixmap.isNull():
        global_palette.setBrush(QPalette.Window, pixmap)
    return pixmap
