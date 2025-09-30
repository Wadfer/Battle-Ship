import sys
import os
from PyQt5.QtWidgets import (QApplication, QMainWindow, QPushButton, 
                           QVBoxLayout, QWidget, QMessageBox, QLabel)
from PyQt5.QtGui import QPixmap, QPalette, QBrush, QFont  # Для работы с изображениями и стилями
from PyQt5.QtCore import Qt  # Для констант и флагов Qt

# Импорт экрана расстановки кораблей
from ship_placement import ShipPlacementScreen

def resource_path(relative_path):
    if hasattr(sys, '_MEIPASS'):
        # Если приложение упаковано в exe, используем временную папку PyInstaller
        return os.path.join(sys._MEIPASS, relative_path)
    # Иначе используем текущую рабочую директорию
    return os.path.join(os.path.abspath('.'), relative_path)

class MainMenu(QMainWindow):
    """
    Класс главного меню игры "Морской бой"
    
    Наследуется от QMainWindow и предоставляет:
    - Интерфейс главного меню с кнопками навигации
    - Отображение фонового изображения
    - Переходы к другим экранам игры
    - Отображение правил игры
    """
    
    def __init__(self):
        """
        Конструктор главного меню
        
        Инициализирует окно главного меню и вызывает создание интерфейса
        """
        super().__init__()  # Вызов конструктора родительского класса
        self.initUI()  # Создание пользовательского интерфейса
        
    def initUI(self):
        """
        Создание и настройка пользовательского интерфейса главного меню

        Создает:
        - Заголовок игры
        - Кнопки навигации (Новая игра, Правила, Выход)
        - Стили для всех элементов
        - Фоновое изображение
        """
        # Настройка основных свойств окна
        self.setWindowTitle('Морской бой')  # Заголовок окна
        self.setFixedSize(1200, 700)  # Фиксированный размер окна
        
        # Создание центрального виджета и основного макета
        central_widget = QWidget()  # Центральный контейнер для всех элементов
        self.setCentralWidget(central_widget)  # Установка центрального виджета
        layout = QVBoxLayout(central_widget)  # Вертикальный макет для размещения элементов
        layout.setAlignment(Qt.AlignCenter)  # Выравнивание по центру
        layout.setSpacing(20)  # Расстояние между элементами
        
        # Создание заголовка игры
        title_label = QLabel('МОРСКОЙ БОЙ', self)
        title_label.setAlignment(Qt.AlignCenter)  # Выравнивание текста по центру
        # Стилизация заголовка с эффектом тени
        title_label.setStyleSheet("""
            QLabel {
                color: white;  /* Белый цвет текста */
                font-size: 48px;  /* Размер шрифта */
                font-weight: bold;  /* Жирный шрифт */
                text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.5);  /* Тень текста */
                margin-bottom: 40px;  /* Отступ снизу */
            }
        """)
        layout.addWidget(title_label)  # Добавление заголовка в макет
        
        # Создание кнопок навигации
        new_game_btn = QPushButton('Новая игра', self)  # Кнопка для начала новой игры
        rules_btn = QPushButton('Правила', self)  # Кнопка для показа правил
        exit_btn = QPushButton('Выход', self)  # Кнопка для выхода из игры
        
        # Стилизация кнопок с эффектами наведения
        button_style = """
            QPushButton {
                background-color: rgba(74, 74, 74, 180);  /* Полупрозрачный серый фон */
                color: white;  /* Белый текст */
                border: 2px solid #666666;  /* Серая рамка */
                border-radius: 5px;  /* Закругленные углы */
                padding: 15px;  /* Внутренние отступы */
                font-size: 18px;  /* Размер шрифта */
                min-width: 250px;  /* Минимальная ширина */
                font-weight: bold;  /* Жирный шрифт */
            }
            QPushButton:hover {
                background-color: rgba(102, 102, 102, 180);  /* Светлее при наведении */
            }
        """
        # Применение стилей ко всем кнопкам
        new_game_btn.setStyleSheet(button_style)
        rules_btn.setStyleSheet(button_style)
        exit_btn.setStyleSheet(button_style)
        
        # Добавление кнопок в основной макет
        layout.addWidget(new_game_btn)
        layout.addWidget(rules_btn)
        layout.addWidget(exit_btn)
        
        # Подключение обработчиков событий к кнопкам
        new_game_btn.clicked.connect(self.start_new_game)  # Обработчик для новой игры
        rules_btn.clicked.connect(self.show_rules)  # Обработчик для показа правил
        exit_btn.clicked.connect(self.close)  # Обработчик для закрытия приложения
        
        # Установка фонового изображения
        self.set_background()
        
    def set_background(self):
        """
        Установка фонового изображения для главного меню
        
        Сначала пытается загрузить изображение из папки assets,
        если это не удается, устанавливает градиентный фон по умолчанию
        """
        try:
            # Попытка загрузить фоновое изображение из папки assets
            background_path = resource_path("assets/menu_background.jpg")
            if os.path.exists(background_path):  # Проверка существования файла
                palette = QPalette()  # Создание палитры цветов
                pixmap = QPixmap(background_path)  # Загрузка изображения
                if not pixmap.isNull():  # Проверка успешной загрузки
                    # Масштабирование изображения под размер окна с сохранением пропорций
                    scaled_pixmap = pixmap.scaled(self.size(), Qt.KeepAspectRatioByExpanding, Qt.SmoothTransformation)
                    palette.setBrush(QPalette.Window, QBrush(scaled_pixmap))  # Установка фона
                    self.setPalette(palette)  # Применение палитры к окну
                    return  # Успешная установка фона
        except Exception as e:
            print(f"Error loading background: {e}")  # Вывод ошибки в консоль
        
        # Если загрузка фонового изображения не удалась, устанавливаем градиентный фон по умолчанию
        self.setStyleSheet("""
            QMainWindow {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                          stop:0 #1a237e, stop:1 #0d47a1);
            }
        """)
    
    def start_new_game(self):
        """
        Обработчик кнопки "Новая игра"
        
        Создает экран расстановки кораблей, показывает его и скрывает главное меню
        """
        self.ship_placement = ShipPlacementScreen()  # Создание экрана расстановки кораблей
        self.ship_placement.show()  # Показ экрана расстановки
        self.hide()  # Скрытие главного меню
    
    def show_rules(self):
        """
        Обработчик кнопки "Правила"
        
        Показывает диалоговое окно с правилами игры "Морской бой"
        """
        # Текст с правилами игры
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
        # Создание диалогового окна с правилами
        msg = QMessageBox(self)
        msg.setWindowTitle("Правила игры")  # Заголовок окна
        msg.setText(rules_text)  # Текст правил
        
        # Стилизация диалогового окна
        msg.setStyleSheet("""
            QMessageBox {
                background-color: #2b2b2b;  /* Темный фон */
                color: white;  /* Белый текст */
            }
            QMessageBox QLabel {
                color: white;  /* Белый цвет для текста */
                font-size: 14px;  /* Размер шрифта */
            }
            QPushButton {
                background-color: #4a4a4a;  /* Серый фон кнопок */
                color: white;  /* Белый текст кнопок */
                border: 2px solid #666666;  /* Серая рамка */
                border-radius: 5px;  /* Закругленные углы */
                padding: 5px 15px;  /* Внутренние отступы */
                min-width: 150px;  /* Минимальная ширина */
            }
            QPushButton:hover {
                background-color: #666666;  /* Светлее при наведении */
            }
        """)
        msg.exec_()  # Показ диалогового окна

def main():
    """
    Главная функция приложения
    
    Создает экземпляр QApplication, настраивает стиль,
    создает и показывает главное меню, запускает цикл обработки событий
    """
    app = QApplication(sys.argv)  # Создание объекта приложения с аргументами командной строки
    
    # Установка стиля приложения (Fusion - современный стиль Qt)
    app.setStyle('Fusion')
    
    # Создание и отображение главного меню
    menu = MainMenu()  # Создание экземпляра главного меню
    menu.show()  # Показ главного меню
    
    # Запуск основного цикла обработки событий приложения
    sys.exit(app.exec_())

if __name__ == '__main__':
    """
    Точка входа в программу
    
    Проверяет, что модуль запущен напрямую (а не импортирован),
    и вызывает главную функцию
    """
    main()