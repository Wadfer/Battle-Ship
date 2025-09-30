"""
Модуль экрана результатов игры "Морской бой"

Этот модуль содержит:
- Отображение результата игры (победа/поражение)
- Статистику игры (выстрелы, попадания, время)
- Различные фоновые изображения для победы и поражения
- Переход обратно в главное меню

Автор: [Ваше имя]
Версия: 1.0
"""

# Импорт необходимых модулей для работы с GUI
from PyQt5.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                           QPushButton, QLabel, QGridLayout)
from PyQt5.QtCore import Qt  # Для констант и флагов Qt
from PyQt5.QtGui import QPixmap, QPalette, QBrush  # Для работы с изображениями
import os  # Для работы с файловой системой
from datetime import datetime  # Для работы с временем
import sys  # Для работы с системными параметрами

def resource_path(relative_path):
    """
    Функция для корректного определения пути к ресурсам при упаковке в исполняемый файл
    
    Args:
        relative_path (str): Относительный путь к файлу ресурса
        
    Returns:
        str: Абсолютный путь к файлу ресурса
        
    Примечание:
        При упаковке с помощью PyInstaller ресурсы упаковываются в временную папку,
        доступную через sys._MEIPASS. Эта функция проверяет, запущено ли приложение
        из упакованного exe файла или из исходного кода.
    """
    if hasattr(sys, '_MEIPASS'):
        # Если приложение упаковано в exe, используем временную папку PyInstaller
        return os.path.join(sys._MEIPASS, relative_path)
    # Иначе используем текущую рабочую директорию
    return os.path.join(os.path.abspath('.'), relative_path)

