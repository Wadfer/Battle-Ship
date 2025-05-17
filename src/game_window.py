import sys
import os

# Добавляем директорию проекта в sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                           QPushButton, QLabel, QGridLayout, 
                           QStackedWidget, QHBoxLayout, QGroupBox, QRadioButton, QButtonGroup)
from PyQt5.QtCore import Qt, QTimer, QSize
from PyQt5.QtGui import QFont, QColor, QPalette, QIcon, QPixmap, QPainter, QBrush, QPen

from src.game_logic import GameLogic, CellState, Ship
from src.menu_widget import MenuWidget
from src.result_widget import ResultWidget
import random

class ShipButton(QPushButton):
    def __init__(self, size, parent=None):
        super().__init__(parent)
        self.size = size
        self.setFixedSize(QSize(120, 40))
        self.setCheckable(True)
        self.placed = False
        self.count = 0
        self.max_count = 0

    def paintEvent(self, event):
        super().paintEvent(event)
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        # Рисуем корабль
        cell_size = 20
        start_x = 10
        y = 10

        # Устанавливаем цвет в зависимости от состояния
        if self.placed:
            painter.setBrush(QBrush(QColor("#e0e0e0")))  # Светло-серый для размещенных
        else:
            painter.setBrush(QBrush(QColor("#808080")))  # Серый для неразмещенных

        painter.setPen(QPen(Qt.black, 1))
        
        # Рисуем корабль горизонтально
        for i in range(self.size):
            painter.drawRect(start_x + i * cell_size, y, cell_size - 2, cell_size - 2)

        # Рисуем счетчик
        painter.setPen(QPen(Qt.black))
        painter.drawText(start_x + self.size * cell_size + 5, y + 15, 
                        f"{self.count}/{self.max_count}")

    def setPlaced(self, placed):
        self.placed = placed
        self.setEnabled(not placed)  # Блокируем кнопку, если все корабли размещены
        if placed:
            self.setChecked(False)  # Снимаем выделение с заблокированной кнопки
        self.update()

class ShipButton(QPushButton):
    def __init__(self, size, parent=None):
        super().__init__(parent)
        self.size = size
        self.setFixedSize(QSize(120, 40))
        self.setCheckable(True)
        self.placed = False
        self.count = 0
        self.max_count = 0

    def paintEvent(self, event):
        super().paintEvent(event)
        painter = QPainter(self)
        
        # Рисуем корабль
        rect = self.rect()
        rect.adjust(10, 10, -10, -10)  # Добавляем отступы
        
        # Рисуем прямоугольник
        painter.setBrush(QBrush(QColor(135, 206, 235)))  # Светло-голубой цвет
        painter.setPen(QPen(Qt.black, 2))
        painter.drawRect(rect)
        
        # Рисуем количество кораблей
        font = painter.font()
        font.setPointSize(10)
        painter.setFont(font)
        painter.drawText(rect, Qt.AlignCenter, f"{self.count}/{self.max_count}")

    def setPlaced(self, placed):
        self.placed = placed
        self.update()

class GameWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.game_logic = GameLogic()
        self.init_ui()
        self.selected_ship_size = 4  # По умолчанию выбран самый большой корабль

    def init_ui(self):
        self.setWindowTitle('Морской бой')
        self.setMinimumSize(1000, 600)

        # Create central widget and main layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)

        # Create stacked widget for different screens
        self.stacked_widget = QStackedWidget()
        main_layout.addWidget(self.stacked_widget)

        # Create menu screen
        self.menu_widget = MenuWidget()
        self.menu_widget.set_button_actions(self.show_ship_setup, self.close)
        self.stacked_widget.addWidget(self.menu_widget)

        # Create ship setup screen
        self.ship_setup_widget = QWidget()
        self.init_ship_setup_ui()
        self.stacked_widget.addWidget(self.ship_setup_widget)

        # Create game screen
        self.game_widget = QWidget()
        self.init_game_ui()
        self.stacked_widget.addWidget(self.game_widget)

        # Start with menu screen
        self.stacked_widget.setCurrentWidget(self.menu_widget)

    def init_ship_setup_ui(self):
        layout = QHBoxLayout(self.ship_setup_widget)

        # Left side - Game board
        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)

        # Ship info label
        self.ship_info_label = QLabel()
        self.ship_info_label.setAlignment(Qt.AlignCenter)
        left_layout.addWidget(self.ship_info_label)

        # Orientation info label
        self.orientation_label = QLabel("Нажмите 'R' для поворота корабля")
        self.orientation_label.setAlignment(Qt.AlignCenter)
        left_layout.addWidget(self.orientation_label)

        # Game board
        board_widget = QWidget()
        board_layout = QVBoxLayout(board_widget)
        board_label = QLabel("Ваше поле")
        board_label.setAlignment(Qt.AlignCenter)
        board_layout.addWidget(board_label)
        
        self.setup_grid = QGridLayout()
        self.setup_buttons = []
        for i in range(10):
            row = []
            for j in range(10):
                button = QPushButton()
                button.setFixedSize(QSize(40, 40))
                button.clicked.connect(lambda checked, x=i, y=j: self.on_setup_board_click(x, y))
                self.setup_grid.addWidget(button, i, j)
                row.append(button)
            self.setup_buttons.append(row)
        board_layout.addLayout(self.setup_grid)
        left_layout.addWidget(board_widget)

        # Кнопка "Назад"
        back_button = QPushButton("Назад")
        back_button.setFixedSize(100, 30)
        back_button.setStyleSheet("""
            QPushButton {
                background-color: #f44336;
                color: white;
                border: none;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #da190b;
            }
        """)
        back_button.clicked.connect(lambda: self.stacked_widget.setCurrentWidget(self.menu_widget))
        left_layout.addWidget(back_button, alignment=Qt.AlignBottom)
        
        layout.addWidget(left_widget)

        # Right side - Control panel
        right_widget = QWidget()
        right_layout = QVBoxLayout(right_widget)

        # Ship selection group
        ship_group = QGroupBox("Корабли")
        ship_layout = QVBoxLayout()
        
        # Create ship selection buttons
        self.ship_buttons = {}
        ship_sizes = [4, 3, 3, 2, 2, 2, 1, 1, 1, 1]
        for size in sorted(set(ship_sizes), reverse=True):
            count = ship_sizes.count(size)
            button = ShipButton(size)
            button.max_count = count
            button.clicked.connect(lambda checked, s=size: self.select_ship(s))
            if size == 4:  # Select the largest ship by default
                button.setChecked(True)
            self.ship_buttons[size] = button
            ship_layout.addWidget(button)
        
        ship_group.setLayout(ship_layout)
        right_layout.addWidget(ship_group)

        # Control buttons
        control_group = QGroupBox("Управление")
        control_layout = QVBoxLayout()
        
        start_button = QPushButton("Начать игру")
        start_button.clicked.connect(self.on_setup_done_clicked)
        start_button.setEnabled(False)
        self.done_button = start_button
        
        random_button = QPushButton("Случайно")
        random_button.clicked.connect(self.randomize_ships)
        
        clear_button = QPushButton("Очистить")
        clear_button.clicked.connect(self.clear_board)
        
        control_layout.addWidget(start_button)
        control_layout.addWidget(random_button)
        control_layout.addWidget(clear_button)
        control_group.setLayout(control_layout)
        right_layout.addWidget(control_group)
        
        # Add stretch to push everything to the top
        right_layout.addStretch()
        layout.addWidget(right_widget)

        self.current_ship_index = 0
        self.ships = ship_sizes
        self.is_horizontal = True
        self.update_ship_info()

    def update_ship_counts(self):
        # Подсчитываем количество размещенных кораблей каждого размера
        placed_ships = {}
        for ship in self.game_logic.player_ships:
            placed_ships[ship.size] = placed_ships.get(ship.size, 0) + 1

        # Обновляем состояние кнопок
        for size, button in self.ship_buttons.items():
            button.count = placed_ships.get(size, 0)
            button.setPlaced(button.count == button.max_count)

        # Если текущий выбранный корабль заблокирован, выбираем первый доступный
        if self.ship_buttons[self.selected_ship_size].placed:
            for size, button in self.ship_buttons.items():
                if not button.placed:
                    self.select_ship(size)
                    break

    def select_ship(self, size: int):
        if not self.ship_buttons[size].placed:  # Проверяем, не заблокирован ли корабль
            self.selected_ship_size = size
            for s, button in self.ship_buttons.items():
                button.setChecked(s == size and not button.placed)

    def randomize_ships(self):
        # Clear current board
        self.clear_board()
        
        # Place ships randomly
        ships = self.ships.copy()
        random.shuffle(ships)
        
        for ship_size in ships:
            ship = Ship(ship_size)
            while True:
                x = random.randint(0, 9)
                y = random.randint(0, 9)
                is_horizontal = random.choice([True, False])
                if self.game_logic.place_ship(self.game_logic.player_board, ship, (x, y), is_horizontal):
                    self.game_logic.player_ships.append(ship)
                    break
        
        self.current_ship_index = len(self.ships)
        self.update_setup_board_display()
        self.update_ship_info()
        self.update_ship_counts()  # Обновляем счетчики кораблей

    def clear_board(self):
        # Clear the board
        self.game_logic.player_board = [[CellState.EMPTY for _ in range(10)] for _ in range(10)]
        self.game_logic.player_ships = []
        self.current_ship_index = 0
        self.update_setup_board_display()
        self.update_ship_info()
        self.update_ship_counts()  # Обновляем счетчики кораблей
        self.done_button.setEnabled(False)

    def set_orientation(self, horizontal: bool):
        self.is_horizontal = horizontal
        self.orientation_label.setText(
            "Горизонтально" if self.is_horizontal else "Вертикально"
        )

    def update_ship_info(self):
        if self.current_ship_index < len(self.ships):
            remaining_ships = self.ships[self.current_ship_index:]
            ship_counts = {}
            for size in remaining_ships:
                ship_counts[size] = ship_counts.get(size, 0) + 1
            
            info_text = "Осталось разместить:\n"
            for size, count in sorted(ship_counts.items(), reverse=True):
                info_text += f"Корабль {size}x1: {count} шт.\n"
            self.ship_info_label.setText(info_text)
        else:
            self.ship_info_label.setText("Все корабли размещены!")
            self.done_button.setEnabled(True)

    def update_setup_board_display(self):
        for i in range(10):
            for j in range(10):
                state = self.game_logic.player_board[i][j]
                if state == CellState.EMPTY:
                    self.setup_buttons[i][j].setStyleSheet("background-color: white;")
                elif state == CellState.SHIP:
                    self.setup_buttons[i][j].setStyleSheet("background-color: gray;")

    def show_invalid_placement(self, x: int, y: int):
        self.setup_buttons[x][y].setStyleSheet("background-color: #ffcccc;")
        QTimer.singleShot(500, lambda: self.update_setup_board_display())

    def on_setup_board_click(self, x: int, y: int):
        if self.current_ship_index >= len(self.ships):
            return

        ship = Ship(self.selected_ship_size)
        if self.game_logic.place_ship(self.game_logic.player_board, ship, (x, y), self.is_horizontal):
            self.game_logic.player_ships.append(ship)
            self.current_ship_index += 1
            self.update_setup_board_display()
            self.update_ship_info()
            self.update_ship_counts()  # Обновляем счетчики кораблей
        else:
            self.show_invalid_placement(x, y)

    def on_setup_done_clicked(self):
        if self.current_ship_index == len(self.ships):
            self.stacked_widget.setCurrentWidget(self.game_widget)
        else:
            self.ship_info_label.setText("Разместите все корабли перед началом игры!")
            self.ship_info_label.setStyleSheet("color: red;")
            QTimer.singleShot(2000, lambda: self.update_ship_info())

    def setup_computer_ships(self):
        # Создаем список кораблей
        ships = [4, 3, 3, 2, 2, 2, 1, 1, 1, 1]
        
        # Сначала очищаем доску и список кораблей
        self.game_logic.computer_board = [[CellState.EMPTY for _ in range(10)] for _ in range(10)]
        self.game_logic.computer_ships = []
        
        # Размещаем корабли
        for ship_size in ships:
            ship = Ship(ship_size)
            placed = False
            attempts = 0
            max_attempts = 100  # Максимальное количество попыток размещения
            
            while not placed and attempts < max_attempts:
                x = random.randint(0, 9)
                y = random.randint(0, 9)
                is_horizontal = random.choice([True, False])
                
                if self.game_logic.place_ship(self.game_logic.computer_board, ship, (x, y), is_horizontal):
                    self.game_logic.computer_ships.append(ship)
                    placed = True
                attempts += 1
            
            if not placed:
                return False

    def update_board_display(self):
        # Update player's board
        for i in range(10):
            for j in range(10):
                state = self.game_logic.player_board[i][j]
                self.update_button(self.player_buttons[i][j], state)

        # Update computer's board
        for i in range(10):
            for j in range(10):
                state = self.game_logic.computer_board[i][j]
                self.update_button(self.computer_buttons[i][j], state, is_computer_board=True)

    def update_button(self, button: QPushButton, state: CellState, is_computer_board: bool = False):
        if state == CellState.EMPTY:
            button.setStyleSheet("background-color: white;")
            button.setEnabled(True)  # Клетка доступна для выстрела
        elif state == CellState.SHIP:
            if is_computer_board:
                button.setStyleSheet("background-color: white;")  # Скрываем корабли компьютера
            else:
                button.setStyleSheet("background-color: gray;")  # Корабли игрока видны
            button.setEnabled(True)  # Клетка доступна для выстрела
        elif state == CellState.HIT:
            button.setStyleSheet("background-color: red;")
            button.setEnabled(False)  # Клетка уже использована
        elif state == CellState.MISS:
            button.setStyleSheet("background-color: blue;")
            button.setEnabled(False)  # Клетка уже использована

    def on_player_board_click(self, x: int, y: int):
        if self.game_logic.current_turn == "player" and not self.game_logic.game_over:
            hit, ship_sunk = self.game_logic.make_shot(self.game_logic.computer_board, x, y)
            
            if hit:
                # Mark surrounding cells if ship is sunk
                if ship_sunk:
                    ship_coords = self.game_logic.get_ship_coordinates(self.game_logic.computer_board, x, y)
                    for sx, sy in ship_coords:
                        self.game_logic.mark_surrounding_cells(self.game_logic.computer_board, sx, sy)
            
            self.update_board_display()
            
            if ship_sunk:
                self.game_logic.mark_surrounding_cells(self.game_logic.computer_board, x, y)
                self.update_board_display()
            elif hit:
                self.update_board_display()
            else:
                self.game_logic.switch_turn()
                self.computer_turn()

        if self.game_logic.check_game_over():
            winner = "Вы" if self.game_logic.winner == "player" else "Компьютер"
            self.show_result(winner)

    def on_computer_board_click(self, x: int, y: int):
        if self.game_logic.current_turn == "player" and not self.game_logic.game_over:
            # Проверяем, не была ли клетка уже использована
            if self.game_logic.computer_board[x][y] in [CellState.HIT, CellState.MISS]:
                return  # Клетка уже использована

            hit, ship_sunk = self.game_logic.make_shot(self.game_logic.computer_board, x, y)
            
            if hit:
                # Mark surrounding cells if ship is sunk
                if ship_sunk:
                    ship_coords = self.game_logic.get_ship_coordinates(self.game_logic.computer_board, x, y)
                    for sx, sy in ship_coords:
                        self.game_logic.mark_surrounding_cells(self.game_logic.computer_board, sx, sy)
                # После попадания (будь то уничтоженный или подбитый корабль) продолжаем ход
                self.update_board_display()
            else:
                # При промахе передаем ход компьютеру
                self.game_logic.switch_turn()
                self.computer_turn()

        if self.game_logic.check_game_over():
            winner = "Вы" if self.game_logic.winner == "player" else "Компьютер"
            self.show_result(winner)

    def computer_turn(self):
        def make_computer_shot():
            # Ищем доступную клетку
            available_cells = []
            # Сначала ищем клетки вокруг попаданий
            for x in range(10):
                for y in range(10):
                    if self.game_logic.player_board[x][y] == CellState.HIT:
                        # Проверяем соседние клетки
                        for dx, dy in [(1, 0), (-1, 0), (0, 1), (0, -1)]:
                            nx, ny = x + dx, y + dy
                            if 0 <= nx < 10 and 0 <= ny < 10:
                                if self.game_logic.player_board[nx][ny] in [CellState.EMPTY, CellState.SHIP]:
                                    available_cells.append((nx, ny))
            
            # Если не нашли клеток вокруг попаданий, ищем случайные клетки
            if not available_cells:
                for x in range(10):
                    for y in range(10):
                        if self.game_logic.player_board[x][y] in [CellState.EMPTY, CellState.SHIP]:
                            available_cells.append((x, y))
            
            if not available_cells:
                return  # Нет доступных клеток
                
            # Выбираем клетку
            x, y = random.choice(available_cells)
            
            # Создаем функцию для выполнения выстрела
            def execute_shot():
                hit, ship_sunk = self.game_logic.make_shot(self.game_logic.player_board, x, y)
                
                if hit:
                    # Mark surrounding cells if ship is sunk
                    if ship_sunk:
                        ship_coords = self.game_logic.get_ship_coordinates(self.game_logic.player_board, x, y)
                        for sx, sy in ship_coords:
                            self.game_logic.mark_surrounding_cells(self.game_logic.player_board, sx, sy)
                    # После попадания (будь то уничтоженный или подбитый корабль) продолжаем ход
                    QTimer.singleShot(500, make_computer_shot)
                else:
                    # При промахе передаем ход игроку
                    self.game_logic.switch_turn()
                
                self.update_board_display()
                
                # Проверяем конец игры сразу после хода
            if self.game_logic.check_game_over():
                winner = "Вы" if self.game_logic.winner == "player" else "Компьютер"
                self.show_result(winner)
            
            # Добавляем задержку перед выстрелом
            QTimer.singleShot(500, execute_shot)

        # Вызываем сразу без задержки
        make_computer_shot()

    def show_ship_setup(self):
        self.stacked_widget.setCurrentWidget(self.ship_setup_widget)
        self.setup_computer_ships()  # Размещаем корабли компьютера

    def show_result(self, winner):
        """Показывает экран с результатом игры"""
        result_widget = ResultWidget(winner, self)
        self.stacked_widget.addWidget(result_widget)
        self.stacked_widget.setCurrentWidget(result_widget)

    def init_game_ui(self):
        layout = QHBoxLayout(self.game_widget)

        # Create player's board
        player_board_widget = QWidget()
        player_layout = QVBoxLayout(player_board_widget)
        player_label = QLabel("Ваше поле")
        player_label.setAlignment(Qt.AlignCenter)
        player_layout.addWidget(player_label)
        
        self.player_grid = QGridLayout()
        self.player_buttons = []
        for i in range(10):
            row = []
            for j in range(10):
                button = QPushButton()
                button.setFixedSize(QSize(40, 40))
                button.clicked.connect(lambda checked, x=i, y=j: self.on_player_board_click(x, y))
                self.player_grid.addWidget(button, i, j)
                row.append(button)
            self.player_buttons.append(row)
        player_layout.addLayout(self.player_grid)
        layout.addWidget(player_board_widget)

        # Create computer's board
        computer_board_widget = QWidget()
        computer_layout = QVBoxLayout(computer_board_widget)
        computer_label = QLabel("Поле противника")
        computer_label.setAlignment(Qt.AlignCenter)
        computer_layout.addWidget(computer_label)
        
        self.computer_grid = QGridLayout()
        self.computer_buttons = []
        for i in range(10):
            row = []
            for j in range(10):
                button = QPushButton()
                button.setFixedSize(QSize(40, 40))
                button.clicked.connect(lambda checked, x=i, y=j: self.on_computer_board_click(x, y))
                self.computer_grid.addWidget(button, i, j)
                row.append(button)
            self.computer_buttons.append(row)
        computer_layout.addLayout(self.computer_grid)
        layout.addWidget(computer_board_widget)

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_R and self.stacked_widget.currentWidget() == self.ship_setup_widget:
            self.is_horizontal = not self.is_horizontal
            self.orientation_label.setText(
                "Горизонтально" if self.is_horizontal else "Вертикально"
            )
        else:
            super().keyPressEvent(event) 