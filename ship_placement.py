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
        self.is_valid_placement = True
        self.setCursor(Qt.OpenHandCursor)
        self.is_placed = False
        self.current_cells = []
        
    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.is_dragging = True
            self.drag_start_pos = event.pos()
            self.original_pos = self.pos()
            self.original_parent = self.parent()
            self.setCursor(Qt.ClosedHandCursor)
            self.raise_()
            
            # Если корабль уже размещен, удаляем его с текущей позиции
            if self.is_placed:
                self.remove_from_board()
            
    def mouseMoveEvent(self, event):
        if self.is_dragging:
            # Перемещаем корабль относительно курсора
            new_pos = self.mapToParent(event.pos() - self.drag_start_pos)
            
            # Ограничиваем перемещение границами родительского виджета
            parent_rect = self.parent().rect()
            new_x = max(0, min(new_pos.x(), parent_rect.width() - self.width()))
            new_y = max(0, min(new_pos.y(), parent_rect.height() - self.height()))
            self.move(new_x, new_y)
            
    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton and self.is_dragging:
            self.is_dragging = False
            self.setCursor(Qt.OpenHandCursor)
            
            # Проверяем, находится ли корабль над игровым полем
            game_board = self.parent().findChild(QWidget, "game_board")
            if game_board:
                # Получаем позицию центра корабля относительно игрового поля
                center_pos = self.mapTo(game_board, self.rect().center())
                if game_board.geometry().contains(center_pos):
                    # Находим ближайшую клетку
                    target_cell = None
                    target_pos = None
                    min_distance = float('inf')
                    
                    for pos, cell in self.parent().cells.items():
                        cell_center = cell.rect().center()
                        cell_center_global = cell.mapTo(game_board, cell_center)
                        distance = (center_pos - cell_center_global).manhattanLength()
                        
                        if distance < min_distance:
                            min_distance = distance
                            target_cell = cell
                            target_pos = pos
                    
                    if target_cell and self.parent().can_place_ship(self, target_pos):
                        # Размещаем корабль
                        self.parent().place_ship(self, target_pos)
                        self.is_placed = True
                    else:
                        self.return_to_original_position()
                else:
                    self.return_to_original_position()
            else:
                self.return_to_original_position()
            
            # Восстанавливаем стиль
            self.setStyleSheet("""
                QWidget {
                    background-color: transparent;
                    border: none;
                }
            """)
    
    def return_to_original_position(self):
        if self.original_parent:
            self.setParent(self.original_parent)
            self.move(self.original_pos)
            self.raise_()
            self.is_placed = False
    
    def remove_from_board(self):
        # Восстанавливаем стиль клеток
        for cell in self.current_cells:
            cell.setStyleSheet("""
                QPushButton {
                    background-color: rgba(255, 255, 255, 30);
                    border: 1px solid rgba(255, 255, 255, 50);
                }
                QPushButton:hover {
                    background-color: rgba(255, 255, 255, 50);
                }
            """)
        
        # Удаляем корабль из списка размещенных
        if self in self.parent().placed_ships:
            self.parent().placed_ships.remove(self)
        
        self.current_cells = []
        self.is_placed = False
            
    def rotate(self):
        if not self.is_dragging:  # Разрешаем поворот только когда корабль не перетаскивается
            self.is_horizontal = not self.is_horizontal
            if self.is_horizontal:
                self.setFixedSize(self.ship_size * 25, 25)
            else:
                self.setFixedSize(25, self.ship_size * 25)
            
            # Если корабль размещен, обновляем его позицию
            if self.is_placed:
                self.remove_from_board()
                # Пытаемся разместить корабль снова с новой ориентацией
                game_board = self.parent().findChild(QWidget, "game_board")
                if game_board:
                    center_pos = self.mapTo(game_board, self.rect().center())
                    if game_board.geometry().contains(center_pos):
                        for pos, cell in self.parent().cells.items():
                            cell_center = cell.rect().center()
                            cell_center_global = cell.mapTo(game_board, cell_center)
                            if (center_pos - cell_center_global).manhattanLength() < 50:  # Порог расстояния
                                if self.parent().can_place_ship(self, pos):
                                    self.parent().place_ship(self, pos)
                                    self.is_placed = True
                                break
            
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
    FIELD_SIZE = 10
    SHIPS_SET = [(4, 1), (3, 2), (2, 3), (1, 4)]

    def __init__(self):
        super().__init__()
        self.setWindowTitle('Расстановка кораблей')
        self.setFixedSize(1000, 700)
        self.placed_ships = []  # [{'widget': ShipPreview, 'row': int, 'col': int, 'horizontal': bool}]
        self.available_ships = []  # ShipPreview
        self.board = [[0 for _ in range(self.FIELD_SIZE)] for _ in range(self.FIELD_SIZE)]
        self.initUI()

    def initUI(self):
        """Создание и настройка экрана расстановки кораблей"""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(20, 50, 20, 20)

        # Игровое поле
        board_widget = QWidget()
        board_widget.setObjectName('game_board')
        board_layout = QVBoxLayout(board_widget)
        board_layout.setSpacing(10)
        board_title = QLabel('Расстановка кораблей')
        board_title.setAlignment(Qt.AlignCenter)
        board_title.setStyleSheet('color: white; font-size: 24px; font-weight: bold;')
        board_layout.addWidget(board_title)
        grid_layout = QGridLayout()
        grid_layout.setSpacing(1)
        # Подписи столбцов
        for i, letter in enumerate('АБВГДЕЖЗИК'):
            label = QLabel(letter)
            label.setAlignment(Qt.AlignCenter)
            label.setStyleSheet('color: white; font-weight: bold; font-size: 16px;')
            grid_layout.addWidget(label, 0, i + 1)
        # Подписи строк
        for i in range(1, 11):
            label = QLabel(str(i))
            label.setAlignment(Qt.AlignCenter)
            label.setStyleSheet('color: white; font-weight: bold; font-size: 16px;')
            grid_layout.addWidget(label, i, 0)
        # Клетки поля
        self.cells = {}
        for row in range(1, 11):
            for col in range(1, 11):
                cell = QPushButton()
                cell.setFixedSize(40, 40)
                cell.setStyleSheet('background-color: rgba(255,255,255,30); border: 1px solid rgba(255,255,255,50);')
                cell.setAcceptDrops(True)
                cell.row = row - 1
                cell.col = col - 1
                cell.enterEvent = lambda e, r=row-1, c=col-1: self.cell_hover_enter(r, c)
                cell.leaveEvent = lambda e, r=row-1, c=col-1: self.cell_hover_leave(r, c)
                cell.dragEnterEvent = self.cell_drag_enter
                cell.dropEvent = self.cell_drop
                grid_layout.addWidget(cell, row, col)
                self.cells[(row-1, col-1)] = cell
        board_layout.addLayout(grid_layout)
        main_layout.addWidget(board_widget)

        # Панель кораблей
        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)
        right_layout.setSpacing(30)
        ship_container = QWidget()
        ship_container_layout = QVBoxLayout(ship_container)
        ship_container_layout.setSpacing(15)
        ship_container_layout.setContentsMargins(5, 5, 5, 5)
        self.ship_previews = []
        for size, count in self.SHIPS_SET:
            for _ in range(count):
                ship = ShipPreview(size, ship_container)
                ship.setFixedSize(size * 40, 40)
                ship.is_horizontal = True
                ship.setCursor(Qt.OpenHandCursor)
                ship.mousePressEvent = lambda e, s=ship: self.start_drag_ship(e, s)
                ship.mouseDoubleClickEvent = lambda e, s=ship: self.rotate_ship(e, s)
                self.available_ships.append(ship)
                self.ship_previews.append(ship)
                ship_container_layout.addWidget(ship)
        right_layout.addWidget(ship_container)
        # Панель управления
        control_panel = QWidget()
        control_layout = QVBoxLayout(control_panel)
        control_layout.setSpacing(15)
        random_btn = QPushButton('Случайно')
        clear_btn = QPushButton('Очистить')
        start_btn = QPushButton('Начать игру')
        back_btn = QPushButton('Назад')
        for btn in [random_btn, clear_btn, start_btn, back_btn]:
            btn.setStyleSheet('background-color: rgba(74,74,74,180); color: white; border: 2px solid #666666; border-radius: 5px; padding: 12px; font-size: 16px; min-width: 200px; font-weight: bold;')
        random_btn.clicked.connect(self.random_placement)
        clear_btn.clicked.connect(self.clear_board)
        start_btn.clicked.connect(self.start_game)
        back_btn.clicked.connect(self.go_back)
        self.start_btn = start_btn
        control_layout.addWidget(random_btn)
        control_layout.addWidget(clear_btn)
        control_layout.addWidget(start_btn)
        control_layout.addWidget(back_btn)
        right_layout.addWidget(control_panel)
        main_layout.addWidget(right_panel)
        self.set_background()
        self.update_start_btn()

    # Drag & Drop логика
    def start_drag_ship(self, event, ship):
        if event.button() == Qt.LeftButton:
            self.dragged_ship = ship
            ship.raise_()
            ship.setCursor(Qt.ClosedHandCursor)
            ship.mouseMoveEvent = lambda e, s=ship: self.drag_ship(e, s)
            ship.mouseReleaseEvent = lambda e, s=ship: self.drop_ship(e, s)
            self.drag_offset = event.pos()

    def drag_ship(self, event, ship):
        if event.buttons() & Qt.LeftButton:
            new_pos = ship.mapToParent(event.pos() - self.drag_offset)
            ship.move(new_pos)

    def drop_ship(self, event, ship):
        ship.setCursor(Qt.OpenHandCursor)
        ship.mouseMoveEvent = None
        ship.mouseReleaseEvent = None
        # Проверяем, над какой клеткой отпустили
        for (row, col), cell in self.cells.items():
            cell_rect = cell.geometry()
            cell_pos = cell.mapToGlobal(QPoint(0, 0))
            ship_pos = ship.mapToGlobal(QPoint(0, 0))
            if (cell_pos.x() <= ship_pos.x() <= cell_pos.x() + cell_rect.width() and
                cell_pos.y() <= ship_pos.y() <= cell_pos.y() + cell_rect.height()):
                if self.can_place_ship(row, col, ship.ship_size, ship.is_horizontal):
                    self.place_ship_on_board(ship, row, col)
                    return
        # Если не удалось разместить — возвращаем на панель
        self.return_ship_to_panel(ship)

    def cell_hover_enter(self, row, col):
        pass  # Здесь можно реализовать визуальную подсветку
    def cell_hover_leave(self, row, col):
        pass
    def cell_drag_enter(self, event):
        event.accept()
    def cell_drop(self, event):
        event.accept()

    def rotate_ship(self, event, ship):
        if event.button() == Qt.LeftButton or event.button() == Qt.RightButton:
            ship.is_horizontal = not ship.is_horizontal
            if ship.is_horizontal:
                ship.setFixedSize(ship.ship_size * 40, 40)
            else:
                ship.setFixedSize(40, ship.ship_size * 40)

    def can_place_ship(self, row, col, size, is_horizontal):
        # Проверка границ поля
        if is_horizontal:
            if col + size > self.FIELD_SIZE:
                return False
        else:
            if row + size > self.FIELD_SIZE:
                return False
        # Проверка на соприкосновение с другими кораблями
        for i in range(size):
            r = row + (0 if is_horizontal else i)
            c = col + (i if is_horizontal else 0)
            for dr in [-1, 0, 1]:
                for dc in [-1, 0, 1]:
                    nr, nc = r + dr, c + dc
                    if 0 <= nr < self.FIELD_SIZE and 0 <= nc < self.FIELD_SIZE:
                        if self.board[nr][nc] != 0:
                            return False
        return True

    def place_ship_on_board(self, ship, row, col):
        # Удаляем с панели, если нужно
        if ship in self.available_ships:
            self.available_ships.remove(ship)
        # Снимаем с предыдущего места, если нужно
        for s in self.placed_ships:
            if s['widget'] == ship:
                self.remove_ship_from_board(ship)
        # Обновляем board (занимаем клетки)
        for i in range(ship.ship_size):
            r = row + (0 if ship.is_horizontal else i)
            c = col + (i if ship.is_horizontal else 0)
            self.board[r][c] = 1
        # Перемещаем виджет корабля на поле
        first_cell = self.cells[(row, col)]
        cell_pos = first_cell.mapTo(self, QPoint(0, 0))
        ship.setParent(self)
        ship.move(cell_pos)
        ship.show()
        ship.raise_()
        self.placed_ships.append({'widget': ship, 'row': row, 'col': col, 'horizontal': ship.is_horizontal})
        self.update_start_btn()

    def remove_ship_from_board(self, ship):
        # Находим и удаляем корабль с board
        for s in self.placed_ships:
            if s['widget'] == ship:
                row, col, horizontal, size = s['row'], s['col'], s['horizontal'], ship.ship_size
                for i in range(size):
                    r = row + (0 if horizontal else i)
                    c = col + (i if horizontal else 0)
                    self.board[r][c] = 0
                self.placed_ships.remove(s)
                break
        self.update_start_btn()

    def return_ship_to_panel(self, ship):
        # Возвращаем корабль на панель
        ship.setParent(self.ship_previews[0].parent())
        ship.show()
        ship.raise_()
        self.available_ships.append(ship)
        self.remove_ship_from_board(ship)

    def random_placement(self):
        self.clear_board()
        ships = []
        for size, count in self.SHIPS_SET:
            ships += [size] * count
        random.shuffle(ships)
        for size in ships:
            placed = False
            for _ in range(100):
                row = random.randint(0, self.FIELD_SIZE-1)
                col = random.randint(0, self.FIELD_SIZE-1)
                is_horizontal = random.choice([True, False])
                if self.can_place_ship(row, col, size, is_horizontal):
                    # Находим нужный ShipPreview
                    for ship in self.available_ships:
                        if ship.ship_size == size:
                            ship.is_horizontal = is_horizontal
                            self.place_ship_on_board(ship, row, col)
                            placed = True
                            break
                if placed:
                    break

    def clear_board(self):
        # Очищаем всё поле и возвращаем все корабли на панель
        self.board = [[0 for _ in range(self.FIELD_SIZE)] for _ in range(self.FIELD_SIZE)]
        for s in self.placed_ships[:]:
            self.return_ship_to_panel(s['widget'])
        self.placed_ships = []
        self.update_start_btn()

    def start_game(self):
        # Проверяем, все ли корабли размещены
        if len(self.placed_ships) == sum(c for _, c in self.SHIPS_SET):
            ships = [(s['row']+1, s['col']+1, s['widget'].ship_size, s['widget'].is_horizontal) for s in self.placed_ships]
            from game_screen import GameScreen
            self.game_screen = GameScreen(ships)
            self.game_screen.show()
            self.close()

    def update_start_btn(self):
        # Кнопка "Начать игру" активна только если все корабли размещены
        self.start_btn.setEnabled(len(self.placed_ships) == sum(c for _, c in self.SHIPS_SET))

    def set_background(self):
        """Установка фонового изображения для экрана расстановки кораблей"""
        background_path = 'assets/ship_placement_background.jpg'
        if os.path.exists(background_path):
            palette = QPalette()
            pixmap = QPixmap(background_path)
            if not pixmap.isNull():
                scaled_pixmap = pixmap.scaled(self.size(), Qt.KeepAspectRatioByExpanding, Qt.SmoothTransformation)
                palette.setBrush(QPalette.Window, QBrush(scaled_pixmap))
                self.setPalette(palette)
                return
        self.setStyleSheet('QMainWindow {background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #1a237e, stop:1 #0d47a1);} ')

    def go_back(self):
        """Переход в главное меню"""
        from main import MainMenu
        self.main_menu = MainMenu()
        self.main_menu.show()
        self.close()