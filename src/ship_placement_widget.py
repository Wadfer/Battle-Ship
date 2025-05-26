from PyQt5.QtWidgets import (QWidget, QLabel, QPushButton, QGridLayout, QHBoxLayout,
                         QVBoxLayout, QFrame, QMessageBox, QSizePolicy, QScrollArea, QGroupBox)
from PyQt5.QtCore import Qt, QPoint, QMimeData
from PyQt5.QtGui import QPainter, QPixmap, QDragEnterEvent, QDragMoveEvent, QDropEvent, QDrag, QTransform, QIcon
from PyQt5.QtCore import Qt, QSize, pyqtSignal
from PyQt5.QtGui import QPainter, QPen, QBrush, QColor, QFont, QPixmap
from pathlib import Path
from src.game_logic import CellState, Ship
import random


class ShipPlacementWidget(QWidget):
    start_game = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.setAcceptDrops(True)  # Включаем поддержку перетаскивания
        self.ship_being_dragged = None  # Текущий перетаскиваемый корабль
        self.drag_start_pos = None  # Позиция начала перетаскивания
        self.ship_images = []  # Список для хранения QLabel'ов кораблей
        self.field_buttons = [[None for _ in range(10)] for _ in range(10)]  # Кнопки игрового поля
        self.start_button = None  # Кнопка "Начать игру"
        self.ship_counters = {4: 1, 3: 2, 2: 3, 1: 4}  # Счетчики кораблей
        self.board = [[CellState.EMPTY for _ in range(10)] for _ in range(10)]  # Состояние поля
        
        self.init_ui()
        
        # Состояние кораблей
        self.selected_ship = None
        self.selected_ship_size = None
        self.is_horizontal = False

    def init_ui(self):
        # Создаем фон
        self.background = QLabel(self)
        self.background.setGeometry(0, 0, 1000, 600)
        self.background.lower()  # Отправляем фон на задний план
        
        # Загружаем фоновое изображение
        image_path = Path("src/images/ship_placement_background.jpg")
        if image_path.exists():
            pixmap = QPixmap(str(image_path))
            if not pixmap.isNull():
                self.background.setPixmap(pixmap)
                self.background.setScaledContents(True)

        # Создаем основной layout
        layout = QHBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Левая часть - игровое поле 10x10
        left_layout = QVBoxLayout()
        left_layout.setContentsMargins(0, 0, 0, 0)
        
        # Создаем контейнер для поля
        field_container = QFrame()
        field_container.setFixedSize(500, 500)
        field_container.setStyleSheet("""
            QFrame {
                background-color: rgba(0, 0, 0, 0.2);
                border: none;
                border-radius: 10px;
            }
        """)
        
        # Создаем сетку для поля
        self.grid = QGridLayout()
        self.grid.setSpacing(0)
        
        # Создаем кнопки для каждой ячейки поля
        for i in range(10):
            for j in range(10):
                button = QPushButton()
                button.setFixedSize(30, 30)
                button.setStyleSheet("""
                    QPushButton {
                        border: 1px solid white;
                        background-color: rgba(0, 0, 0, 0.2);
                        color: white;
                    }
                    QPushButton:hover {
                        background-color: rgba(0, 0, 139, 0.2);
                    }
                """)
                button.clicked.connect(lambda _, x=i, y=j: self.on_cell_click(x, y))
                self.field_buttons[i][j] = button
                self.grid.addWidget(button, i, j)

        # Устанавливаем сетку в контейнер
        field_container.setLayout(self.grid)
        
        left_layout.addWidget(field_container)
        left_layout.setContentsMargins(30, 0, 0, 0)  # Увеличиваем отступ слева до 30 пикселей
        layout.addLayout(left_layout)
        
        # Создаем горизонтальный layout для правой панели
        right_layout = QHBoxLayout()
        right_layout.setSpacing(10)
        right_layout.setAlignment(Qt.AlignCenter)
        right_layout.setContentsMargins(10, 10, 10, 10)

        # Добавляем корабли в правую панель
        ship_counts = {4: 1, 3: 2, 2: 3, 1: 4}
        for size, count in ship_counts.items():
            # Создаем QLabel для отображения корабля
            ship_label = QLabel()
            ship_label.setFixedSize(30, size * 30)  # Меняем размеры для вертикального отображения
            
            # Загружаем изображение корабля
            ship_name = {
                1: '1_deck_ship',
                2: '2_deck_ship',
                3: '3_deck_ship',
                4: '4_deck_ship'
            }[size]
            ship_image_path = Path(f"src/images/{ship_name}.png")
            if ship_image_path.exists():
                pixmap = QPixmap(str(ship_image_path))
                # Поворачиваем изображение на 90 градусов
                pixmap = pixmap.transformed(QTransform().rotate(90))
                ship_label.setPixmap(pixmap)
                ship_label.setScaledContents(True)
            
            # Создаем QLabel для отображения количества
            count_label = QLabel()
            count_label.setText(f"{self.ship_counters[size]}\nосталось")
            count_label.setAlignment(Qt.AlignCenter)
            count_label.setStyleSheet("""
                QLabel {
                    color: white;
                    font-size: 12px;
                    background-color: rgba(0, 0, 0, 0.5);
                    border-radius: 5px;
                    padding: 2px;
                    margin-top: 5px;
                    min-width: 50px;
                }
            """)
            
            # Создаем вертикальный layout для корабля и его количества
            ship_layout = QVBoxLayout()
            ship_layout.setSpacing(0)  # Убираем лишний отступ между элементами
            ship_layout.addWidget(ship_label)
            ship_layout.addWidget(count_label)
            
            # Создаем горизонтальный layout для корабля
            ship_layout_h = QHBoxLayout()
            ship_layout_h.addLayout(ship_layout)
            ship_layout_h.setAlignment(Qt.AlignCenter)
            
            # Добавляем корабль и счетчик в основной layout
            right_layout.addLayout(ship_layout_h)
            
            # Сохраняем пару QLabel'ов для дальнейшего использования
            self.ship_images.append((ship_label, count_label))

        # Создаем кнопку "Начать игру"
        self.start_button = QPushButton("Начать игру")
        self.start_button.setEnabled(False)
        self.start_button.clicked.connect(self.on_start_game)
        self.start_button.setStyleSheet("""
            QPushButton {
                color: white;
                border: none;
                background: rgba(128, 128, 128, 0.7);
                text-align: center;
                padding: 10px;
                min-width: 150px;
                min-height: 40px;
                border-radius: 5px;
            }
            QPushButton:hover {
                background: rgba(128, 128, 128, 0.9);
            }
            QPushButton:pressed {
                background: rgba(128, 128, 128, 1);
            }
        """)
        right_layout.addWidget(self.start_button)
        
        # Добавляем правую часть в основной layout
        layout.addLayout(right_layout)
        
        # Устанавливаем основной layout
        self.setLayout(layout)

        # Устанавливаем размеры окна
        self.setMinimumSize(1000, 600)
        self.setWindowTitle("Расстановка кораблей")

    def initUI(self):
        # Создаем основной layout
        main_layout = QVBoxLayout()

        # Создаем область с кораблями
        ship_area = QHBoxLayout()
        ship_group = QGroupBox("Корабли")
        ship_layout = QVBoxLayout()

        # Создаем кнопки для каждого размера корабля
        ship_counts = {4: 1, 3: 2, 2: 3, 1: 4}
        for size, count in ship_counts.items():
            # Создаем QLabel для отображения корабля
            ship_label = QLabel()
            ship_label.setFixedSize(30, size * 30)  # Меняем размеры для вертикального отображения
            
            # Загружаем изображение корабля
            ship_name = {
                1: '1_deck_ship',
                2: '2_deck_ship',
                3: '3_deck_ship',
                4: '4_deck_ship'
            }[size]
            ship_image_path = Path(f"src/images/{ship_name}.png")
            if ship_image_path.exists():
                pixmap = QPixmap(str(ship_image_path))
                # Поворачиваем изображение на 90 градусов
                pixmap = pixmap.transformed(QTransform().rotate(90))
                ship_label.setPixmap(pixmap)
                ship_label.setScaledContents(True)
            
            # Создаем QLabel для отображения количества
            count_label = QLabel()
            count_label.setText(f"{self.ship_counters[size]}\nосталось")
            count_label.setAlignment(Qt.AlignCenter)
            count_label.setStyleSheet("""
                QLabel {
                    color: white;
                    font-size: 12px;
                    background-color: rgba(0, 0, 0, 0.5);
                    border-radius: 5px;
                    padding: 2px;
                    margin-top: 5px;
                    min-width: 50px;
                }
            """)
            
            # Создаем вертикальный layout для корабля и его количества
            ship_layout = QVBoxLayout()
            ship_layout.setSpacing(0)  # Убираем лишний отступ между элементами
            ship_layout.addWidget(ship_label)
            ship_layout.addWidget(count_label)
            
            # Добавляем корабль и счетчик в layout
            ship_layout.addWidget(count_label)
            
            # Сохраняем пару QLabel'ов для дальнейшего использования
            self.ship_images.append((ship_label, count_label))

        ship_group.setLayout(ship_layout)
        ship_area.addWidget(ship_group)
        main_layout.addLayout(ship_area)

        # Создаем игровое поле
        field_group = QGroupBox("Ваше поле")
        field_layout = QGridLayout()
        
        # Создаем кнопки для каждой ячейки поля
        for i in range(10):
            for j in range(10):
                button = QPushButton()
                button.setFixedSize(30, 30)
                button.setStyleSheet("""
                    QPushButton {
                        border: 1px solid black;
                        background-color: transparent;
                        color: white;
                    }
                    QPushButton:hover {
                        background-color: rgba(0, 0, 139, 0.2);
                    }
                """)
                button.clicked.connect(lambda _, x=i, y=j: self.on_cell_click(x, y))
                self.field_buttons[i][j] = button
                field_layout.addWidget(button, i, j)

        field_group.setLayout(field_layout)
        main_layout.addWidget(field_group)

        # Создаем кнопку "Начать игру"
        self.start_button = QPushButton("Начать игру")
        self.start_button.setEnabled(False)
        self.start_button.clicked.connect(self.on_start_game)
        self.start_button.setStyleSheet("""
            QPushButton {
                color: white;
                border: none;
                background: rgba(128, 128, 128, 0.7);
                text-align: center;
                padding: 10px;
                min-width: 150px;
                min-height: 40px;
                border-radius: 5px;
            }
            QPushButton:hover {
                background: rgba(128, 128, 128, 0.9);
            }
            QPushButton:pressed {
                background: rgba(128, 128, 128, 1);
            }
        """)
        main_layout.addWidget(self.start_button)

        # Устанавливаем основной layout
        self.setLayout(main_layout)

        # Устанавливаем размеры окна
        self.setMinimumSize(600, 800)
        self.setWindowTitle("Расстановка кораблей")

    def on_cell_click(self, x, y):
        """Обрабатывает клик по ячейке поля"""
        if self.ship_being_dragged is not None:
            # Проверяем, можно ли разместить корабль в данной позиции
            if self.can_place_ship(x, y, self.ship_being_dragged, self.is_horizontal):
                self.place_ship(x, y, self.ship_being_dragged, self.is_horizontal)
                self.ship_being_dragged = None

    def on_start_game(self):
        """Обрабатывает нажатие кнопки 'Начать игру'"""
        # Здесь будет код для начала игры
        print("Начинаем игру!")

    def drag_release(self, event):
        """Обрабатывает окончание перетаскивания"""
        if self.ship_being_dragged is not None:
            # Получаем позицию мыши при отпускании
            pos = event.pos()
            x = pos.x() // 30
            y = pos.y() // 30

            # Пытаемся разместить корабль
            if self.can_place_ship(x, y, self.ship_being_dragged, self.is_horizontal):
                self.place_ship(x, y, self.ship_being_dragged, self.is_horizontal)
                self.ship_being_dragged = None

    def can_place_ship(self, x, y, size, horizontal):
        """Проверяет, можно ли разместить корабль в данной позиции"""
        if horizontal:
            if x + size > 10:
                return False
            for i in range(size):
                if self.board[y][x + i] != CellState.EMPTY:
                    return False
        else:
            if y + size > 10:
                return False
            for i in range(size):
                if self.board[y + i][x] != CellState.EMPTY:
                    return False

        # Проверяем, не пересекаются ли корабли по диагонали
        for i in range(-1, size + 1):
            for j in range(-1, 2):
                if horizontal:
                    if 0 <= y + j < 10 and 0 <= x + i < 10:
                        if self.board[y + j][x + i] != CellState.EMPTY:
                            return False
                else:
                    if 0 <= y + i < 10 and 0 <= x + j < 10:
                        if self.board[y + i][x + j] != CellState.EMPTY:
                            return False

        return True

    def place_ship(self, x, y, size, horizontal):
        """Размещает корабль на игровом поле"""
        # Обновляем состояние поля
        if horizontal:
            for i in range(size):
                self.board[y][x + i] = CellState.SHIP
                # Устанавливаем иконку корабля
                button = self.field_buttons[y][x + i]
                button.setStyleSheet("""
                    QPushButton {
                        border: 1px solid black;
                        background-color: rgba(0, 0, 139, 0.5);
                        color: white;
                    }
                """)
        else:
            for i in range(size):
                self.board[y + i][x] = CellState.SHIP
                # Устанавливаем иконку корабля
                button = self.field_buttons[y + i][x]
                button.setStyleSheet("""
                    QPushButton {
                        border: 1px solid black;
                        background-color: rgba(0, 0, 139, 0.5);
                        color: white;
                    }
                """)

        # Обновляем счетчик кораблей
        self.ship_counters[size] -= 1

        # Проверяем, можно ли начать игру
        self.check_game_ready()

    def start_drag(self, event, size):
        """Начинает перетаскивание корабля"""
        self.ship_being_dragged = size
        self.drag_start_pos = event.pos()

    def drag_move(self, event, size):
        """Обрабатывает движение при перетаскивании"""
        if self.ship_being_dragged is not None:
            # Получаем текущую позицию мыши
            pos = event.pos()

            # Проверяем, нажата ли клавиша Shift (для поворота корабля)
            if event.modifiers() & Qt.ShiftModifier:
                self.is_horizontal = not self.is_horizontal

            # Проверяем, можно ли разместить корабль в текущей позиции
            x = pos.x() // 30
            y = pos.y() // 30

            if self.can_place_ship(x, y, size, self.is_horizontal):
                # Отрисовываем предварительное положение корабля
                self.draw_preview(x, y, size, self.is_horizontal)

    def draw_preview(self, x, y, size, horizontal):
        """Отрисовывает предварительное положение корабля"""
        # Очищаем предыдущий предварительный просмотр
        for i in range(10):
            for j in range(10):
                button = self.field_buttons[i][j]
                if button.styleSheet().find("background-color: rgba(0, 0, 139, 0.2);") != -1:
                    button.setStyleSheet("""
                        QPushButton {
                            border: 1px solid black;
                            background-color: transparent;
                            color: white;
                        }
                        QPushButton:hover {
                            background-color: rgba(0, 0, 139, 0.2);
                        }
                    """)

        # Отрисовываем новый предварительный просмотр
        if horizontal:
            for i in range(size):
                button = self.field_buttons[y][x + i]
                button.setStyleSheet("""
                    QPushButton {
                        border: 1px solid black;
                        background-color: rgba(0, 0, 139, 0.2);
                        color: white;
                    }
                """)
        else:
            for i in range(size):
                button = self.field_buttons[y + i][x]
                button.setStyleSheet("""
                    QPushButton {
                        border: 1px solid black;
                        background-color: rgba(0, 0, 139, 0.2);
                        color: white;
                    }
                """)

    def check_game_ready(self):
        """Проверяет, можно ли начать игру"""
        # Проверяем, размещены ли все корабли
        ship_counts = {4: 1, 3: 2, 2: 3, 1: 4}

        all_ships_placed = True
        for size, count in ship_counts.items():
            if self.ship_counters[size] > 0:
                all_ships_placed = False
                break
        
        # Включаем/выключаем кнопку "Начать игру"
        self.start_button.setEnabled(all_ships_placed)
        
        if all_ships_placed:
            self.start_button.setStyleSheet("""
                QPushButton {
                    color: white;
                    border: none;
                    background: rgba(0, 255, 0, 0.7);
                    text-align: center;
                    padding: 10px;
                    min-width: 150px;
                    min-height: 40px;
                    border-radius: 5px;
                }
                QPushButton:hover {
                    background: rgba(0, 255, 0, 0.9);
                }
                QPushButton:pressed {
                    background: rgba(0, 255, 0, 1);
                }
            """)
        else:
            self.start_button.setStyleSheet("""
                QPushButton {
                    color: white;
                    border: none;
                    background: rgba(128, 128, 128, 0.7);
                    text-align: center;
                    padding: 10px;
                    min-width: 150px;
                    min-height: 40px;
                    border-radius: 5px;
                }
                QPushButton:hover {
                    background: rgba(128, 128, 128, 0.9);
                }
                QPushButton:pressed {
                    background: rgba(128, 128, 128, 1);
                }
            """)
            drag.exec_(Qt.MoveAction)

    def drag_move(self, event, size):
        """Обрабатывает движение при перетаскивании"""
        if self.ship_being_dragged is not None:
            if event.buttons() & Qt.LeftButton:
                # Получаем текущую позицию мыши
                current_pos = event.pos()

                # Вычисляем координаты на поле
                x = current_pos.x() // 30  # 30 - размер клетки
                y = current_pos.y() // 30

                # Проверяем, можно ли разместить корабль в этой позиции
                if self.can_place_ship(x, y, size, False):
                    event.accept()
                else:
                    event.ignore()

    def drag_release(self, event):
        """Обрабатывает окончание перетаскивания"""
        if self.ship_being_dragged is not None:
            # Получаем позицию мыши при отпускании
            pos = event.pos()
            x = pos.x() // 30
            y = pos.y() // 30

            # Пытаемся разместить корабль
            if self.can_place_ship(x, y, self.ship_being_dragged, False):
                self.place_ship(x, y, self.ship_being_dragged, False)
                self.check_game_ready()

            self.ship_being_dragged = None

    def resizeEvent(self, event):
        """Обрабатывает изменение размера окна"""
        if hasattr(self, 'background'):
            self.background.setGeometry(0, 0, self.width(), self.height())

    def start_drag(self, event, size):
        """Начинает перетаскивание корабля"""
        if event.button() == Qt.LeftButton:
            self.ship_being_dragged = size
            self.drag_start_pos = event.pos()

            # Создаем drag объект
            drag = QDrag(self)
            mime_data = QMimeData()
            mime_data.setText(str(size))
            drag.setMimeData(mime_data)

            # Создаем pixmap для перетаскиваемого корабля
            image_path = Path(f"src/images/{size}_deck_ship.png")
            if image_path.exists():
                pixmap = QPixmap(str(image_path))
                if not pixmap.isNull():
                    # Поворачиваем изображение на 90 градусов
                    rotated_pixmap = pixmap.transformed(QTransform().rotate(90))
                    drag.setPixmap(rotated_pixmap)
                    drag.setHotSpot(QPoint(rotated_pixmap.width() // 2, rotated_pixmap.height() // 2))

            # Запускаем перетаскивание
            drag.exec_(Qt.MoveAction)

    def drag_move(self, event, size):
        """Обрабатывает движение при перетаскивании"""
        if self.ship_being_dragged is not None:
            if event.buttons() & Qt.LeftButton:
                # Получаем текущую позицию мыши
                current_pos = event.pos()

                # Вычисляем координаты на поле
                x = current_pos.x() // 30  # 30 - размер клетки
                y = current_pos.y() // 30

                # Проверяем, можно ли разместить корабль в этой позиции
                if self.can_place_ship(x, y, size, False):
                    event.accept()
                else:
                    event.ignore()

    def drag_release(self, event):
        """Обрабатывает окончание перетаскивания"""
        if self.ship_being_dragged is not None:
            # Получаем позицию мыши при отпускании
            pos = event.pos()
            x = pos.x() // 30
            y = pos.y() // 30

            # Пытаемся разместить корабль
            if self.can_place_ship(x, y, self.ship_being_dragged, False):
                self.place_ship(x, y, self.ship_being_dragged, False)
                self.check_game_ready()

            self.ship_being_dragged = None