class ResultScreen(QMainWindow):
    """
    Класс экрана результатов игры
    
    Наследуется от QMainWindow и предоставляет:
    - Отображение результата игры (победа/поражение)
    - Подробную статистику игры
    - Различные фоновые изображения в зависимости от результата
    - Переход обратно в главное меню
    """
    
    def __init__(self, player_won, game_stats=None):
        """
        Конструктор экрана результатов
        
        Args:
            player_won (bool): True если игрок выиграл, False если проиграл
            game_stats (dict, optional): Словарь со статистикой игры
        """
        super().__init__()  # Вызов конструктора родительского класса
        
        # Сохранение результата игры
        self.player_won = player_won  # Результат игры
        
        # Инициализация статистики игры (используем переданную или значения по умолчанию)
        self.game_stats = game_stats or {
            'shots': 0,  # Общее количество выстрелов
            'hits': 0,  # Количество попаданий
            'start_time': datetime.now(),  # Время начала игры
            'player_ships_destroyed': 0,  # Количество уничтоженных кораблей игрока
            'computer_ships_destroyed': 0  # Количество уничтоженных кораблей компьютера
        }
        
        # Создание пользовательского интерфейса
        self.initUI()
        
    def initUI(self):
        """
        Создание и настройка пользовательского интерфейса экрана результатов
        
        Создает:
        - Заголовок с результатом игры
        - Контейнер со статистикой
        - Кнопку возврата в главное меню
        - Фоновое изображение
        """
        # Настройка основных свойств окна
        self.setWindowTitle('Морской бой - Результат')  # Заголовок окна
        self.setFixedSize(1000, 700)  # Фиксированный размер окна
        
        # Создание центрального виджета и основного макета
        central_widget = QWidget()  # Центральный контейнер
        self.setCentralWidget(central_widget)  # Установка центрального виджета
        main_layout = QVBoxLayout(central_widget)  # Вертикальный макет
        main_layout.setContentsMargins(50, 50, 50, 50)  # Отступы от краев
        main_layout.setSpacing(30)  # Расстояние между элементами
        
        # Создание заголовка с результатом игры
        result_title = QLabel("Победа!" if self.player_won else "Поражение!")
        result_title.setAlignment(Qt.AlignCenter)  # Выравнивание по центру
        
        # Стилизация заголовка с эффектом тени и полупрозрачным фоном
        result_title.setStyleSheet("""
            QLabel {
                color: #ffffff;  /* Белый цвет текста */
                font-size: 48px;  /* Размер шрифта */
                font-weight: bold;  /* Жирный шрифт */
                text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.8);  /* Тень текста */
                background-color: rgba(0, 0, 0, 0.5);  /* Полупрозрачный черный фон */
                padding: 20px;  /* Внутренние отступы */
                border-radius: 10px;  /* Закругленные углы */
            }
        """)
        main_layout.addWidget(result_title)  # Добавление заголовка в макет
        
        # Создание контейнера для статистики
        stats_container = QWidget()  # Контейнер для статистики
        stats_container.setStyleSheet("""
            QWidget {
                background-color: rgba(0, 0, 0, 0.7);  /* Полупрозрачный черный фон */
                border-radius: 10px;  /* Закругленные углы */
                padding: 20px;  /* Внутренние отступы */
            }
        """)
        stats_layout = QVBoxLayout(stats_container)  # Вертикальный макет для статистики
        stats_layout.setSpacing(15)  # Расстояние между элементами статистики
        
        # Расчет статистических данных
        total_shots = self.game_stats['shots']  # Общее количество выстрелов
        hits = self.game_stats['hits']  # Количество попаданий
        hit_percentage = (hits / total_shots * 100) if total_shots > 0 else 0  # Процент попаданий
        game_duration = datetime.now() - self.game_stats['start_time']  # Продолжительность игры
        minutes = game_duration.seconds // 60  # Минуты игры
        seconds = game_duration.seconds % 60  # Секунды игры
        
        # Создание списка статистических данных для отображения
        stats = [
            f"Всего выстрелов: {total_shots}",  # Общее количество выстрелов
            f"Попаданий: {hits}",  # Количество попаданий
            f"Процент попаданий: {hit_percentage:.1f}%",  # Процент попаданий
            f"Уничтожено кораблей противника: {self.game_stats['computer_ships_destroyed']}",  # Уничтоженные корабли противника
            f"Потеряно своих кораблей: {self.game_stats['player_ships_destroyed']}",  # Потерянные корабли игрока
            f"Время игры: {minutes} мин. {seconds} сек."  # Продолжительность игры
        ]
        
        # Создание и добавление меток статистики
        for stat in stats:
            label = QLabel(stat)  # Создание метки с текстом статистики
            label.setStyleSheet("""
                QLabel {
                    color: white;  /* Белый цвет текста */
                    font-size: 18px;  /* Размер шрифта */
                    padding: 5px;  /* Внутренние отступы */
                }
            """)
            stats_layout.addWidget(label)  # Добавление метки в макет статистики
        
        main_layout.addWidget(stats_container)  # Добавление контейнера статистики в основной макет
        
        # Создание кнопки возврата в главное меню
        back_btn = QPushButton("В главное меню")
        back_btn.setStyleSheet("""
            QPushButton {
                background-color: rgba(74, 74, 74, 180);  /* Полупрозрачный серый фон */
                color: white;  /* Белый текст */
                border: 2px solid #666666;  /* Серая рамка */
                border-radius: 5px;  /* Закругленные углы */
                padding: 12px;  /* Внутренние отступы */
                font-size: 16px;  /* Размер шрифта */
                min-width: 200px;  /* Минимальная ширина */
                font-weight: bold;  /* Жирный шрифт */
            }
            QPushButton:hover {
                background-color: rgba(102, 102, 102, 180);  /* Светлее при наведении */
            }
        """)
        back_btn.clicked.connect(self.go_back)  # Подключение обработчика нажатия
        main_layout.addWidget(back_btn, alignment=Qt.AlignCenter)  # Добавление кнопки по центру
        
        # Установка фонового изображения
        self.set_background()
        
    def set_background(self):
        """
        Установка фонового изображения для экрана результата
        
        Выбирает фоновое изображение в зависимости от результата игры:
        - win_result_background.jpg для победы
        - loss_result_background.jpg для поражения
        
        Если загрузка изображения не удается, устанавливает градиентный фон по умолчанию
        """
        try:
            # Выбор фонового изображения в зависимости от результата
            background_name = "win_result_background.jpg" if self.player_won else "loss_result_background.jpg"
            background_path = resource_path(os.path.join("assets", background_name))
            
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
    
    def go_back(self):
        """
        Обработчик кнопки "В главное меню"
        
        Создает новое главное меню, показывает его и закрывает экран результатов
        """
        from main import MainMenu  # Импорт класса главного меню
        self.main_menu = MainMenu()  # Создание экземпляра главного меню
        self.main_menu.show()  # Показ главного меню
        self.close()  # Закрытие экрана результатов 