"""
Модуль игрового экрана игры "Морской бой"

Этот модуль содержит:
- Основной игровой интерфейс с двумя полями (игрок и компьютер)
- Логику игры и обработку выстрелов
- Искусственный интеллект для компьютера
- Отслеживание статистики игры
- Переходы к экрану результатов

Автор: [Ваше имя]
Версия: 1.0
"""

# Импорт необходимых модулей для работы с GUI
from PyQt5.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                           QPushButton, QLabel, QGridLayout, QMessageBox)
from PyQt5.QtCore import Qt, QSize, QTimer  # Для таймеров и констант Qt
from PyQt5.QtGui import QPixmap, QPalette, QBrush  # Для работы с изображениями
import os  # Для работы с файловой системой
import random  # Для генерации случайных чисел (ИИ компьютера)
from datetime import datetime  # Для отслеживания времени игры
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

class GameScreen(QMainWindow):
    """
    Класс игрового экрана игры "Морской бой"
    
    Наследуется от QMainWindow и предоставляет:
    - Два игровых поля (игрок и компьютер)
    - Логику обработки выстрелов
    - Искусственный интеллект для компьютера
    - Отслеживание статистики игры
    - Переходы к экрану результатов
    """
    
    def __init__(self, player_ships):
        """
        Конструктор игрового экрана
        
        Args:
            player_ships (list): Список кораблей игрока в формате [(row, col, size, is_horizontal), ...]
        """
        super().__init__()  # Вызов конструктора родительского класса
        
        # Инициализация данных игры
        self.player_ships = player_ships  # Корабли игрока, переданные с экрана расстановки
        self.player_board = [[0 for _ in range(10)] for _ in range(10)]  # Игровое поле игрока (10x10)
        self.computer_board = [[0 for _ in range(10)] for _ in range(10)]  # Игровое поле компьютера (10x10)
        self.computer_ships = []  # Список кораблей компьютера
        self.player_turn = True  # Флаг, чей сейчас ход (True - игрок, False - компьютер)
        
        # Статистика игры
        self.game_stats = {
            'shots': 0,  # Общее количество выстрелов
            'hits': 0,  # Количество попаданий
            'start_time': datetime.now(),  # Время начала игры
            'player_ships_destroyed': 0,  # Количество уничтоженных кораблей игрока
            'computer_ships_destroyed': 0  # Количество уничтоженных кораблей компьютера
        }
        
        # Переменные для искусственного интеллекта компьютера
        self.last_hit = None  # Последняя клетка, в которую попал компьютер
        self.hunting_mode = False  # Режим "охоты" - когда компьютер ищет остальную часть корабля
        self.hit_direction = None  # Направление, в котором компьютер продолжает стрелять
        self.possible_targets = []  # Список возможных целей для компьютера
        
        # Таймер для задержки выстрела ИИ (создает эффект "размышления")
        self.shot_timer = QTimer()
        self.shot_timer.setSingleShot(True)  # Таймер срабатывает только один раз
        self.shot_timer.timeout.connect(self.make_computer_shot)  # Подключение обработчика выстрела ИИ
        
        # Инициализация интерфейса и размещение кораблей
        self.initUI()  # Создание пользовательского интерфейса
        self.place_computer_ships()  # Размещение кораблей компьютера
        self.place_player_ships()  # Размещение кораблей игрока
        
    def initUI(self):
        """
        Создание и настройка пользовательского интерфейса игрового экрана
        
        Создает:
        - Два игровых поля (игрок и компьютер)
        - Подписи для полей и координат
        - Кнопки управления
        - Фоновое изображение
        """
        # Настройка основных свойств окна
        self.setWindowTitle('Морской бой - Игра')  # Заголовок окна
        self.setFixedSize(1200, 700)  # Фиксированный размер окна
        
        # Создание центрального виджета
        central_widget = QWidget()  # Центральный контейнер
        self.setCentralWidget(central_widget)  # Установка центрального виджета

        # Создание основного вертикального макета
        outer_layout = QVBoxLayout(central_widget)  # Внешний вертикальный макет
        outer_layout.setContentsMargins(20, 20, 20, 20)  # Отступы от краев
        outer_layout.setSpacing(0)  # Расстояние между элементами

        # Создание горизонтального макета для игровых полей
        main_layout = QHBoxLayout()  # Горизонтальный макет для размещения полей рядом
        main_layout.setAlignment(Qt.AlignCenter)  # Выравнивание по центру

        # --- Игровые доски ---
        player_board_widget = QWidget()
        player_layout = QVBoxLayout(player_board_widget)
        player_layout.setSpacing(20)
        
        # Добави название игрового поля игрока
        player_title = QLabel("Ваше поле")
        player_title.setAlignment(Qt.AlignCenter)
        player_title.setStyleSheet("""
            QLabel {
                color: #ffffff;
                font-size: 24px;
                font-weight: bold;
                text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.8);
                padding: 10px;
            }
        """)
        player_layout.addWidget(player_title)
        
        # Создайте сетку игроков
        player_grid = QGridLayout()
        player_grid.setSpacing(1)
        
        # Добавить метки столбцов (A-K)
        for i, letter in enumerate('АБВГДЕЖЗИК'):
            label = QLabel(letter)
            label.setAlignment(Qt.AlignCenter)
            label.setStyleSheet("""
                QLabel {
                    color: #ffffff;
                    font-weight: bold;
                    font-size: 16px;
                    padding: 5px;
                    text-shadow: 1px 1px 2px rgba(0, 0, 0, 0.8);
                }
            """)
            player_grid.addWidget(label, 0, i + 1)
        
        # Добавить метки строк (1-10)
        for i in range(1, 11):
            label = QLabel(str(i))
            label.setAlignment(Qt.AlignCenter)
            label.setStyleSheet("""
                QLabel {
                    color: #ffffff;
                    font-weight: bold;
                    font-size: 16px;
                    padding: 5px;
                    text-shadow: 1px 1px 2px rgba(0, 0, 0, 0.8);
                }
            """)
            player_grid.addWidget(label, i, 0)
        
        # Создавайте ячейки для игроков
        self.player_cells = {}
        for row in range(1, 11):
            for col in range(1, 11):
                cell = QPushButton()
                cell.setFixedSize(40, 40)
                cell.setStyleSheet("""
                    QPushButton {
                        background-color: rgba(255, 255, 255, 30);
                        border: 1px solid rgba(255, 255, 255, 50);
                    }
                    QPushButton:hover {
                        background-color: rgba(255, 255, 255, 50);
                    }
                """)
                player_grid.addWidget(cell, row, col)
                self.player_cells[(row, col)] = cell
        
        player_layout.addLayout(player_grid)
        
        # Создайте плату компьютера
        computer_board_widget = QWidget()
        computer_layout = QVBoxLayout(computer_board_widget)
        
        # Добавить название игрового поля компьютера
        computer_title = QLabel("Поле противника")
        computer_title.setAlignment(Qt.AlignCenter)
        computer_title.setStyleSheet("""
            QLabel {
                color: #ffffff;
                font-size: 24px;
                font-weight: bold;
                text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.8);
                padding: 10px;
            }
        """)
        computer_layout.addWidget(computer_title)
        
        # Создайте сетку компьютера
        computer_grid = QGridLayout()
        computer_grid.setSpacing(1)
        
        # Добавить метки столбцов (A-K)
        for i, letter in enumerate('АБВГДЕЖЗИК'):
            label = QLabel(letter)
            label.setAlignment(Qt.AlignCenter)
            label.setStyleSheet("""
                QLabel {
                    color: #ffffff;
                    font-weight: bold;
                    font-size: 16px;
                    padding: 5px;
                    text-shadow: 1px 1px 2px rgba(0, 0, 0, 0.8);
                }
            """)
            computer_grid.addWidget(label, 0, i + 1)
        
        # Добавить метки строк (1-10)
        for i in range(1, 11):
            label = QLabel(str(i))
            label.setAlignment(Qt.AlignCenter)
            label.setStyleSheet("""
                QLabel {
                    color: #ffffff;
                    font-weight: bold;
                    font-size: 16px;
                    padding: 5px;
                    text-shadow: 1px 1px 2px rgba(0, 0, 0, 0.8);
                }
            """)
            computer_grid.addWidget(label, i, 0)
        
        # Создайте ячейки компьютера
        self.computer_cells = {}
        for row in range(1, 11):
            for col in range(1, 11):
                cell = QPushButton()
                cell.setFixedSize(40, 40)
                cell.setStyleSheet("""
                    QPushButton {
                        background-color: rgba(255, 255, 255, 30);
                        border: 1px solid rgba(255, 255, 255, 50);
                    }
                    QPushButton:hover {
                        background-color: rgba(255, 255, 255, 50);
                    }
                """)
                cell.clicked.connect(lambda checked, r=row, c=col: self.make_shot(r, c))
                computer_grid.addWidget(cell, row, col)
                self.computer_cells[(row, col)] = cell
        
        computer_layout.addLayout(computer_grid)
        
        main_layout.addWidget(player_board_widget)
        main_layout.addWidget(computer_board_widget)
        outer_layout.addLayout(main_layout)
        outer_layout.addStretch()

        # Кнопка "Главное меню" в левом нижнем углу
        menu_btn = QPushButton('Главное меню')
        menu_btn.setStyleSheet('''
            QPushButton {
                background-color: #4a4a4a;
                color: white;
                border: 2px solid #666666;
                border-radius: 5px;
                padding: 10px 30px;
                font-size: 16px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #666666;
            }
        ''')
        menu_btn.setFixedWidth(180)
        menu_btn.clicked.connect(self.go_to_main_menu)
        bottom_layout = QHBoxLayout()
        bottom_layout.addWidget(menu_btn)
        bottom_layout.addStretch()
        outer_layout.addLayout(bottom_layout)

        self.set_background()
        
    def place_computer_ships(self):
        """
        Размещение кораблей компьютера на скрытом поле
        
        Автоматически размещает корабли компьютера согласно правилам:
        - 1 корабль на 4 клетки
        - 2 корабля на 3 клетки  
        - 3 корабля на 2 клетки
        - 4 корабля на 1 клетку
        
        Корабли размещаются случайным образом с соблюдением правил:
        - Не соприкасаются друг с другом
        - Не выходят за границы поля
        """
        # Определение количества кораблей каждого размера
        ships = [(4, 1), (3, 2), (2, 3), (1, 4)]  # (размер, количество)
        
        # Размещение кораблей каждого типа
        for size, count in ships:
            for _ in range(count):  # Для каждого корабля данного размера
                while True:  # Бесконечный цикл до успешного размещения
                    # Генерация случайной позиции и ориентации
                    row = random.randint(0, 9)  # Случайная строка (0-9)
                    col = random.randint(0, 9)  # Случайный столбец (0-9)
                    is_horizontal = random.choice([True, False])  # Случайная ориентация
                    
                    # Проверка возможности размещения корабля
                    if self.can_place_ship(self.computer_board, row, col, size, is_horizontal):
                        # Размещение корабля на игровом поле (но не отображаем визуально)
                        if is_horizontal:  # Горизонтальное размещение
                            for i in range(size):
                                self.computer_board[row][col + i] = 1  # Отметка клеток корабля
                        else:  # Вертикальное размещение
                            for i in range(size):
                                self.computer_board[row + i][col] = 1  # Отметка клеток корабля
                        
                        # Сохранение информации о корабле
                        self.computer_ships.append((row, col, size, is_horizontal))
                        break  # Выход из цикла при успешном размещении
    
    def place_player_ships(self):
        """Размещение кораблей игрока на видимом поле"""
        for start_pos, size, is_horizontal in self.player_ships:
            row, col = start_pos
            row -= 1  # Преобразование в индексацию на основе 0
            col -= 1
            self.place_ship(self.player_board, row, col, size, is_horizontal)
            # Отобразить корабль на поле игрока
            for i in range(size):
                if is_horizontal:
                    pos = (row + 1, col + i + 1)
                else:
                    pos = (row + i + 1, col + 1)
                self.player_cells[pos].setStyleSheet("""
                    QPushButton {
                        background-color: #D2B48C;
                        border: 2px solid #8B4513;
                    }
                """)
    
    def can_place_ship(self, board, row, col, size, is_horizontal):
        """Проверка возможности размещения корабля на поле"""
        if is_horizontal:
            if col + size > 10:
                return False
            for i in range(size):
                if not self.is_valid_placement(board, row, col + i):
                    return False
        else:
            if row + size > 10:
                return False
            for i in range(size):
                if not self.is_valid_placement(board, row + i, col):
                    return False
        return True
    
    def is_valid_placement(self, board, row, col):
        """Проверка валидности клетки для размещения корабля"""
        # Проверка, пуста ли клетка и ее окружение
        for r in range(max(0, row - 1), min(10, row + 2)):
            for c in range(max(0, col - 1), min(10, col + 2)):
                if board[r][c] != 0:
                    return False
        return True
    
    def place_ship(self, board, row, col, size, is_horizontal):
        """Фактическое размещение корабля на поле"""
        if is_horizontal:
            for i in range(size):
                board[row][col + i] = 1
                # Отображаем корабль только на поле игрока
                if board == self.player_board:
                    cell = self.player_cells[(row + 1, col + i + 1)]
                    cell.setStyleSheet("""
                        QPushButton {
                            background-color: #D2B48C;
                            border: 2px solid #8B4513;
                        }
                    """)
        else:
            for i in range(size):
                board[row + i][col] = 1
                # Отображаем корабль только на поле игрока
                if board == self.player_board:
                    cell = self.player_cells[(row + i + 1, col + 1)]
                    cell.setStyleSheet("""
                        QPushButton {
                            background-color: #D2B48C;
                            border: 2px solid #8B4513;
                        }
                    """)
    
    def make_shot(self, row, col):
        """
        Обработка выстрела игрока по полю противника
        
        Args:
            row (int): Номер строки (1-10)
            col (int): Номер столбца (1-10)
            
        Логика:
        1. Проверяет, ход ли игрока
        2. Проверяет, не стрелял ли уже в эту клетку
        3. Обрабатывает попадание или промах
        4. Обновляет статистику
        5. Проверяет условия победы
        6. Передает ход компьютеру при промахе
        """
        # Проверка, что сейчас ход игрока
        if not self.player_turn:
            return  # Игнорируем выстрел, если не ход игрока
            
        # Преобразование координат из пользовательских (1-10) в программные (0-9)
        row -= 1
        col -= 1
        
        # Проверка, не стрелял ли уже в эту клетку
        if self.computer_board[row][col] in [2, 3]:  # 2 = промах, 3 = попадание
            return  # Игнорируем повторный выстрел в ту же клетку
            
        # Обновление статистики - увеличение счетчика выстрелов
        self.game_stats['shots'] += 1
            
        # Обработка результата выстрела
        if self.computer_board[row][col] == 1:  # Попадание в корабль
            self.computer_board[row][col] = 3  # Отметка клетки как "попадание"
            
            # Визуальное отображение попадания (красная клетка)
            self.computer_cells[(row + 1, col + 1)].setStyleSheet("""
                QPushButton {
                    background-color: #f44336;  /* Красный фон */
                    border: 1px solid #d32f2f;  /* Темно-красная рамка */
                }
            """)
            
            # Увеличение счетчика попаданий
            self.game_stats['hits'] += 1
            
            # Проверка, полностью ли уничтожен корабль
            if self.is_ship_destroyed(self.computer_board, row, col):
                self.game_stats['computer_ships_destroyed'] += 1  # Увеличение счетчика уничтоженных кораблей
                self.mark_surrounding_cells(row, col)  # Отметка клеток вокруг уничтоженного корабля
                
            # Проверка условия победы игрока
            if self.check_winner(self.computer_board):
                self.show_result(True)  # Показ экрана победы
                return
        else:  # Промах
            self.computer_board[row][col] = 2  # Отметка клетки как "промах"
            
            # Визуальное отображение промаха (белая клетка)
            self.computer_cells[(row + 1, col + 1)].setStyleSheet("""
                QPushButton {
                    background-color: white;  /* Белый фон */
                    border: 1px solid #bdbdbd;  /* Серая рамка */
                }
            """)
            
            # Передача хода компьютеру
            self.player_turn = False
            self.computer_turn()  # Запуск хода компьютера
    
    def is_ship_destroyed(self, board, row, col):
        """Проверка, уничтожен ли корабль полностью"""
        # Найти клетки корабля
        ship_cells = []
        # Проверка горизонтали
        c = col
        while c >= 0 and board[row][c] in [1, 3]:
            ship_cells.append((row, c))
            c -= 1
        c = col + 1
        while c < 10 and board[row][c] in [1, 3]:
            ship_cells.append((row, c))
            c += 1
        # Проверка вертикали
        r = row
        while r >= 0 and board[r][col] in [1, 3]:
            ship_cells.append((r, col))
            r -= 1
        r = row + 1
        while r < 10 and board[r][col] in [1, 3]:
            ship_cells.append((r, col))
            r += 1
            
        # Проверка, все ли клетки уничтожены
        return all(board[r][c] == 3 for r, c in ship_cells)
    
    def mark_surrounding_cells(self, row, col):
        """Отметить клетки вокруг уничтоженного корабля"""
        # Найти клетки корабля
        ship_cells = []
        # Проверка горизонтали
        c = col
        while c >= 0 and self.computer_board[row][c] in [1, 3]:
            ship_cells.append((row, c))
            c -= 1
        c = col + 1
        while c < 10 and self.computer_board[row][c] in [1, 3]:
            ship_cells.append((row, c))
            c += 1
        # Проверка вертикали
        r = row
        while r >= 0 and self.computer_board[r][col] in [1, 3]:
            ship_cells.append((r, col))
            r -= 1
        r = row + 1
        while r < 10 and self.computer_board[r][col] in [1, 3]:
            ship_cells.append((r, col))
            r += 1
            
        # Отметить окружающие клетки
        for r, c in ship_cells:
            for dr in [-1, 0, 1]:
                for dc in [-1, 0, 1]:
                    nr, nc = r + dr, c + dc
                    if 0 <= nr < 10 and 0 <= nc < 10 and self.computer_board[nr][nc] == 0:
                        self.computer_board[nr][nc] = 2
                        self.computer_cells[(nr + 1, nc + 1)].setStyleSheet("""
                            QPushButton {
                                background-color: #9e9e9e;
                                border: 1px solid #757575;
                            }
                        """)
    
    def computer_turn(self):
        """Запуск таймера для выстрела ИИ"""
        # Запуск таймера для задержанного выстрела
        self.shot_timer.start(500)  # 0.5 секунда задержки
    
    def make_computer_shot(self):
        """Логика выстрела ИИ"""
        if not self.player_turn:  # Дополнительная проверка для предотвращения множественных выстрелов
            if self.hunting_mode:
                # Если есть попадание, попробуйте найти остальную часть корабля
                if self.last_hit:
                    row, col = self.last_hit
                    if self.hit_direction is None:
                        # Попробуйте все четыре направления
                        directions = [(0, 1), (1, 0), (0, -1), (-1, 0)]
                        random.shuffle(directions)
                        for dr, dc in directions:
                            new_row, new_col = row + dr, col + dc
                            if (0 <= new_row < 10 and 0 <= new_col < 10 and 
                                self.player_board[new_row][new_col] not in [2, 3]):
                                self.hit_direction = (dr, dc)
                                self.fire_shot(new_row, new_col)
                                return
                    else:
                        # Продолжайте в том же направлении
                        dr, dc = self.hit_direction
                        new_row, new_col = row + dr, col + dc
                        if (0 <= new_row < 10 and 0 <= new_col < 10 and 
                            self.player_board[new_row][new_col] not in [2, 3]):
                            self.fire_shot(new_row, new_col)
                            return
                        else:
                            # Если мы попали в край или промах, попробуйте противоположное направление
                            dr, dc = -dr, -dc
                            new_row, new_col = self.last_hit[0] + dr, self.last_hit[1] + dc
                            if (0 <= new_row < 10 and 0 <= new_col < 10 and 
                                self.player_board[new_row][new_col] not in [2, 3]):
                                self.hit_direction = (dr, dc)
                                self.fire_shot(new_row, new_col)
                                return
                            else:
                                # Если оба направления заблокированы, сбросьте режим охоты
                                self.hunting_mode = False
                                self.last_hit = None
                                self.hit_direction = None
            
            # Если не в режиме охоты, используйте вероятностное прицеливание
            if not self.hunting_mode:
                # Создайте карту вероятностей
                probability_map = [[0 for _ in range(10)] for _ in range(10)]
                
                # Отметить уже выстреленные клетки как -1
                for r in range(10):
                    for c in range(10):
                        if self.player_board[r][c] in [2, 3]:
                            probability_map[r][c] = -1
                
                # Рассчитайте вероятности на основе правил размещения кораблей
                for r in range(10):
                    for c in range(10):
                        if probability_map[r][c] != -1:
                            # Проверка горизонтальных и вертикальных возможностей
                            for size in range(1, 5):  # Размеры кораблей от 1 до 4
                                # Горизонталь
                                if c + size <= 10:
                                    valid = True
                                    for i in range(size):
                                        if probability_map[r][c + i] == -1:
                                            valid = False
                                            break
                                    if valid:
                                        for i in range(size):
                                            probability_map[r][c + i] += 1
                                
                                # Вертикаль
                                if r + size <= 10:
                                    valid = True
                                    for i in range(size):
                                        if probability_map[r + i][c] == -1:
                                            valid = False
                                            break
                                    if valid:
                                        for i in range(size):
                                            probability_map[r + i][c] += 1
                
                # Найти клетки с наивысшей вероятностью
                max_prob = 0
                best_cells = []
                for r in range(10):
                    for c in range(10):
                        if probability_map[r][c] > max_prob:
                            max_prob = probability_map[r][c]
                            best_cells = [(r, c)]
                        elif probability_map[r][c] == max_prob:
                            best_cells.append((r, c))
                
                if best_cells:
                    row, col = random.choice(best_cells)
                    self.fire_shot(row, col)
                    return
            
            # Если все остальное не удается, сделайте случайный выстрел
            while True:
                row = random.randint(0, 9)
                col = random.randint(0, 9)
                if self.player_board[row][col] not in [2, 3]:
                    self.fire_shot(row, col)
                    break
    
    def fire_shot(self, row, col):
        """Обработка выстрела ИИ по полю игрока"""
        if self.player_board[row][col] == 1:  # Hit
            self.player_board[row][col] = 3
            self.player_cells[(row + 1, col + 1)].setStyleSheet("""
                QPushButton {
                    background-color: #f44336;
                    border: 1px solid #d32f2f;
                }
            """)
            
            # Обновление целей ИИ
            self.hunting_mode = True
            self.last_hit = (row, col)
            
            # Проверка, уничтожен ли корабль
            if self.is_ship_destroyed(self.player_board, row, col):
                self.game_stats['player_ships_destroyed'] += 1
                self.mark_surrounding_cells_player(row, col)
                # Сбросьте режим охоты, когда корабль уничтожен
                self.hunting_mode = False
                self.last_hit = None
                self.hit_direction = None
                
            # Проверка, уничтожены ли все корабли
            if self.check_winner(self.player_board):
                self.show_result(False)
                return
                
            # Продолжайте ход ИИ после попадания
            self.computer_turn()
            
        else:  # Промах
            self.player_board[row][col] = 2
            self.player_cells[(row + 1, col + 1)].setStyleSheet("""
                QPushButton {
                    background-color: white;
                    border: 1px solid #bdbdbd;
                }
            """)
            # Если мы в режиме охоты и промахнулись, попробуйте другое направление
            if self.hunting_mode:
                self.hit_direction = None
            # Давайте ход игроку только после промаха
            self.player_turn = True
    
    def mark_surrounding_cells_player(self, row, col):
        """Отметить клетки вокруг уничтоженного корабля игрока"""
        # Найти клетки корабля
        ship_cells = []
        # Проверка горизонтали
        c = col
        while c >= 0 and self.player_board[row][c] in [1, 3]:
            ship_cells.append((row, c))
            c -= 1
        c = col + 1
        while c < 10 and self.player_board[row][c] in [1, 3]:
            ship_cells.append((row, c))
            c += 1
        # Проверка вертикали
        r = row
        while r >= 0 and self.player_board[r][col] in [1, 3]:
            ship_cells.append((r, col))
            r -= 1
        r = row + 1
        while r < 10 and self.player_board[r][col] in [1, 3]:
            ship_cells.append((r, col))
            r += 1
            
        # Отметить окружающие клетки
        for r, c in ship_cells:
            for dr in [-1, 0, 1]:
                for dc in [-1, 0, 1]:
                    nr, nc = r + dr, c + dc
                    if 0 <= nr < 10 and 0 <= nc < 10 and self.player_board[nr][nc] == 0:
                        self.player_board[nr][nc] = 2
                        self.player_cells[(nr + 1, nc + 1)].setStyleSheet("""
                            QPushButton {
                                background-color: #9e9e9e;
                                border: 1px solid #757575;
                            }
                        """)
    
    def check_winner(self, board):
        """Проверка победы (нет оставшихся кораблей)"""
        return all(cell != 1 for row in board for cell in row)
    
    def show_result(self, player_won):
        """Показать экран результата игры"""
        from result_screen import ResultScreen
        self.result_screen = ResultScreen(player_won, self.game_stats)
        self.result_screen.show()
        self.close()
    
    def set_background(self):
        """Установка фонового изображения для экрана игры"""
        try:
            background_path = resource_path(os.path.join("assets", "Game_background.jpg"))
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
        
        # Если загрузка фонового изображения не удалась, установите градиентный фон по умолчанию
        self.setStyleSheet("""
            QMainWindow {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                          stop:0 #1a237e, stop:1 #0d47a1);
            }
        """)

    def go_to_main_menu(self):
        from main import MainMenu
        self.main_menu = MainMenu()
        self.main_menu.show()
        self.close() 