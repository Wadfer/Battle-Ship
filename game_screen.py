from PyQt5.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                           QPushButton, QLabel, QGridLayout, QMessageBox)
from PyQt5.QtCore import Qt, QSize, QTimer
from PyQt5.QtGui import QPixmap, QPalette, QBrush
import os
import random
from datetime import datetime

class GameScreen(QMainWindow):
    def __init__(self, player_ships):
        super().__init__()
        self.player_ships = player_ships
        self.player_board = [[0 for _ in range(10)] for _ in range(10)]
        self.computer_board = [[0 for _ in range(10)] for _ in range(10)]
        self.computer_ships = []
        self.player_turn = True
        self.game_stats = {
            'shots': 0,
            'hits': 0,
            'start_time': datetime.now(),
            'player_ships_destroyed': 0,
            'computer_ships_destroyed': 0
        }
        # AI targeting variables
        self.last_hit = None
        self.hunting_mode = False
        self.hit_direction = None
        self.possible_targets = []
        
        # Initialize AI shot timer
        self.shot_timer = QTimer()
        self.shot_timer.setSingleShot(True)
        self.shot_timer.timeout.connect(self.make_computer_shot)
        
        self.initUI()
        self.place_computer_ships()
        self.place_player_ships()
        
    def initUI(self):
        self.setWindowTitle('Морской бой - Игра')
        self.setFixedSize(1200, 700)
        
        # Create central widget and main layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(20, 20, 20, 20)  # Reduced top margin from 50 to 20
        
        # Create player's board
        player_board_widget = QWidget()
        player_layout = QVBoxLayout(player_board_widget)
        player_layout.setSpacing(20)  # Add spacing between title and board
        
        # Add player's board title
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
        
        # Create player's grid
        player_grid = QGridLayout()
        player_grid.setSpacing(1)
        
        # Add column labels (A-K)
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
        
        # Add row labels (1-10)
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
        
        # Create player's cells
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
        
        # Create computer's board
        computer_board_widget = QWidget()
        computer_layout = QVBoxLayout(computer_board_widget)
        
        # Add computer's board title
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
        
        # Create computer's grid
        computer_grid = QGridLayout()
        computer_grid.setSpacing(1)
        
        # Add column labels (A-K)
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
        
        # Add row labels (1-10)
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
        
        # Create computer's cells
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
        
        # Add boards to main layout
        main_layout.addWidget(player_board_widget)
        main_layout.addWidget(computer_board_widget)
        
        # Set background
        self.set_background()
        
    def place_computer_ships(self):
        ships = [(4, 1), (3, 2), (2, 3), (1, 4)]
        for size, count in ships:
            for _ in range(count):
                while True:
                    row = random.randint(0, 9)
                    col = random.randint(0, 9)
                    is_horizontal = random.choice([True, False])
                    
                    if self.can_place_ship(self.computer_board, row, col, size, is_horizontal):
                        # Размещаем корабль на доске, но не отображаем его визуально
                        if is_horizontal:
                            for i in range(size):
                                self.computer_board[row][col + i] = 1
                        else:
                            for i in range(size):
                                self.computer_board[row + i][col] = 1
                        self.computer_ships.append((row, col, size, is_horizontal))
                        break
    
    def place_player_ships(self):
        for start_pos, size, is_horizontal in self.player_ships:
            row, col = start_pos
            row -= 1  # Convert to 0-based indexing
            col -= 1
            self.place_ship(self.player_board, row, col, size, is_horizontal)
            # Show ship on player's board
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
        # Check if the cell and its surroundings are empty
        for r in range(max(0, row - 1), min(10, row + 2)):
            for c in range(max(0, col - 1), min(10, col + 2)):
                if board[r][c] != 0:
                    return False
        return True
    
    def place_ship(self, board, row, col, size, is_horizontal):
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
        if not self.player_turn:
            return
            
        # Convert to 0-based indexing
        row -= 1
        col -= 1
        
        # Check if the cell was already shot
        if self.computer_board[row][col] in [2, 3]:  # 2 for miss, 3 for hit
            return
            
        # Update shots count
        self.game_stats['shots'] += 1
            
        # Make the shot
        if self.computer_board[row][col] == 1:  # Hit
            self.computer_board[row][col] = 3
            self.computer_cells[(row + 1, col + 1)].setStyleSheet("""
                QPushButton {
                    background-color: #f44336;
                    border: 1px solid #d32f2f;
                }
            """)
            
            # Увеличиваем счетчик попаданий
            self.game_stats['hits'] += 1
            
            # Check if ship is destroyed
            if self.is_ship_destroyed(self.computer_board, row, col):
                self.game_stats['computer_ships_destroyed'] += 1
                self.mark_surrounding_cells(row, col)
                
            # Check if all ships are destroyed
            if self.check_winner(self.computer_board):
                self.show_result(True)
                return
        else:  # Miss
            self.computer_board[row][col] = 2
            self.computer_cells[(row + 1, col + 1)].setStyleSheet("""
                QPushButton {
                    background-color: white;
                    border: 1px solid #bdbdbd;
                }
            """)
            self.player_turn = False
            self.computer_turn()
    
    def is_ship_destroyed(self, board, row, col):
        # Find the ship's cells
        ship_cells = []
        # Check horizontal
        c = col
        while c >= 0 and board[row][c] in [1, 3]:
            ship_cells.append((row, c))
            c -= 1
        c = col + 1
        while c < 10 and board[row][c] in [1, 3]:
            ship_cells.append((row, c))
            c += 1
        # Check vertical
        r = row
        while r >= 0 and board[r][col] in [1, 3]:
            ship_cells.append((r, col))
            r -= 1
        r = row + 1
        while r < 10 and board[r][col] in [1, 3]:
            ship_cells.append((r, col))
            r += 1
            
        # Check if all cells are hit
        return all(board[r][c] == 3 for r, c in ship_cells)
    
    def mark_surrounding_cells(self, row, col):
        # Find the ship's cells
        ship_cells = []
        # Check horizontal
        c = col
        while c >= 0 and self.computer_board[row][c] in [1, 3]:
            ship_cells.append((row, c))
            c -= 1
        c = col + 1
        while c < 10 and self.computer_board[row][c] in [1, 3]:
            ship_cells.append((row, c))
            c += 1
        # Check vertical
        r = row
        while r >= 0 and self.computer_board[r][col] in [1, 3]:
            ship_cells.append((r, col))
            r -= 1
        r = row + 1
        while r < 10 and self.computer_board[r][col] in [1, 3]:
            ship_cells.append((r, col))
            r += 1
            
        # Mark surrounding cells
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
        # Start the timer for delayed shot
        self.shot_timer.start(500)  # 0.5 second delay
    
    def make_computer_shot(self):
        if not self.player_turn:  # Additional check to prevent multiple shots
            if self.hunting_mode:
                # If we have a hit, try to find the rest of the ship
                if self.last_hit:
                    row, col = self.last_hit
                    if self.hit_direction is None:
                        # Try all four directions
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
                        # Continue in the same direction
                        dr, dc = self.hit_direction
                        new_row, new_col = row + dr, col + dc
                        if (0 <= new_row < 10 and 0 <= new_col < 10 and 
                            self.player_board[new_row][new_col] not in [2, 3]):
                            self.fire_shot(new_row, new_col)
                            return
                        else:
                            # If we hit the edge or a miss, try the opposite direction
                            dr, dc = -dr, -dc
                            new_row, new_col = self.last_hit[0] + dr, self.last_hit[1] + dc
                            if (0 <= new_row < 10 and 0 <= new_col < 10 and 
                                self.player_board[new_row][new_col] not in [2, 3]):
                                self.hit_direction = (dr, dc)
                                self.fire_shot(new_row, new_col)
                                return
                            else:
                                # If both directions are blocked, reset hunting mode
                                self.hunting_mode = False
                                self.last_hit = None
                                self.hit_direction = None
            
            # If not in hunting mode, use probability targeting
            if not self.hunting_mode:
                # Create probability map
                probability_map = [[0 for _ in range(10)] for _ in range(10)]
                
                # Mark already shot cells as -1
                for r in range(10):
                    for c in range(10):
                        if self.player_board[r][c] in [2, 3]:
                            probability_map[r][c] = -1
                
                # Calculate probabilities based on ship placement rules
                for r in range(10):
                    for c in range(10):
                        if probability_map[r][c] != -1:
                            # Check horizontal and vertical possibilities
                            for size in range(1, 5):  # Ship sizes from 1 to 4
                                # Horizontal
                                if c + size <= 10:
                                    valid = True
                                    for i in range(size):
                                        if probability_map[r][c + i] == -1:
                                            valid = False
                                            break
                                    if valid:
                                        for i in range(size):
                                            probability_map[r][c + i] += 1
                                
                                # Vertical
                                if r + size <= 10:
                                    valid = True
                                    for i in range(size):
                                        if probability_map[r + i][c] == -1:
                                            valid = False
                                            break
                                    if valid:
                                        for i in range(size):
                                            probability_map[r + i][c] += 1
                
                # Find cells with highest probability
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
            
            # If all else fails, make a random shot
            while True:
                row = random.randint(0, 9)
                col = random.randint(0, 9)
                if self.player_board[row][col] not in [2, 3]:
                    self.fire_shot(row, col)
                    break
    
    def fire_shot(self, row, col):
        if self.player_board[row][col] == 1:  # Hit
            self.player_board[row][col] = 3
            self.player_cells[(row + 1, col + 1)].setStyleSheet("""
                QPushButton {
                    background-color: #f44336;
                    border: 1px solid #d32f2f;
                }
            """)
            
            # Update AI targeting
            self.hunting_mode = True
            self.last_hit = (row, col)
            
            # Check if ship is destroyed
            if self.is_ship_destroyed(self.player_board, row, col):
                self.game_stats['player_ships_destroyed'] += 1
                self.mark_surrounding_cells_player(row, col)
                # Reset hunting mode when ship is destroyed
                self.hunting_mode = False
                self.last_hit = None
                self.hit_direction = None
                
            # Check if all ships are destroyed
            if self.check_winner(self.player_board):
                self.show_result(False)
                return
                
            # Continue AI turn after hit
            self.computer_turn()
            
        else:  # Miss
            self.player_board[row][col] = 2
            self.player_cells[(row + 1, col + 1)].setStyleSheet("""
                QPushButton {
                    background-color: white;
                    border: 1px solid #bdbdbd;
                }
            """)
            # If we're in hunting mode and missed, try another direction
            if self.hunting_mode:
                self.hit_direction = None
            # Give turn to player only after miss
            self.player_turn = True
    
    def mark_surrounding_cells_player(self, row, col):
        # Find the ship's cells
        ship_cells = []
        # Check horizontal
        c = col
        while c >= 0 and self.player_board[row][c] in [1, 3]:
            ship_cells.append((row, c))
            c -= 1
        c = col + 1
        while c < 10 and self.player_board[row][c] in [1, 3]:
            ship_cells.append((row, c))
            c += 1
        # Check vertical
        r = row
        while r >= 0 and self.player_board[r][col] in [1, 3]:
            ship_cells.append((r, col))
            r -= 1
        r = row + 1
        while r < 10 and self.player_board[r][col] in [1, 3]:
            ship_cells.append((r, col))
            r += 1
            
        # Mark surrounding cells
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
        return all(cell != 1 for row in board for cell in row)
    
    def show_result(self, player_won):
        from result_screen import ResultScreen
        self.result_screen = ResultScreen(player_won, self.game_stats)
        self.result_screen.show()
        self.close()
    
    def set_background(self):
        try:
            background_path = "assets/Game_background.jpg"
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
        
        # If background loading fails, set default gradient background
        self.setStyleSheet("""
            QMainWindow {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                          stop:0 #1a237e, stop:1 #0d47a1);
            }
        """) 