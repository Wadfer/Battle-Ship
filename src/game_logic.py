from enum import Enum
from typing import List, Tuple, Optional

class CellState(Enum):
    EMPTY = 0
    SHIP = 1
    HIT = 2
    MISS = 3

class Ship:
    def __init__(self, size: int):
        self.size = size
        self.hits = 0
        self.coordinates: List[Tuple[int, int]] = []
        self.sunk = False

    def is_sunk(self) -> bool:
        return self.hits == self.size

    def mark_hit(self, x: int, y: int):
        if (x, y) in self.coordinates:
            self.hits += 1
            # Проверяем, уничтожен ли корабль
            if self.is_sunk():
                self.sunk = True
                return True, True  # Возвращаем True, True для уничтожения
            return True, False  # Возвращаем True, False для подбитого
        return False, False  # Возвращаем False, False для промаха

class GameLogic:
    def __init__(self):
        self.board_size = 10
        self.player_board = [[CellState.EMPTY for _ in range(self.board_size)] for _ in range(self.board_size)]
        self.computer_board = [[CellState.EMPTY for _ in range(self.board_size)] for _ in range(self.board_size)]
        self.player_ships: List[Ship] = []
        self.computer_ships: List[Ship] = []
        self.current_turn = "player"  # or "computer"
        self.game_over = False
        self.winner = None

    def is_valid_position(self, board: List[List[CellState]], x: int, y: int) -> bool:
        # Check if position is within board bounds
        if not (0 <= x < self.board_size and 0 <= y < self.board_size):
            return False
        
        # Check if position and surrounding cells are empty
        for dx in [-1, 0, 1]:
            for dy in [-1, 0, 1]:
                nx, ny = x + dx, y + dy
                if 0 <= nx < self.board_size and 0 <= ny < self.board_size:
                    if board[nx][ny] == CellState.SHIP:
                        return False
        return True

    def place_ship(self, board: List[List[CellState]], ship: Ship, start_pos: Tuple[int, int], is_horizontal: bool) -> bool:
        x, y = start_pos
        
        # Check if ship can be placed
        if is_horizontal:
            # Check if ship fits horizontally
            if y + ship.size > self.board_size:
                return False
            # Check all positions and surrounding cells
            for i in range(ship.size):
                if not self.is_valid_position(board, x, y + i):
                    return False
            # Place the ship
            ship.coordinates = []  # Очищаем список координат перед размещением
            for i in range(ship.size):
                board[x][y + i] = CellState.SHIP
                ship.coordinates.append((x, y + i))
            return True
        else:
            # Check if ship fits vertically
            if x + ship.size > self.board_size:
                return False
            # Check all positions and surrounding cells
            for i in range(ship.size):
                if not self.is_valid_position(board, x + i, y):
                    return False
            # Place the ship
            ship.coordinates = []  # Очищаем список координат перед размещением
            for i in range(ship.size):
                board[x + i][y] = CellState.SHIP
                ship.coordinates.append((x + i, y))
            return True

    def make_shot(self, board: List[List[CellState]], x: int, y: int) -> Tuple[bool, bool]:
        # Проверяем, не была ли клетка уже использована
        if board[x][y] in [CellState.HIT, CellState.MISS]:
            return False, False

        if board[x][y] == CellState.SHIP:
            # Находим корабль, который был попален
            ships = self.player_ships if board is self.player_board else self.computer_ships
            for ship in ships:
                # Проверяем все координаты корабля
                if any(coord == (x, y) for coord in ship.coordinates):
                    hit, ship_sunk = ship.mark_hit(x, y)
                    board[x][y] = CellState.HIT
                    
                    # Если корабль уничтожен
                    if ship_sunk:
                        # Отмечаем все клетки корабля как HIT
                        for sx, sy in ship.coordinates:
                            if board[sx][sy] == CellState.SHIP:
                                board[sx][sy] = CellState.HIT
                        # Отмечаем окружающие клетки
                        for sx, sy in ship.coordinates:
                            self.mark_surrounding_cells(board, sx, sy)
                        return True, True
                    
                    # Если корабль подбит
                    if hit:
                        return True, False
            
            # Если корабль не найден, но клетка SHIP - это ошибка
            raise ValueError(f"Клетка ({x}, {y}) помечена как корабль, но корабль не найден")
            
        elif board[x][y] == CellState.EMPTY:
            board[x][y] = CellState.MISS
            return False, False
        return False, False

    def mark_surrounding_cells(self, board: List[List[CellState]], x: int, y: int):
        """Mark all surrounding cells around the sunk ship as misses."""
        # Mark all adjacent cells (horizontal and vertical)
        for dx, dy in [(1, 0), (-1, 0), (0, 1), (0, -1)]:
            nx, ny = x + dx, y + dy
            if 0 <= nx < self.board_size and 0 <= ny < self.board_size:
                if board[nx][ny] in [CellState.EMPTY, CellState.SHIP]:
                    board[nx][ny] = CellState.MISS
        
        # Mark all diagonal cells
        for dx, dy in [(1, 1), (-1, 1), (1, -1), (-1, -1)]:
            nx, ny = x + dx, y + dy
            if 0 <= nx < self.board_size and 0 <= ny < self.board_size:
                if board[nx][ny] in [CellState.EMPTY, CellState.SHIP]:
                    board[nx][ny] = CellState.MISS

    def get_ship_coordinates(self, board: List[List[CellState]], x: int, y: int) -> List[Tuple[int, int]]:
        """Find all coordinates of a ship that was hit."""
        # Находим корабль по координатам
        ships = self.player_ships if board is self.player_board else self.computer_ships
        for ship in ships:
            if (x, y) in ship.coordinates:
                return ship.coordinates
        return []

    def check_game_over(self) -> bool:
        player_ships_sunk = all(ship.is_sunk() for ship in self.player_ships)
        computer_ships_sunk = all(ship.is_sunk() for ship in self.computer_ships)
        
        if player_ships_sunk:
            self.game_over = True
            self.winner = "computer"
            return True
        elif computer_ships_sunk:
            self.game_over = True
            self.winner = "player"
            return True
        return False

    def switch_turn(self):
        self.current_turn = "computer" if self.current_turn == "player" else "player" 