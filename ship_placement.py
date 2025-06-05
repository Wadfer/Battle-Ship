from PyQt5.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                           QPushButton, QLabel, QGridLayout)
from PyQt5.QtCore import Qt, QSize, QPoint
from PyQt5.QtGui import QPixmap, QPalette, QBrush, QColor, QPainter, QPen, QCursor
import os
import random

class ShipPreview(QWidget):
    def __init__(self, size, parent=None):
        super().__init__(parent)
        self.ship_size = size
        self.is_horizontal = True
        self.setFixedSize(size * 25, 25)
        self.setStyleSheet("""
            QWidget {
                background-color: transparent;
                border: none;
            }
        """)
        self.setMouseTracking(True)
        self.is_dragging = False
        self.drag_start_pos = None
        self.original_pos = None
        self.original_parent = None
        
    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.is_dragging = True
            self.drag_start_pos = event.pos()
            self.original_pos = self.pos()
            self.original_parent = self.parent()
            self.raise_()
            
    def mouseMoveEvent(self, event):
        if self.is_dragging:
            # Перемещаем корабль относительно курсора
            new_pos = self.mapToParent(event.pos() - self.drag_start_pos)
            # Ограничиваем перемещение границами родительского виджета
            new_pos.setX(max(0, min(new_pos.x(), self.parent().width() - self.width())))
            new_pos.setY(max(0, min(new_pos.y(), self.parent().height() - self.height())))
            self.move(new_pos)
            
    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton and self.is_dragging:
            self.is_dragging = False
            
            # Проверяем, находится ли корабль над игровым полем
            game_board = self.parent().findChild(QWidget, "game_board")
            if game_board:
                # Получаем позицию центра корабля относительно игрового поля
                center_pos = self.mapTo(game_board, self.rect().center())
                if game_board.geometry().contains(center_pos):
                    # Пытаемся разместить корабль
                    if not self.parent().try_place_ship(self):
                        self.return_to_original_position()
                else:
                    self.return_to_original_position()
            else:
                self.return_to_original_position()
    
    def return_to_original_position(self):
        if self.original_parent:
            self.setParent(self.original_parent)
            self.move(self.original_pos)
            self.raise_()
            
    def rotate(self):
        self.is_horizontal = not self.is_horizontal
        if self.is_horizontal:
            self.setFixedSize(self.ship_size * 25, 25)
        else:
            self.setFixedSize(25, self.ship_size * 25)
        self.update()
            
    def mouseDoubleClickEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.rotate()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # Цвета в стиле старой карты
        ship_color = QColor(210, 180, 140)  # Бежевый
        border_color = QColor(139, 69, 19)  # Коричневый
        detail_color = QColor(160, 82, 45)  # Темно-коричневый
        
        # Получаем размеры для отрисовки
        width = self.width()
        height = self.height()
        cell_size = min(width // self.ship_size, height)
        
        if self.is_horizontal:
            # Рисуем основную часть
            painter.setBrush(QBrush(ship_color))
            painter.setPen(QPen(border_color, 2))
            painter.drawRoundedRect(0, 0, width - 5, height, 5, 5)
            
            # Рисуем детали
            for i in range(self.ship_size):
                # Иллюминаторы
                painter.setBrush(QBrush(detail_color))
                painter.setPen(QPen(border_color, 1))
                painter.drawEllipse(i * cell_size + 8, 8, 9, 9)
                
                # Деревянные доски
                if i < self.ship_size - 1:
                    painter.setPen(QPen(detail_color, 1, Qt.DashLine))
                    painter.drawLine(i * cell_size + cell_size, 5, i * cell_size + cell_size, 20)
            
            # Нос корабля
            painter.setBrush(QBrush(ship_color))
            painter.setPen(QPen(border_color, 2))
            painter.drawPolygon([
                QPoint(width - 5, 0),
                QPoint(width, height // 2),
                QPoint(width - 5, height)
            ])
            
            # Добавляем текстуру дерева
            for i in range(self.ship_size):
                for j in range(3):
                    painter.setPen(QPen(detail_color, 1))
                    painter.drawLine(i * cell_size + 5, 5 + j * 7, i * cell_size + 20, 5 + j * 7)
        else:
            # Рисуем основную часть
            painter.setBrush(QBrush(ship_color))
            painter.setPen(QPen(border_color, 2))
            painter.drawRoundedRect(0, 0, width, height - 5, 5, 5)
            
            # Рисуем детали
            for i in range(self.ship_size):
                # Иллюминаторы
                painter.setBrush(QBrush(detail_color))
                painter.setPen(QPen(border_color, 1))
                painter.drawEllipse(8, i * cell_size + 8, 9, 9)
                
                # Деревянные доски
                if i < self.ship_size - 1:
                    painter.setPen(QPen(detail_color, 1, Qt.DashLine))
                    painter.drawLine(5, i * cell_size + cell_size, 20, i * cell_size + cell_size)
            
            # Нос корабля
            painter.setBrush(QBrush(ship_color))
            painter.setPen(QPen(border_color, 2))
            painter.drawPolygon([
                QPoint(0, height - 5),
                QPoint(width // 2, height),
                QPoint(width, height - 5)
            ])
            
            # Добавляем текстуру дерева
            for i in range(self.ship_size):
                for j in range(3):
                    painter.setPen(QPen(detail_color, 1))
                    painter.drawLine(5, i * cell_size + 5 + j * 7, 20, i * cell_size + 5 + j * 7)

class ShipPlacementScreen(QMainWindow):
    def __init__(self):
        super().__init__()
        self.placed_ships = []
        self.available_ships = []
        self.initUI()
        
    def initUI(self):
        self.setWindowTitle('Расстановка кораблей')
        self.setFixedSize(1000, 700)
        
        # Create central widget and main layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(20, 50, 20, 20)
        
        # Create game board
        board_widget = QWidget()
        board_widget.setObjectName("game_board")  # Добавляем имя для поиска
        board_layout = QVBoxLayout(board_widget)
        board_layout.setSpacing(20)
        
        # Add board title
        board_title = QLabel("Расстановка кораблей")
        board_title.setAlignment(Qt.AlignCenter)
        board_title.setStyleSheet("""
            QLabel {
                color: white;
                font-size: 24px;
                font-weight: bold;
                text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.5);
            }
        """)
        board_layout.addWidget(board_title)
        
        # Create grid layout
        grid_layout = QGridLayout()
        grid_layout.setSpacing(1)
        
        # Add column labels (A-K)
        for i, letter in enumerate('АБВГДЕЖЗИК'):
            label = QLabel(letter)
            label.setAlignment(Qt.AlignCenter)
            label.setStyleSheet("""
                QLabel {
                    color: white;
                    font-weight: bold;
                    font-size: 16px;
                    padding: 5px;
                }
            """)
            grid_layout.addWidget(label, 0, i + 1)
        
        # Add row labels (1-10)
        for i in range(1, 11):
            label = QLabel(str(i))
            label.setAlignment(Qt.AlignCenter)
            label.setStyleSheet("""
                QLabel {
                    color: white;
                    font-weight: bold;
                    font-size: 16px;
                    padding: 5px;
                }
            """)
            grid_layout.addWidget(label, i, 0)
        
        # Create grid cells
        self.cells = {}
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
                grid_layout.addWidget(cell, row, col)
                self.cells[(row, col)] = cell
        
        board_layout.addLayout(grid_layout)
        
        # Create right panel
        right_panel = QWidget()
        right_panel.setObjectName("ship_panel")  # Добавляем имя для поиска
        right_layout = QVBoxLayout(right_panel)
        right_layout.setSpacing(30)
        
        # Create ship container
        ship_container = QWidget()
        ship_container_layout = QVBoxLayout(ship_container)
        ship_container_layout.setSpacing(15)
        ship_container_layout.setContentsMargins(5, 5, 5, 5)
        
        # Add ship buttons
        ships = [
            ("4-палубный", 4, 1),
            ("3-палубный", 3, 2),
            ("2-палубный", 2, 3),
            ("1-палубный", 1, 4)
        ]
        
        for ship_name, size, count in ships:
            ship_group = QWidget()
            ship_group_layout = QVBoxLayout(ship_group)
            ship_group_layout.setSpacing(5)
            ship_group_layout.setContentsMargins(0, 0, 0, 0)
            
            # Add ship name and count
            name_label = QLabel(f"{ship_name} (x{count})")
            name_label.setStyleSheet("""
                QLabel {
                    color: white;
                    font-size: 14px;
                    font-weight: bold;
                }
            """)
            ship_group_layout.addWidget(name_label)
            
            # Add ship previews
            previews_widget = QWidget()
            previews_layout = QHBoxLayout(previews_widget)
            previews_layout.setSpacing(10)
            previews_layout.setContentsMargins(0, 0, 0, 0)
            
            for _ in range(count):
                preview = ShipPreview(size, previews_widget)
                preview.ship_size = size
                preview.ship_name = ship_name
                self.available_ships.append(preview)
                previews_layout.addWidget(preview)
            
            previews_layout.addStretch()
            ship_group_layout.addWidget(previews_widget)
            ship_container_layout.addWidget(ship_group)
        
        right_layout.addWidget(ship_container)
        
        # Add control buttons
        control_panel = QWidget()
        control_layout = QVBoxLayout(control_panel)
        control_layout.setSpacing(15)
        
        random_btn = QPushButton("Случайно")
        clear_btn = QPushButton("Очистить")
        start_btn = QPushButton("Начать игру")
        back_btn = QPushButton("Назад")
        
        button_style = """
            QPushButton {
                background-color: rgba(74, 74, 74, 180);
                color: white;
                border: 2px solid #666666;
                border-radius: 5px;
                padding: 12px;
                font-size: 16px;
                min-width: 200px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: rgba(102, 102, 102, 180);
            }
        """
        
        random_btn.setStyleSheet(button_style)
        clear_btn.setStyleSheet(button_style)
        start_btn.setStyleSheet(button_style)
        back_btn.setStyleSheet(button_style)
        
        # Connect buttons
        random_btn.clicked.connect(self.random_placement)
        clear_btn.clicked.connect(self.clear_board)
        start_btn.clicked.connect(self.start_game)
        back_btn.clicked.connect(self.go_back)
        
        control_layout.addWidget(random_btn)
        control_layout.addWidget(clear_btn)
        control_layout.addWidget(start_btn)
        control_layout.addWidget(back_btn)
        
        right_layout.addWidget(control_panel)
        
        # Add widgets to main layout
        main_layout.addWidget(board_widget)
        main_layout.addWidget(right_panel)
        
        # Set background
        self.set_background()
        
    def try_place_ship(self, ship):
        # Получаем позицию центра корабля относительно игрового поля
        game_board = self.findChild(QWidget, "game_board")
        if not game_board:
            return False
            
        center_pos = ship.mapTo(game_board, ship.rect().center())
        
        # Находим клетку под центром корабля
        target_cell = None
        target_pos = None
        
        for pos, cell in self.cells.items():
            cell_rect = cell.geometry()
            if cell_rect.contains(center_pos):
                target_cell = cell
                target_pos = pos
                break
        
        if target_cell and target_pos:
            # Проверяем возможность размещения
            if self.can_place_ship(ship, target_pos):
                # Размещаем корабль
                self.place_ship(ship, target_pos)
                return True
        
        return False
        
    def can_place_ship(self, ship, start_pos):
        row, col = start_pos
        size = ship.ship_size
        is_horizontal = ship.is_horizontal
        
        # Проверяем, помещается ли корабль на поле
        if is_horizontal:
            if col + size - 1 > 10:
                return False
        else:
            if row + size - 1 > 10:
                return False
        
        # Проверяем каждую клетку корабля и вокруг неё
        for i in range(size):
            if is_horizontal:
                current_row, current_col = row, col + i
            else:
                current_row, current_col = row + i, col
            
            # Проверяем саму клетку
            if (current_row, current_col) not in self.cells:
                return False
                
            cell_style = self.cells[(current_row, current_col)].styleSheet()
            if "background-color: transparent" in cell_style:
                return False
            
            # Проверяем соседние клетки
            for r in range(max(1, current_row - 1), min(11, current_row + 2)):
                for c in range(max(1, current_col - 1), min(11, current_col + 2)):
                    if (r, c) not in self.cells:
                        continue
                    cell_style = self.cells[(r, c)].styleSheet()
                    if "background-color: transparent" in cell_style:
                        return False
        
        return True
        
    def place_ship(self, ship, start_pos):
        row, col = start_pos
        size = ship.ship_size
        is_horizontal = ship.is_horizontal
        
        # Создаем один виджет корабля для всего корабля
        ship_cell = ShipPreview(size)
        ship_cell.is_horizontal = is_horizontal
        
        # Вычисляем размеры и позицию корабля
        if is_horizontal:
            ship_cell.setFixedSize(size * 40, 40)
            # Находим первую клетку корабля
            first_cell = self.cells[(row, col)]
            # Размещаем корабль на первой клетке
            ship_cell.setParent(first_cell)
            ship_cell.move(0, 0)
        else:
            ship_cell.setFixedSize(40, size * 40)
            # Находим первую клетку корабля
            first_cell = self.cells[(row, col)]
            # Размещаем корабль на первой клетке
            ship_cell.setParent(first_cell)
            ship_cell.move(0, 0)
        
        # Устанавливаем стиль для всех клеток корабля
        for i in range(size):
            if is_horizontal:
                current_pos = (row, col + i)
            else:
                current_pos = (row + i, col)
            
            cell = self.cells[current_pos]
            cell.setStyleSheet("""
                QPushButton {
                    background-color: transparent;
                    border: 1px solid rgba(255, 255, 255, 50);
                }
            """)
        
        # Показываем корабль
        ship_cell.raise_()
        ship_cell.update()
        
        # Удаляем корабль из доступных
        if ship in self.available_ships:
            self.available_ships.remove(ship)
            ship.hide()
        
        # Добавляем в список размещенных кораблей
        self.placed_ships.append((start_pos, size, is_horizontal))
        
    def random_placement(self):
        self.clear_board()
        ships = [(4, 1), (3, 2), (2, 3), (1, 4)]
        
        for size, count in ships:
            for _ in range(count):
                attempts = 0
                while attempts < 100:
                    row = random.randint(1, 10)
                    col = random.randint(1, 10)
                    is_horizontal = random.choice([True, False])
                    
                    # Создаем временный корабль для проверки
                    temp_ship = ShipPreview(size)
                    temp_ship.ship_size = size
                    temp_ship.is_horizontal = is_horizontal
                    
                    if self.can_place_ship(temp_ship, (row, col)):
                        # Создаем один виджет корабля для всего корабля
                        ship_cell = ShipPreview(size)
                        ship_cell.is_horizontal = is_horizontal
                        
                        # Вычисляем размеры и позицию корабля
                        if is_horizontal:
                            ship_cell.setFixedSize(size * 40, 40)
                            # Находим первую клетку корабля
                            first_cell = self.cells[(row, col)]
                            # Размещаем корабль на первой клетке
                            ship_cell.setParent(first_cell)
                            ship_cell.move(0, 0)
                        else:
                            ship_cell.setFixedSize(40, size * 40)
                            # Находим первую клетку корабля
                            first_cell = self.cells[(row, col)]
                            # Размещаем корабль на первой клетке
                            ship_cell.setParent(first_cell)
                            ship_cell.move(0, 0)
                        
                        # Устанавливаем стиль для всех клеток корабля
                        for i in range(size):
                            if is_horizontal:
                                current_pos = (row, col + i)
                            else:
                                current_pos = (row + i, col)
                            
                            cell = self.cells[current_pos]
                            cell.setStyleSheet("""
                                QPushButton {
                                    background-color: transparent;
                                    border: 1px solid rgba(255, 255, 255, 50);
                                }
                            """)
                        
                        # Показываем корабль
                        ship_cell.raise_()
                        ship_cell.update()  # Принудительно обновляем отрисовку
                        
                        self.placed_ships.append(((row, col), size, is_horizontal))
                        break
                    
                    attempts += 1
                    
                    # Если не удалось разместить корабль после 100 попыток, пропускаем его
                    if attempts >= 100:
                        break
        
    def clear_board(self):
        # Очищаем все клетки
        for cell in self.cells.values():
            # Удаляем все дочерние виджеты (корабли)
            for child in cell.children():
                child.deleteLater()
            
            # Восстанавливаем стиль клетки
            cell.setStyleSheet("""
                QPushButton {
                    background-color: rgba(255, 255, 255, 30);
                    border: 1px solid rgba(255, 255, 255, 50);
                }
                QPushButton:hover {
                    background-color: rgba(255, 255, 255, 50);
                }
            """)
        
        # Показываем все доступные корабли
        for ship in self.available_ships:
            ship.setParent(ship.parent())
        
        # Очищаем список размещенных кораблей
        self.placed_ships = []
        
    def start_game(self):
        # Проверяем, размещены ли все корабли
        if len(self.placed_ships) == 10:  # 1+2+3+4 = 10 кораблей всего
            from game_screen import GameScreen
            self.game_screen = GameScreen(self.placed_ships)
            self.game_screen.show()
            self.close()
        
    def set_background(self):
        background_path = "assets/ship_placement_background.jpg"
        if os.path.exists(background_path):
            palette = QPalette()
            pixmap = QPixmap(background_path)
            if not pixmap.isNull():
                scaled_pixmap = pixmap.scaled(self.size(), Qt.KeepAspectRatioByExpanding, Qt.SmoothTransformation)
                palette.setBrush(QPalette.Window, QBrush(scaled_pixmap))
                self.setPalette(palette)
                return
        
        # If background loading fails, set default gradient background
        self.setStyleSheet("""
            QMainWindow {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                          stop:0 #1a237e, stop:1 #0d47a1);
            }
        """)
        
    def go_back(self):
        from main import MainMenu
        self.main_menu = MainMenu()
        self.main_menu.show()
        self.close() 