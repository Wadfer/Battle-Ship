import sys
import os

# Добавляем директорию проекта в sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from PyQt5.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QGridLayout, QGroupBox)
from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import QPalette, QPixmap, QFont
from src.menu_widget_new import MenuWidget
from src.ship_placement_widget import ShipPlacementWidget
from src.game_logic import CellState, GameLogic, Ship
import random


class GameWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.game_logic = GameLogic()
        self.init_ui()
        self.current_widget = None

    def init_ui(self):
        self.setWindowTitle("Морской бой")
        self.setGeometry(100, 100, 1000, 600)
        self.setFixedSize(1000, 600)
        
        # Создаем главное меню
        self.menu_widget = MenuWidget()
        self.setCentralWidget(self.menu_widget)
        
        # Подключаем сигналы
        self.menu_widget.start_game.connect(self.show_ship_placement)
        self.menu_widget.exit_game.connect(self.close)



    def show_ship_placement(self):
        """Показывает экран расстановки кораблей"""
        if self.current_widget:
            self.current_widget.hide()
        
        self.ship_placement_widget = ShipPlacementWidget()
        self.ship_placement_widget.start_game.connect(self.start_game)
        self.setCentralWidget(self.ship_placement_widget)
        self.current_widget = self.ship_placement_widget

    def start_game(self):
        """Начинает новую игру"""
        print("Начинаем новую игру")
        if self.current_widget:
            self.current_widget.hide()
        
        # Здесь будет создание игрового поля
        self.game_widget = QLabel("Игровое поле")
        self.game_widget.setStyleSheet("""
            QLabel {
                border: 2px solid white;
                background-color: #00008B;
                color: white;
                font-size: 24px;
            }
        """)
        self.game_widget.setFixedSize(1000, 600)
        self.setCentralWidget(self.game_widget)
        self.current_widget = self.game_widget    # Размещаем корабли игрока
        self.setup_player_ships()  # Размещаем корабли компьютера
        self.setup_computer_ships()  # Размещаем корабли компьютера
        self.game_logic.start_game()  # Начинаем игру
        self.menu_widget.show_game()  # Показываем игровое поле в меню

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

    def setup_player_ships(self):
        """Автоматически размещает корабли игрока"""
        # Создаем список кораблей
        ships = [4, 3, 3, 2, 2, 2, 1, 1, 1, 1]
        
        # Сначала очищаем доску и список кораблей
        self.game_logic.player_board = [[CellState.EMPTY for _ in range(10)] for _ in range(10)]
        self.game_logic.player_ships = []
        
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
                
                if self.game_logic.place_ship(self.game_logic.player_board, ship, (x, y), is_horizontal):
                    self.game_logic.player_ships.append(ship)
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
            button.setEnabled(True)  
        elif state == CellState.SHIP:
            if is_computer_board:
                button.setStyleSheet("background-color: white;")  
            else:
                button.setStyleSheet("background-color: gray;")  

    def make_computer_shot(self):
        """Выбирает случайную клетку для выстрела компьютера"""
        # Получаем список доступных клеток для выстрела
        available_cells = []
        for x in range(10):
            for y in range(10):
                if self.game_logic.player_board[x][y] in [CellState.EMPTY, CellState.SHIP]:
                    available_cells.append((x, y))
        
        if not available_cells:
            return  
        
        # Выбираем клетку
        x, y = random.choice(available_cells)
        self.execute_shot(x, y)

    def execute_shot(self, x: int, y: int):
        """Выполняет выстрел по указанной клетке"""
        hit, ship_sunk = self.game_logic.make_shot(self.game_logic.player_board, x, y)
        
        if hit:
            # Mark surrounding cells if ship is sunk
            if ship_sunk:
                ship_coords = self.game_logic.get_ship_coordinates(self.game_logic.player_board, x, y)
                for sx, sy in ship_coords:
                    self.game_logic.mark_surrounding_cells(self.game_logic.player_board, sx, sy)
            # После попадания (будь то уничтоженный или подбитый корабль) продолжаем ход
            QTimer.singleShot(500, self.make_computer_shot)
        else:
            # При промахе передаем ход игроку
            self.game_logic.switch_turn()
        
        self.update_board_display()
        
        # Проверяем конец игры сразу после хода
        if self.game_logic.check_game_over():
            winner = "Вы" if self.game_logic.winner == "player" else "Компьютер"
            self.show_result(winner)



    def keyPressEvent(self, event):
        super().keyPressEvent(event)