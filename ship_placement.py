from PyQt5.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                           QPushButton, QLabel, QGridLayout, QMessageBox,
                           QFrame, QSizePolicy)
from PyQt5.QtCore import Qt, QSize, QPoint, QRect, QMimeData
from PyQt5.QtGui import QPixmap, QPalette, QBrush, QColor, QPainter, QPen, QCursor, QFont, QDrag
import os
import random
from PyQt5.QtWidgets import QApplication
import sys

def resource_path(relative_path):
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath('.'), relative_path)

class ShipPreview(QWidget):
    def __init__(self, size, parent=None, placement_screen=None):
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
        self.is_invalid_position = False
        self.field_cell_size = 40
        self.placement_screen = placement_screen
        self.current_row = -1
        self.current_col = -1
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setAttribute(Qt.WA_NoSystemBackground)
        self.setAttribute(Qt.WA_OpaquePaintEvent)
        self.setFocusPolicy(Qt.StrongFocus)
        self._drag_start_pos = None
        self._drag_initiated = False
        self.is_template = True  # Для шаблонных кораблей на панели
        self.is_temp_dragged = False  # True для временного экземпляра
        
    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            if self.is_template and not self.is_placed:
                self._drag_start_pos = event.pos()
                self._drag_initiated = False
            elif self.is_placed:
                # Запрещаем любые действия с уже выставленным кораблем
                return

    def mouseMoveEvent(self, event):
        if self.is_template and not self.is_placed and self._drag_start_pos is not None:
            if (event.pos() - self._drag_start_pos).manhattanLength() > QApplication.startDragDistance():
                if not self._drag_initiated:
                    self._drag_initiated = True
                    if self.placement_screen:
                        self.placement_screen.start_drag_ship(event, self, from_field=False)

        if self.is_dragging and self.is_temp_dragged:
            # Найти ближайшую клетку
            if self.placement_screen:
                game_board = self.placement_screen.findChild(QWidget, "game_board")
                if game_board:
                    global_mouse = self.mapToGlobal(event.pos())
                    board_mouse = game_board.mapFromGlobal(global_mouse)
                    min_dist = float('inf')
                    snap_pos = None
                    for (row, col), cell in self.placement_screen.cells.items():
                        cell_center = cell.rect().center()
                        cell_center_global = cell.mapTo(game_board, cell_center)
                        dist = (board_mouse - cell_center_global).manhattanLength()
                        if dist < min_dist:
                            min_dist = dist
                            snap_pos = (row, col, cell)
                    if snap_pos:
                        row, col, cell = snap_pos
                        # Позиционируем корабль по левому верхнему углу клетки
                        cell_pos = cell.mapTo(self.placement_screen, QPoint(0, 0))
                        self.move(cell_pos)
                        # Подсветка
                        can_place = self.placement_screen.can_place_ship(row, col, self.ship_size, self.is_horizontal)
                        self.highlight_ship_cells(row, col, can_place)
                        self.is_valid_placement = can_place
                        self.is_invalid_position = not can_place
                        self.update()
                        self._snap_row = row
                        self._snap_col = col
                    else:
                        self.highlight_ship_cells(-1, -1, False)
                        self.is_valid_placement = True
                        self.is_invalid_position = False
                        self.update()
                        self._snap_row = None
                        self._snap_col = None

    def mouseReleaseEvent(self, event):
        if self.is_dragging and self.is_temp_dragged:
            self.is_dragging = False
            self.setCursor(Qt.OpenHandCursor)
            placed = False
            if hasattr(self, '_snap_row') and self._snap_row is not None and self._snap_col is not None:
                if self.placement_screen and self.placement_screen.can_place_ship(self._snap_row, self._snap_col, self.ship_size, self.is_horizontal):
                    placed = self.placement_screen.try_place_dragged_ship(self, self._snap_row, self._snap_col)
            if not placed:
                # Если не удалось разместить — удалить экземпляр и вернуть счетчик, если drag был с панели
                if hasattr(self, 'from_panel') and self.from_panel:
                    self.placement_screen.update_ship_count(self.ship_size, 1)
                    self.placement_screen.available_ships[self.ship_size]['template'].setVisible(True)
                self.deleteLater()

    def return_to_original_position(self):
        """Возврат корабля на исходную позицию"""
        if self.original_parent and self.original_pos:
            self.setParent(self.original_parent)
            self.move(self.original_pos)
            self.show()
            self.is_valid_placement = True
            self.is_invalid_position = False
            self.update()

    def mouseDoubleClickEvent(self, event):
        """Поворот корабля при двойном клике"""
        if not self.is_placed:
            self.is_horizontal = not self.is_horizontal
            if self.is_horizontal:
                self.setFixedSize(self.ship_size * 25, 25)
            else:
                self.setFixedSize(25, self.ship_size * 25)
            self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        if self.is_invalid_position:
            ship_color = QColor(255, 100, 100)
            border_color = QColor(200, 50, 50)
            detail_color = QColor(180, 40, 40)
        else:
            ship_color = QColor(210, 180, 140)
            border_color = QColor(139, 69, 19)
            detail_color = QColor(160, 82, 45)
        
        width = self.width()
        height = self.height()
        
        # Определяем размер клетки в зависимости от контекста
        cell_size = self.field_cell_size if self.is_placed else 25
        
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
            
    def rotate(self):
        """Поворот корабля"""
        if not self.is_placed:
            self.is_horizontal = not self.is_horizontal
            if self.is_horizontal:
                self.setFixedSize(self.ship_size * 25, 25)
            else:
                self.setFixedSize(25, self.ship_size * 25)
            self.update()

    def place_on_field(self, row, col):
        """Размещение корабля на поле"""
        self.is_placed = True
        self.current_row = row
        self.current_col = col
        
        # Устанавливаем размеры для поля
        if self.is_horizontal:
            self.setFixedSize(self.ship_size * self.field_cell_size, self.field_cell_size)
        else:
            self.setFixedSize(self.field_cell_size, self.ship_size * self.field_cell_size)
        
        # Позиционируем корабль
        first_cell = self.placement_screen.cells[(row, col)]
        cell_pos = first_cell.mapTo(self.placement_screen, QPoint(0, 0))
        
        # Устанавливаем родителя и позицию
        self.setParent(self.placement_screen)
        self.move(cell_pos)
        self.raise_()
        self.show()
        self.update()

    def return_to_panel(self):
        """Возврат корабля на панель"""
        self.is_placed = False
        self.is_horizontal = True  # Возвращаем в горизонтальное положение
        self.current_row = -1
        self.current_col = -1
        self.setFixedSize(self.ship_size * 25, 25)  # Возвращаем горизонтальный размер
        
        if self.original_parent and self.original_pos:
            self.setParent(self.original_parent)
            self.move(self.original_pos)
            self.raise_()
            self.update()

    def highlight_ship_cells(self, row, col, is_valid):
        """Подсветка клеток при перетаскивании корабля"""
        # Сбрасываем предыдущую подсветку
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
        
        self.current_cells = []
        
        if row >= 0 and col >= 0:
            # Подсвечиваем новые клетки
            for i in range(self.ship_size):
                r = row + (0 if self.is_horizontal else i)
                c = col + (i if self.is_horizontal else 0)
                if 0 <= r < 10 and 0 <= c < 10:
                    cell = self.placement_screen.cells.get((r, c))
                    if cell:
                        self.current_cells.append(cell)
                        if is_valid:
                            cell.setStyleSheet("""
                                QPushButton {
                                    background-color: rgba(0, 255, 0, 50);
                                    border: 1px solid rgba(0, 255, 0, 100);
                                }
                                QPushButton:hover {
                                    background-color: rgba(0, 255, 0, 70);
                                }
                            """)
                        else:
                            cell.setStyleSheet("""
                                QPushButton {
                                    background-color: rgba(255, 0, 0, 50);
                                    border: 1px solid rgba(255, 0, 0, 100);
                                }
                                QPushButton:hover {
                                    background-color: rgba(255, 0, 0, 70);
                                }
                            """)

    def keyPressEvent(self, event):
        # Поворот по R или русской К
        if event.key() == Qt.Key_R or event.text().upper() == 'К':
            if self.is_dragging and self.is_temp_dragged:
                self.rotate()
                if self.placement_screen:
                    self.placement_screen.snap_dragged_ship(self)

