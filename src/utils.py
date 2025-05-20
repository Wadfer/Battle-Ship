from pathlib import Path

def get_image_path(filename):
    """Возвращает абсолютный путь к изображению"""
    base_path = Path(__file__).parent.parent  # Получаем путь к директории проекта
    return str(base_path / "images" / filename)
