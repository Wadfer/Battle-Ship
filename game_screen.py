from PyQt5.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                           QPushButton, QLabel, QGridLayout, QMessageBox)
from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import QPixmap, QPalette, QBrush
import os
import random

class GameScreen(QMainWindow):
    def __init__(self, player_ships):
        super().__init__()
        self.player_ships = player_ships
        self.player_board = [[0 for _ in range(10)] for _ in range(10)]
        self.computer_board = [[0 for _ in range(10)] for _ in range(10)]
        self.computer_ships = []
        self.player_turn = True
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
        main_layout.setContentsMargins(20, 50, 20, 20)  # Add top margin
        
        # Create player's board
        player_board_widget = QWidget()
        player_layout = QVBoxLayout(player_board_widget)
        player_layout.setSpacing(20)  # Add spacing between title and board
        
        # Add player's board title
        player_title = QLabel("Ваше поле")
        player_title.setAlignment(Qt.AlignCenter)
        player_title.setStyleSheet("color: white; font-size: 20px; font-weight: bold;")
        player_layout.addWidget(player_title)
        
        # Create player's grid
        player_grid = QGridLayout()
        player_grid.setSpacing(1)
        
        # Add column labels (A-K)
        for i, letter in enumerate('АБВГДЕЖЗИК'):
            label = QLabel(letter)
            label.setAlignment(Qt.AlignCenter)
            label.setStyleSheet("color: white; font-weight: bold;")
            player_grid.addWidget(label, 0, i + 1)
        
        # Add row labels (1-10)
        for i in range(1, 11):
            label = QLabel(str(i))
            label.setAlignment(Qt.AlignCenter)
            label.setStyleSheet("color: white; font-weight: bold;")
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
        computer_title.setStyleSheet("color: white; font-size: 20px; font-weight: bold;")
        computer_layout.addWidget(computer_title)
        
        # Create computer's grid
        computer_grid = QGridLayout()
        computer_grid.setSpacing(1)
        
        # Add column labels (A-K)
        for i, letter in enumerate('АБВГДЕЖЗИК'):
            label = QLabel(letter)
            label.setAlignment(Qt.AlignCenter)
            label.setStyleSheet("color: white; font-weight: bold;")
            computer_grid.addWidget(label, 0, i + 1)
        
        # Add row labels (1-10)
        for i in range(1, 11):
            label = QLabel(str(i))
            label.setAlignment(Qt.AlignCenter)
            label.setStyleSheet("color: white; font-weight: bold;")
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
                        self.place_ship(self.computer_board, row, col, size, is_horizontal)
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
                        background-color: #4CAF50;
                        border: 1px solid #388E3C;
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
        else:
            for i in range(size):
                board[row + i][col] = 1
    
    def make_shot(self, row, col):
        if not self.player_turn:
            return
            
        # Convert to 0-based indexing
        row -= 1
        col -= 1
        
        # Check if the cell was already shot
        if self.computer_board[row][col] in [2, 3]:  # 2 for miss, 3 for hit
            return
            
        # Make the shot
        if self.computer_board[row][col] == 1:  # Hit
            self.computer_board[row][col] = 3
            self.computer_cells[(row + 1, col + 1)].setStyleSheet("""
                QPushButton {
                    background-color: #f44336;
                    border: 1px solid #d32f2f;
                }
            """)
            
            # Check if ship is destroyed
            if self.is_ship_destroyed(self.computer_board, row, col):
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
        while True:
            row = random.randint(0, 9)
            col = random.randint(0, 9)
            
            if self.player_board[row][col] not in [2, 3]:  # Not shot yet
                if self.player_board[row][col] == 1:  # Hit
                    self.player_board[row][col] = 3
                    self.player_cells[(row + 1, col + 1)].setStyleSheet("""
                        QPushButton {
                            background-color: #f44336;
                            border: 1px solid #d32f2f;
                        }
                    """)
                    
                    # Check if ship is destroyed
                    if self.is_ship_destroyed(self.player_board, row, col):
                        self.mark_surrounding_cells_player(row, col)
                        
                    # Check if all ships are destroyed
                    if self.check_winner(self.player_board):
                        self.show_result(False)
                        return
                else:  # Miss
                    self.player_board[row][col] = 2
                    self.player_cells[(row + 1, col + 1)].setStyleSheet("""
                        QPushButton {
                            background-color: white;
                            border: 1px solid #bdbdbd;
                        }
                    """)
                    self.player_turn = True
                    break
    
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
        self.result_screen = ResultScreen(player_won)
        self.result_screen.show()
        self.close()
    
    def set_background(self):
        try:
            background_path = "assets/game_background.jpg"
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