class ShipPlacementScreen(QMainWindow):
    FIELD_SIZE = 10
    SHIPS_SET = [(4, 1), (3, 2), (2, 3), (1, 4)]  # (размер, количество)
    field_cell_size = 40  # Размер клетки на поле

    def __init__(self):
        super().__init__()
        self.setWindowTitle('Расстановка кораблей')
        self.setFixedSize(1000, 700)
        self.placed_ships = []
        self.available_ships = {}
        self.board = [[0 for _ in range(self.FIELD_SIZE)] for _ in range(self.FIELD_SIZE)]
        self.dragged_ship = None
        self.drag_offset = None
        self.initUI()
        self.setFocusPolicy(Qt.StrongFocus)  # Добавляем возможность получать фокус
        
    def initUI(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(20)

        # Игровое поле
        board_container = QWidget()
        board_container.setObjectName('game_board')
        board_layout = QVBoxLayout(board_container)
        board_layout.setSpacing(10)
        
        # Заголовок поля
        board_title = QLabel('Расстановка кораблей')
        board_title.setAlignment(Qt.AlignCenter)
        board_title.setStyleSheet('color: white; font-size: 24px; font-weight: bold;')
        board_layout.addWidget(board_title)
        
        # Сетка поля
        grid_container = QWidget()
        grid_layout = QGridLayout(grid_container)
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
                cell.setStyleSheet("""
                    QPushButton {
                        background-color: rgba(255, 255, 255, 30);
                        border: 1px solid rgba(255, 255, 255, 50);
                    }
                    QPushButton:hover {
                        background-color: rgba(255, 255, 255, 50);
                    }
                """)
                cell.row = row - 1
                cell.col = col - 1
                cell.clicked.connect(lambda checked, r=row-1, c=col-1: self.cell_clicked(r, c))
                grid_layout.addWidget(cell, row, col)
                self.cells[(row-1, col-1)] = cell
        
        board_layout.addWidget(grid_container)
        main_layout.addWidget(board_container)
        
        # Правая панель
        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)
        right_layout.setSpacing(20)
        
        # Панель кораблей
        ships_panel = QFrame()
        ships_panel.setFrameStyle(QFrame.StyledPanel)
        ships_panel.setStyleSheet("""
            QFrame {
                background-color: rgba(0, 0, 0, 100);
                border-radius: 10px;
                border: 2px solid rgba(255, 255, 255, 50);
            }
        """)
        ships_layout = QVBoxLayout(ships_panel)
        ships_layout.setSpacing(15)
        ships_layout.setContentsMargins(10, 10, 10, 10)
        
        # Заголовок панели кораблей
        ships_title = QLabel('Корабли')
        ships_title.setAlignment(Qt.AlignCenter)
        ships_title.setStyleSheet('color: white; font-size: 20px; font-weight: bold;')
        ships_layout.addWidget(ships_title)
        
        # Контейнер для кораблей
        ships_container = QWidget()
        ships_container_layout = QVBoxLayout(ships_container)
        ships_container_layout.setSpacing(15)
        
        # Создаем корабли для каждого размера
        for size, count in self.SHIPS_SET:
            ship_widget = QWidget()
            ship_layout = QHBoxLayout(ship_widget)
            ship_layout.setSpacing(10)
            
            # Контейнер для кораблей одного типа
            ships_group = QWidget()
            ships_group_layout = QVBoxLayout(ships_group)
            ships_group_layout.setSpacing(5)
            ships_group_layout.setContentsMargins(0, 0, 0, 0)
            
            # Создаем общий корабль для отображения
            template_ship = ShipPreview(size, ships_group, self)
            template_ship.setFixedSize(size * 25, 25)
            template_ship.is_horizontal = True
            template_ship.setCursor(Qt.OpenHandCursor)
            template_ship.mousePressEvent = lambda e, s=template_ship: self.start_drag_ship(e, s)
            ships_group_layout.addWidget(template_ship)
            
            # Метка с количеством
            count_label = QLabel(f"x{count}")
            count_label.setStyleSheet('color: white; font-size: 16px; font-weight: bold;')
            
            ship_layout.addWidget(ships_group)
            ship_layout.addWidget(count_label)
            ship_layout.addStretch()
            
            ships_container_layout.addWidget(ship_widget)
            
            # Сохраняем информацию о кораблях
            self.available_ships[size] = {
                'template': template_ship,
                'count': count,
                'label': count_label
            }
            
        ships_layout.addWidget(ships_container)
        right_layout.addWidget(ships_panel)
        
        # Панель управления
        control_panel = QFrame()
        control_panel.setFrameStyle(QFrame.StyledPanel)
        control_panel.setStyleSheet("""
            QFrame {
                background-color: rgba(0, 0, 0, 100);
                border-radius: 10px;
                border: 2px solid rgba(255, 255, 255, 50);
            }
        """)
        control_layout = QVBoxLayout(control_panel)
        control_layout.setSpacing(15)
        control_layout.setContentsMargins(10, 10, 10, 10)
        
        # Статусная строка
        self.status_label = QLabel('Перетащите корабли на поле')
        self.status_label.setAlignment(Qt.AlignCenter)
        self.status_label.setStyleSheet('color: white; font-size: 16px;')
        control_layout.addWidget(self.status_label)
        
        # Счетчик кораблей
        self.ships_counter = QLabel('Осталось: 10 кораблей')
        self.ships_counter.setAlignment(Qt.AlignCenter)
        self.ships_counter.setStyleSheet('color: white; font-size: 16px; font-weight: bold;')
        control_layout.addWidget(self.ships_counter)
        
        # Кнопки управления
        random_btn = QPushButton('Авторасстановка')
        clear_btn = QPushButton('Очистить поле')
        start_btn = QPushButton('Начать игру')
        back_btn = QPushButton('Назад')
        
        for btn in [random_btn, clear_btn, start_btn, back_btn]:
            btn.setStyleSheet("""
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
                    background-color: rgba(94, 94, 94, 180);
                }
                QPushButton:disabled {
                    background-color: rgba(54, 54, 54, 180);
                    color: rgba(255, 255, 255, 128);
                }
            """)
            
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

    def update_ship_count(self, size, delta):
        """Обновление счетчика кораблей"""
        if size in self.available_ships:
            ship_info = self.available_ships[size]
            ship_info['count'] = max(0, ship_info['count'] + delta)
            ship_info['label'].setText(f"x{ship_info['count']}")
            
            # Скрываем шаблонный корабль, если все корабли размещены
            if ship_info['count'] == 0:
                ship_info['template'].setVisible(False)
            else:
                ship_info['template'].setVisible(True)
            
            # Обновляем счетчик
            total_ships = sum(c for _, c in self.SHIPS_SET)
            placed_ships = len(self.placed_ships)
            self.ships_counter.setText(f'Осталось: {total_ships - placed_ships} кораблей')
            
            # Обновляем статус
            if placed_ships == total_ships:
                self.status_label.setText('Все корабли размещены!')
            else:
                self.status_label.setText('Перетащите корабли на поле')

    def dragEnterEvent(self, event):
        if event.mimeData().hasFormat("application/x-ship"):
            event.acceptProposedAction()

    def dragMoveEvent(self, event):
        if event.mimeData().hasFormat("application/x-ship"):
            event.acceptProposedAction()

    def dropEvent(self, event):
        if event.mimeData().hasFormat("application/x-ship"):
            size = int(event.mimeData().data("application/x-ship").data().decode())
            
            # Получаем позицию в координатах игрового поля
            game_board = self.findChild(QWidget, "game_board")
            if game_board:
                pos = event.pos()
                board_pos = game_board.mapFrom(self, pos)
                
                # Находим ближайшую клетку
                target_cell = None
                target_pos = None
                min_distance = float('inf')
                
                for pos, cell in self.cells.items():
                    cell_center = cell.rect().center()
                    cell_center_global = cell.mapTo(game_board, cell_center)
                    distance = (board_pos - cell_center_global).manhattanLength()
                    
                    if distance < min_distance:
                        min_distance = distance
                        target_cell = cell
                        target_pos = pos
                
                if target_cell:
                    # Создаем новый корабль
                    new_ship = ShipPreview(size, self, self)
                    new_ship.setFixedSize(size * self.field_cell_size, self.field_cell_size)
                    new_ship.is_horizontal = True
                    
                    if self.can_place_ship(target_pos[0], target_pos[1], size, True):
                        # Размещаем корабль
                        self.place_ship_on_board(new_ship, target_pos[0], target_pos[1])
                        
                        # Позиционируем корабль на поле
                        first_cell = self.cells[(target_pos[0], target_pos[1])]
                        cell_pos = first_cell.mapToGlobal(QPoint(0, 0))
                        new_ship.move(self.mapFromGlobal(cell_pos))
                        new_ship.show()
                    else:
                        new_ship.deleteLater()
            
            event.acceptProposedAction()

    def cell_clicked(self, row, col):
        """Обработка клика по клетке"""
        # Находим первый доступный корабль
        for size, count in self.SHIPS_SET:
            if self.available_ships[size]['count'] > 0:
                # Создаем новый корабль
                new_ship = ShipPreview(size, self, self)
                new_ship.setFixedSize(size * self.field_cell_size, self.field_cell_size)
                new_ship.is_horizontal = True
                
                if self.can_place_ship(row, col, size, True):
                    # Размещаем корабль
                    self.place_ship_on_board(new_ship, row, col)
                    
                    # Позиционируем корабль на поле
                    first_cell = self.cells[(row, col)]
                    cell_pos = first_cell.mapTo(self, QPoint(0, 0))
                    new_ship.move(cell_pos)
                    new_ship.show()
                else:
                    new_ship.deleteLater()
                break

    def rotate_ship(self, event, ship):
        """Поворот корабля"""
        try:
            if event.button() == Qt.LeftButton and not ship.is_placed:
                ship.rotate()
        except Exception as e:
            print(f"Error in rotate_ship: {e}")

    def can_place_ship(self, row, col, size, is_horizontal):
        if row < 0 or col < 0:
            return False
            
        if is_horizontal:
            if col + size > self.FIELD_SIZE:
                return False
        else:
            if row + size > self.FIELD_SIZE:
                return False
        
        for i in range(size):
            r = row + (0 if is_horizontal else i)
            c = col + (i if is_horizontal else 0)
            
            if self.board[r][c] != 0:
                return False
                
            for dr in [-1, 0, 1]:
                for dc in [-1, 0, 1]:
                    nr, nc = r + dr, c + dc
                    if 0 <= nr < self.FIELD_SIZE and 0 <= nc < self.FIELD_SIZE:
                        if self.board[nr][nc] != 0:
                            return False
        return True
        
    def place_ship_on_board(self, ship, row, col):
        """Размещение корабля на поле"""
        try:
            # Проверяем возможность размещения
            if not self.can_place_ship(row, col, ship.ship_size, ship.is_horizontal):
                ship.return_to_original_position()
                return
            
            # Обновляем board (занимаем клетки)
            for i in range(ship.ship_size):
                r = row + (0 if ship.is_horizontal else i)
                c = col + (i if ship.is_horizontal else 0)
                self.board[r][c] = 1
            
            # Добавляем в список размещенных кораблей
            self.placed_ships.append({
                'row': row,
                'col': col,
                'horizontal': ship.is_horizontal,
                'size': ship.ship_size,
                'widget': ship
            })
            
            # Обновляем счетчик кораблей
            self.update_ship_count(ship.ship_size, -1)
            
            # Позиционируем корабль на поле
            first_cell = self.cells[(row, col)]
            cell_pos = first_cell.mapTo(self, QPoint(0, 0))
            ship.move(cell_pos)
            ship.is_placed = True
            ship.current_row = row
            ship.current_col = col
            ship.show()
            
            # Обновляем отображение
            self.update()
            self.update_start_btn()
            
        except Exception as e:
            print(f"Error placing ship: {e}")
            ship.return_to_original_position()

    def remove_ship_from_board(self, ship):
        """Удаление корабля с поля"""
        try:
            for s in self.placed_ships[:]:
                if (s['row'] == ship.current_row and 
                    s['col'] == ship.current_col and 
                    s['size'] == ship.ship_size and 
                    s['horizontal'] == ship.is_horizontal):
                    # Очищаем клетки на поле
                    for i in range(s['size']):
                        r = s['row'] + (0 if s['horizontal'] else i)
                        c = s['col'] + (i if s['horizontal'] else 0)
                        self.board[r][c] = 0
                        # Снимаем подсветку с клетки
                        cell = self.cells.get((r, c))
                        if cell:
                            cell.setStyleSheet("""
                                QPushButton {
                                    background-color: rgba(255, 255, 255, 30);
                                    border: 1px solid rgba(255, 255, 255, 50);
                                }
                                QPushButton:hover {
                                    background-color: rgba(255, 255, 255, 50);
                                }
                            """)
                    self.placed_ships.remove(s)
                    break
            self.update_start_btn()
            self.update_total_ships_counter()
            self.clear_all_cells_highlight()
        except Exception as e:
            print(f"Error in remove_ship_from_board: {e}")

    def return_ship_to_panel(self, ship):
        """Возврат корабля на панель"""
        try:
            # Удаляем корабль с поля
            self.remove_ship_from_board(ship)
            
            # Возвращаем корабль на панель
            ship.return_to_panel()
            
            # Обновляем счетчик
            self.update_ship_count(ship.ship_size, 1)
            
            # Обновляем интерфейс
            self.update_start_btn()
            self.update()
            
        except Exception as e:
            print(f"Error in return_ship_to_panel: {e}")

    def random_placement(self):
        """Случайная расстановка кораблей"""
        # Удаляем все существующие корабли
        for ship_info in self.placed_ships[:]:
            ship = ship_info['widget']
            ship.deleteLater()
        self.placed_ships.clear()
        
        # Очищаем игровое поле
        self.board = [[0 for _ in range(self.FIELD_SIZE)] for _ in range(self.FIELD_SIZE)]
        
        # Сбрасываем счетчики кораблей
        for size, count in self.SHIPS_SET:
            self.available_ships[size]['count'] = count
            self.available_ships[size]['label'].setText(f"x{count}")
            self.available_ships[size]['template'].setVisible(True)
        
        # Создаем список всех кораблей для размещения
        ships = []
        for size, count in self.SHIPS_SET:
            ships += [size] * count
        random.shuffle(ships)
        
        # Пытаемся разместить каждый корабль
        for size in ships:
            placed = False
            attempts = 0
            max_attempts = 100  # Максимальное количество попыток для каждого корабля
            
            while not placed and attempts < max_attempts:
                row = random.randint(0, self.FIELD_SIZE-1)
                col = random.randint(0, self.FIELD_SIZE-1)
                is_horizontal = random.choice([True, False])
                
                if self.can_place_ship(row, col, size, is_horizontal):
                    # Создаем новый корабль
                    new_ship = ShipPreview(size, self, self)
                    if is_horizontal:
                        new_ship.setFixedSize(size * self.field_cell_size, self.field_cell_size)
                    else:
                        new_ship.setFixedSize(self.field_cell_size, size * self.field_cell_size)
                    new_ship.is_horizontal = is_horizontal
                    
                    # Размещаем корабль
                    self.place_ship_on_board(new_ship, row, col)
                    placed = True
                attempts += 1
            
            if not placed:
                # Если не удалось разместить корабль, очищаем поле и пробуем заново
                self.clear_board()
                QMessageBox.warning(self, "Ошибка", "Не удалось разместить все корабли случайным образом!")
                return
        
        # Обновляем отображение
        self.update()
        self.update_start_btn()
        
    def clear_all_cells_highlight(self):
        for cell in self.cells.values():
            cell.setStyleSheet("""
                QPushButton {
                    background-color: rgba(255, 255, 255, 30);
                    border: 1px solid rgba(255, 255, 255, 50);
                }
                QPushButton:hover {
                    background-color: rgba(255, 255, 255, 50);
                }
            """)

    def clear_board(self):
        """Очистка поля"""
        try:
            # Сохраняем список виджетов для удаления
            ships_to_delete = [ship_info['widget'] for ship_info in self.placed_ships]
            for ship in ships_to_delete:
                ship.deleteLater()
            self.placed_ships.clear()
            # Очищаем игровое поле
            self.board = [[0 for _ in range(self.FIELD_SIZE)] for _ in range(self.FIELD_SIZE)]
            # Сбрасываем счетчики кораблей
            for size, count in self.SHIPS_SET:
                self.available_ships[size]['count'] = count
                self.available_ships[size]['label'].setText(f"x{count}")
                self.available_ships[size]['template'].setVisible(True)
            # Обновляем счетчик
            total_ships = sum(c for _, c in self.SHIPS_SET)
            self.ships_counter.setText(f'Осталось: {total_ships} кораблей')
            # Обновляем статус
            self.status_label.setText('Перетащите корабли на поле')
            # Сброс подсветки
            self.clear_all_cells_highlight()
            # Обновляем интерфейс
            self.update_start_btn()
            self.update_total_ships_counter()
            self.update()
        except Exception as e:
            print(f"Error in clear_board: {e}")

    def start_game(self):
        if len(self.placed_ships) == sum(c for _, c in self.SHIPS_SET):
            ships = [((s['row']+1, s['col']+1), s['widget'].ship_size, s['widget'].is_horizontal) for s in self.placed_ships]
            from game_screen import GameScreen
            self.game_screen = GameScreen(ships)
            self.game_screen.show()
            self.close()
        
    def update_start_btn(self):
        total_ships = sum(c for _, c in self.SHIPS_SET)
        placed_ships = len(self.placed_ships)
        
        self.start_btn.setEnabled(placed_ships == total_ships)
        
        if placed_ships == total_ships:
            self.start_btn.setText("Начать игру")
        else:
            self.start_btn.setText(f"Осталось разместить: {total_ships - placed_ships}")

    def set_background(self):
        background_path = resource_path(os.path.join('assets', 'ship_placement_background.jpg'))
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
        from main import MainMenu
        self.main_menu = MainMenu()
        self.main_menu.show()
        self.close() 

    def paintEvent(self, event):
        super().paintEvent(event)
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # Отрисовка размещенных кораблей
        for ship_info in self.placed_ships:
            row, col = ship_info['row'], ship_info['col']
            size = ship_info['size']
            is_horizontal = ship_info['horizontal']
            
            # Получаем позицию первой клетки
            first_cell = self.cells[(row, col)]
            cell_pos = first_cell.mapTo(self, QPoint(0, 0))
            
            # Определяем размеры корабля
            if is_horizontal:
                width = size * self.field_cell_size
                height = self.field_cell_size
            else:
                width = self.field_cell_size
                height = size * self.field_cell_size
            
            # Рисуем корабль
            ship_color = QColor(210, 180, 140)
            border_color = QColor(139, 69, 19)
            detail_color = QColor(160, 82, 45)
            
            # Основная часть
            painter.setBrush(QBrush(ship_color))
            painter.setPen(QPen(border_color, 2))
            painter.drawRoundedRect(cell_pos.x(), cell_pos.y(), width - 5, height, 5, 5)
            
            # Детали
            cell_size = self.field_cell_size
            for i in range(size):
                if is_horizontal:
                    # Иллюминаторы
                    painter.setBrush(QBrush(detail_color))
                    painter.setPen(QPen(border_color, 1))
                    painter.drawEllipse(cell_pos.x() + i * cell_size + 8, cell_pos.y() + 8, 9, 9)
                    
                    # Деревянные доски
                    if i < size - 1:
                        painter.setPen(QPen(detail_color, 1, Qt.DashLine))
                        painter.drawLine(cell_pos.x() + i * cell_size + cell_size, 
                                       cell_pos.y() + 5,
                                       cell_pos.x() + i * cell_size + cell_size,
                                       cell_pos.y() + 20)
                    
                    # Нос корабля
                    if i == size - 1:
                        painter.setBrush(QBrush(ship_color))
                        painter.setPen(QPen(border_color, 2))
                        painter.drawPolygon([
                            QPoint(cell_pos.x() + width - 5, cell_pos.y()),
                            QPoint(cell_pos.x() + width, cell_pos.y() + height // 2),
                            QPoint(cell_pos.x() + width - 5, cell_pos.y() + height)
                        ])
                else:
                    # Иллюминаторы
                    painter.setBrush(QBrush(detail_color))
                    painter.setPen(QPen(border_color, 1))
                    painter.drawEllipse(cell_pos.x() + 8, cell_pos.y() + i * cell_size + 8, 9, 9)
                    
                    # Деревянные доски
                    if i < size - 1:
                        painter.setPen(QPen(detail_color, 1, Qt.DashLine))
                        painter.drawLine(cell_pos.x() + 5,
                                       cell_pos.y() + i * cell_size + cell_size,
                                       cell_pos.x() + 20,
                                       cell_pos.y() + i * cell_size + cell_size)
                    
                    # Нос корабля
                    if i == size - 1:
                        painter.setBrush(QBrush(ship_color))
                        painter.setPen(QPen(border_color, 2))
                        painter.drawPolygon([
                            QPoint(cell_pos.x(), cell_pos.y() + height - 5),
                            QPoint(cell_pos.x() + width // 2, cell_pos.y() + height),
                            QPoint(cell_pos.x() + width, cell_pos.y() + height - 5)
                        ]) 

    def start_drag_ship(self, event, ship, from_field=False):
        size = ship.ship_size
        # Проверяем, есть ли корабли этого типа на панели
        if not from_field:
            if self.available_ships[size]['count'] <= 0:
                return
            # Уменьшаем счетчик только при начале drag&drop
            self.available_ships[size]['count'] -= 1
            if self.available_ships[size]['count'] < 0:
                self.available_ships[size]['count'] = 0
            self.available_ships[size]['label'].setText(f"x{self.available_ships[size]['count']}")
            if self.available_ships[size]['count'] == 0:
                self.available_ships[size]['template'].setVisible(False)
        new_ship = ShipPreview(size, self, self)
        new_ship.is_horizontal = ship.is_horizontal
        new_ship.is_temp_dragged = True
        new_ship.is_template = False
        new_ship.is_placed = False
        new_ship.from_panel = not from_field
        new_ship.setFocus()
        new_ship.setCursor(Qt.ClosedHandCursor)
        if from_field:
            # Удаляем с поля
            self.remove_ship_from_board(ship)
            ship.deleteLater()
        # Позиция
        global_pos = ship.mapToGlobal(event.pos())
        new_ship.move(self.mapFromGlobal(global_pos))
        new_ship.show()
        new_ship.is_dragging = True
        new_ship.drag_start_pos = event.pos()
        self.dragged_ship = new_ship

    def update_drag_highlight(self, ship):
        # Подсветка клеток под временным кораблем
        game_board = self.findChild(QWidget, "game_board")
        if not game_board:
            return
        center_pos = ship.mapTo(game_board, ship.rect().center())
        target_cell = None
        target_pos = None
        min_distance = float('inf')
        for pos, cell in self.cells.items():
            cell_center = cell.rect().center()
            cell_center_global = cell.mapTo(game_board, cell_center)
            distance = (center_pos - cell_center_global).manhattanLength()
            if distance < min_distance:
                min_distance = distance
                target_cell = cell
                target_pos = pos
        if target_cell:
            can_place = self.can_place_ship(target_pos[0], target_pos[1], ship.ship_size, ship.is_horizontal)
            ship.highlight_ship_cells(target_pos[0], target_pos[1], can_place)
            ship.is_valid_placement = can_place
            ship.is_invalid_position = not can_place
            ship.update()
        else:
            ship.highlight_ship_cells(-1, -1, False)
            ship.is_valid_placement = True
            ship.is_invalid_position = False
            ship.update()

    def try_place_dragged_ship(self, ship, row, col):
        if self.can_place_ship(row, col, ship.ship_size, ship.is_horizontal):
            # Создаём новый постоянный экземпляр для поля
            placed_ship = ShipPreview(ship.ship_size, self, self)
            placed_ship.is_horizontal = ship.is_horizontal
            placed_ship.is_placed = True
            placed_ship.is_template = False
            placed_ship.setFocus()
            placed_ship.setCursor(Qt.OpenHandCursor)
            # Размеры и позиция
            if ship.is_horizontal:
                placed_ship.setFixedSize(ship.ship_size * self.field_cell_size, self.field_cell_size)
            else:
                placed_ship.setFixedSize(self.field_cell_size, ship.ship_size * self.field_cell_size)
            first_cell = self.cells[(row, col)]
            cell_pos = first_cell.mapTo(self, QPoint(0, 0))
            placed_ship.move(cell_pos)
            placed_ship.show()
            # Добавляем в placed_ships
            self.placed_ships.append({
                'row': row,
                'col': col,
                'horizontal': ship.is_horizontal,
                'size': ship.ship_size,
                'widget': placed_ship
            })
            # Обновляем board
            for i in range(ship.ship_size):
                r = row + (0 if ship.is_horizontal else i)
                c = col + (i if ship.is_horizontal else 0)
                self.board[r][c] = 1
            # Удаляем временный drag-ship
            ship.deleteLater()
            self.clear_all_cells_highlight()
            self.update()
            self.update_start_btn()
            self.update_total_ships_counter()
            return True
        else:
            # Если не удалось разместить — вернуть счетчик, если drag был с панели
            if hasattr(ship, 'from_panel') and ship.from_panel:
                self.available_ships[ship.ship_size]['count'] += 1
                self.available_ships[ship.ship_size]['label'].setText(f"x{self.available_ships[ship.ship_size]['count']}")
                self.available_ships[ship.ship_size]['template'].setVisible(True)
                self.update_total_ships_counter()
            self.clear_all_cells_highlight()
            return False

    def snap_dragged_ship(self, ship):
        # После поворота корабль прилипает к ближайшей клетке
        game_board = self.findChild(QWidget, "game_board")
        if not game_board:
            return
        # Используем центр корабля
        global_mouse = ship.mapToGlobal(ship.rect().center())
        board_mouse = game_board.mapFromGlobal(global_mouse)
        min_dist = float('inf')
        snap_pos = None
        for (row, col), cell in self.cells.items():
            cell_center = cell.rect().center()
            cell_center_global = cell.mapTo(game_board, cell_center)
            dist = (board_mouse - cell_center_global).manhattanLength()
            if dist < min_dist:
                min_dist = dist
                snap_pos = (row, col, cell)
        if snap_pos:
            row, col, cell = snap_pos
            cell_pos = cell.mapTo(self, QPoint(0, 0))
            ship.move(cell_pos)
            can_place = self.can_place_ship(row, col, ship.ship_size, ship.is_horizontal)
            ship.highlight_ship_cells(row, col, can_place)
            ship.is_valid_placement = can_place
            ship.is_invalid_position = not can_place
            ship.update()
            ship._snap_row = row
            ship._snap_col = col 

    def update_total_ships_counter(self):
        total_left = sum(info['count'] for info in self.available_ships.values())
        self.ships_counter.setText(f'Осталось: {total_left} кораблей') 