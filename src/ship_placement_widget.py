from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, QLabel,
                              QPushButton, QScrollArea, QFrame, QGroupBox)
from PyQt5.QtCore import Qt, QPoint, QMimeData
from PyQt5.QtGui import QPainter, QPixmap, QDragEnterEvent, QDragMoveEvent, QDropEvent, QDrag, QTransform
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
        self.init_ui()
        self.init_game()
        
        # Состояние кораблей
        self.selected_ship = None
        self.selected_ship_size = None
        self.is_horizontal = False

    def init_ui(self):
        # Создаем фоновое изображение
        self.background = QLabel(self)
        self.background.setGeometry(0, 0, 1000, 600)
        self.background.setScaledContents(True)
        self.background.lower()  # Отправляем фон на задний план
        
        # Создаем сетку
        self.grid = QLabel(self)
        self.grid.setGeometry(0, 0, 1000, 600)
        self.grid.lower()  # Отправляем сетку на задний план, но поверх фона
        
        # Загружаем фоновое изображение
        image_path = Path("src/images/ship_placement_background.jpg")
        if image_path.exists():
            pixmap = QPixmap(str(image_path))
            if not pixmap.isNull():
                self.background.setPixmap(pixmap)
            else:
                print(f"Ошибка: не удалось загрузить изображение из {image_path}")
        else:
            print(f"Ошибка: файл {image_path} не найден")
            
        # Создаем сетку
        self.create_grid()

        # Создаем основной layout
        layout = QHBoxLayout()
        
        # Левая часть - игровое поле 10x10
        left_layout = QVBoxLayout()
        
        # Создаем контейнер для поля
        field_container = QFrame()
        field_container.setFixedSize(500, 500)
        field_container.setStyleSheet("""
            QFrame {
                background-color: transparent;
                border: none;
            }
        """)
        
        # Создаем сетку для поля
        field_grid = QGridLayout()
        field_grid.setSpacing(0)
        
        # Создаем кнопки для поля
        self.field_buttons = []
        for i in range(10):
            row = []
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
                button.clicked.connect(lambda checked, x=i, y=j: self.on_field_click(x, y))
                row.append(button)
                field_grid.addWidget(button, i, j)
            self.field_buttons.append(row)
        
        field_container.setLayout(field_grid)
        left_layout.addWidget(field_container)
        left_layout.setContentsMargins(30, 0, 0, 0)  # Увеличиваем отступ слева до 30 пикселей
        layout.addLayout(left_layout)
        
        # Правая часть - панель кораблей и кнопки
        right_layout = QVBoxLayout()
        right_layout.setSpacing(20)
        
        # Панель кораблей
        ships_layout = QHBoxLayout()
        ships_layout.setSpacing(50)  # Увеличиваем отступ между кораблями
        
        # Добавляем корабли разных размеров
        ship_sizes = [4, 3, 3, 2, 2, 2, 1, 1, 1, 1]
        self.ship_images = []
        
        for size in ship_sizes[:4]:  # Берем только первые 4 корабля
            # Создаем QLabel для изображения корабля
            ship_label = QLabel()
            ship_label.setFixedSize(30, 120)  # Вертикальное расположение
            
            # Загружаем изображение корабля
            image_path = Path(f"src/images/{size}_deck_ship.png")
            if image_path.exists():
                pixmap = QPixmap(str(image_path))
                if not pixmap.isNull():
                    # Поворачиваем изображение на 90 градусов
                    rotated_pixmap = pixmap.transformed(QTransform().rotate(90))
                    ship_label.setPixmap(rotated_pixmap)
                    ship_label.setScaledContents(True)
                else:
                    print(f"Ошибка: не удалось загрузить изображение из {image_path}")
            else:
                print(f"Ошибка: файл {image_path} не найден")
            
            # Добавляем обработчики для перетаскивания
            ship_label.mousePressEvent = lambda event, s=size: self.start_drag(event, s)
            ship_label.mouseMoveEvent = lambda event: self.drag_move(event)
            ship_label.mouseReleaseEvent = lambda event: self.drag_release(event)
            
            self.ship_images.append(ship_label)
            ships_layout.addWidget(ship_label)
        
        right_layout.addLayout(ships_layout)
        
        # Кнопки управления
        buttons_layout = QVBoxLayout()
        buttons_layout.setSpacing(10)
        
        # Кнопка "Начать игру"
        start_button = QPushButton("Начать игру")
        start_button.setFont(QFont("Arial", 16))
        start_button.setStyleSheet("""
            QPushButton {
                color: white;
                border: none;
                background: transparent;
                text-align: center;
                padding: 10px;
                min-width: 150px;
                min-height: 40px;
            }
            QPushButton:hover {
                color: #FFD700;
            }
            QPushButton::pressed {
                color: #FFA500;
            }
        """)
        start_button.clicked.connect(self.start_game.emit)
        buttons_layout.addWidget(start_button)

        # Кнопка "Случайно"
        random_button = QPushButton("Случайно")
        random_button.setFont(QFont("Arial", 16))
        random_button.setStyleSheet("""
            QPushButton {
                color: white;
                border: none;
                background: transparent;
                text-align: center;
                padding: 10px;
                min-width: 150px;
                min-height: 40px;
            }
            QPushButton:hover {
                color: #FFD700;
            }
            QPushButton::pressed {
                color: #FFA500;
            }
        """)
        random_button.clicked.connect(self.random_placement)
        buttons_layout.addWidget(random_button)

        # Кнопка "Очистить"
        clear_button = QPushButton("Очистить")
        clear_button.setFont(QFont("Arial", 16))
        clear_button.setStyleSheet("""
            QPushButton {
                color: white;
                border: none;
                background: transparent;
                text-align: center;
                padding: 10px;
                min-width: 150px;
                min-height: 40px;
            }
            QPushButton:hover {
                color: #FFD700;
            }
            QPushButton::pressed {
                color: #FFA500;
            }
        """)
        clear_button.clicked.connect(self.clear_field)
        buttons_layout.addWidget(clear_button)
        
        right_layout.addLayout(buttons_layout)
        layout.addLayout(right_layout)
        
        # Устанавливаем layout для виджета
        self.setLayout(layout)

    def init_game(self):
        """Инициализация игры"""
        self.board = [[CellState.EMPTY for _ in range(10)] for _ in range(10)]
        self.placed_ships = []
        
    def start_drag(self, event, size):
        """Начинает перетаскивание корабля"""
        if event.button() == Qt.LeftButton:
            self.drag_start_pos = event.pos()
            self.ship_being_dragged = size
            self.is_horizontal = False  # По умолчанию вертикальное положение

    def drag_move(self, event):
        """Обрабатывает движение при перетаскивании"""
        if event.buttons() & Qt.LeftButton and self.ship_being_dragged is not None:
            # Создаем drag объект
            drag = QDrag(self)
            mime_data = QMimeData()
            mime_data.setText(f"ship_{self.ship_being_dragged}")
            drag.setMimeData(mime_data)
            
            # Создаем pixmap для отображения при перетаскивании
            image_path = Path(f"src/images/{self.ship_being_dragged}_deck_ship.png")
            if image_path.exists():
                pixmap = QPixmap(str(image_path))
                if not pixmap.isNull():
                    # Поворачиваем изображение на 90 градусов
                    rotated_pixmap = pixmap.transformed(QTransform().rotate(90))
                    drag.setPixmap(rotated_pixmap)
                    drag.setHotSpot(event.pos())
                    
                    # Запускаем перетаскивание
                    drag.exec_(Qt.MoveAction)

    def drag_release(self, event):
        """Обрабатывает окончание перетаскивания"""
        self.drag_start_pos = None
        self.ship_being_dragged = None

    def dragEnterEvent(self, event: QDragEnterEvent):
        """Обрабатывает вход в виджет при перетаскивании"""
        if event.mimeData().hasText():
            event.acceptProposedAction()

    def dragMoveEvent(self, event: QDragMoveEvent):
        """Обрабатывает движение внутри виджета при перетаскивании"""
        if event.mimeData().hasText():
            event.acceptProposedAction()

    def dropEvent(self, event: QDropEvent):
        """Обрабатывает сброс перетаскиваемого объекта"""
        if event.mimeData().hasText():
            text = event.mimeData().text()
            if text.startswith("ship_"):
                # Получаем размер корабля из текста
                size = int(text.split('_')[1])
                
                # Получаем позицию сброса
                pos = event.pos()
                
                # Находим ближайшую ячейку поля
                cell_size = 30
                x = pos.x() // cell_size
                y = pos.y() // cell_size
                
                # Проверяем возможность размещения
                if self.can_place_ship(x, y, size, False):  # False - вертикальное положение
                    # Размещаем корабль
                    self.place_ship(x, y, size, False)
                    self.check_game_ready()
                    
                    # Обновляем кнопки поля
                    for i in range(size):
                        self.field_buttons[x + i][y].setStyleSheet("""
                            QPushButton {
                                border: 1px solid black;
                                background-color: #00008B;
                            }
                        """)
                    
                    event.acceptProposedAction()

    def select_ship(self, size, horizontal):
        """Выбирает корабль для размещения"""
        self.selected_ship_size = size
        self.is_horizontal = horizontal
        
    def toggle_orientation(self):
        """Переключает ориентацию корабля"""
        self.is_horizontal = not self.is_horizontal

    def random_placement(self):
        """Расставляет корабли случайным образом"""
        print("Случайная расстановка кораблей")

    def clear_field(self):
        """Очищает игровое поле"""
        print("Поле очищено")

    def resizeEvent(self, event):
        """Обрабатывает изменение размера окна"""
        if hasattr(self, 'background'):
            self.background.setGeometry(0, 0, self.width(), self.height())
        if hasattr(self, 'grid'):
            self.grid.setGeometry(0, 0, self.width(), self.height())
        super().resizeEvent(event)
        
        # Обновляем размеры кнопок сетки
        if hasattr(self, 'buttons'):
            for i in range(10):
                for j in range(10):
                    self.buttons[i][j].setFixedSize(
                        int(self.width() * 0.5 / 10),  # 50% ширины окна
                        int(self.height() * 0.8 / 10)   # 80% высоты окна
                    )
        
        # Сбрасываем выбранный корабль
        self.selected_ship = None
        self.selected_ship_size = None
        
    def can_place_ship(self, x, y, size, horizontal):
        """Проверяет возможность размещения корабля"""
        if horizontal:
            if y + size > 10:
                return False
            for i in range(size):
                if self.board[x][y + i] != CellState.EMPTY:
                    return False
        else:
            if x + size > 10:
                return False
            for i in range(size):
                if self.board[x + i][y] != CellState.EMPTY:
                    return False
        return True
        
    def place_ship(self, x, y, ship, horizontal):
        """Размещает корабль на поле"""
        if horizontal:
            for i in range(ship.size):
                self.board[x][y + i] = CellState.SHIP
                self.buttons[x][y + i].setStyleSheet("""
                    QPushButton {
                        background-color: gray;
                        border: 1px solid #cccccc;
                    }
                """)
        else:
            for i in range(ship.size):
                self.board[x + i][y] = CellState.SHIP
                self.buttons[x + i][y].setStyleSheet("""
                    QPushButton {
                        background-color: gray;
                        border: 1px solid #cccccc;
                    }
                """)
                
    def check_game_ready(self):
        """Проверяет готовность к игре"""
        ready = True
        for button in self.ship_buttons.values():
            if button.count > 0:
                ready = False
                break
        self.start_button.setEnabled(ready)
        
    def on_start_game(self):
        """Начинает игру"""
        self.start_game.emit()
        
    def on_random_placement(self):
        """Размещает корабли случайным образом"""
        # Очищаем поле
        self.on_clear_board()
        
        # Размещаем корабли
        for size in [4, 3, 2, 1]:
            for _ in range({4: 1, 3: 2, 2: 3, 1: 4}[size]):
                placed = False
                while not placed:
                    x = random.randint(0, 9)
                    y = random.randint(0, 9)
                    horizontal = random.choice([True, False])
                    if self.can_place_ship(x, y, size, horizontal):
                        ship = Ship(size)
                        self.place_ship(x, y, ship, horizontal)
                        self.placed_ships.append(ship)
                        placed = True
        
        self.check_game_ready()
        
    def on_clear_board(self):
        """Очищает поле"""
        # Очищаем поле
        self.board = [[CellState.EMPTY for _ in range(10)] for _ in range(10)]
        for i in range(10):
            for j in range(10):
                self.buttons[i][j].setStyleSheet("""
                    QPushButton {
                        background-color: white;
                        border: 1px solid #cccccc;
                    }
                """)
        
        # Сбрасываем корабли
        self.placed_ships = []
        
        # Отключаем кнопку "Начать игру"
        self.start_button.setEnabled(False)

    def create_grid(self):
        """Создает сетку на фоновом изображении"""
        self.grid.setStyleSheet("""
            QLabel {
                background-color: transparent;
            }
        """)
        
        # Создаем сетку из QLabel
        self.grid_layout = QGridLayout()
        self.grid_layout.setSpacing(0)
        
        # Создаем кнопки для сетки
        self.buttons = []
        for i in range(10):
            row = []
            for j in range(10):
                button = QLabel()
                button.setFixedSize(50, 50)
                button.setStyleSheet("""
                    QLabel {
                        border: 1px solid #cccccc;
                        background-color: transparent;
                    }
                """)
                button.setAlignment(Qt.AlignCenter)
                button.mousePressEvent = lambda event, x=i, y=j: self.on_cell_click(x, y)
                row.append(button)
                self.grid_layout.addWidget(button, i, j)
            self.buttons.append(row)
        
        self.grid.setLayout(self.grid_layout)
        
    def on_field_click(self, x, y):
        """Обрабатывает клик по ячейке поля"""
        if self.selected_ship_size:
            if self.can_place_ship(x, y, self.selected_ship_size, self.is_horizontal):
                self.place_ship(x, y, self.selected_ship_size, self.is_horizontal)
                self.check_game_ready()
                self.selected_ship_size = None
                
    def can_place_ship(self, x, y, size, horizontal):
        """Проверяет, можно ли разместить корабль в данной позиции"""
        if horizontal:
            if y + size > 10:
                return False
            for i in range(size):
                if self.board[x][y + i] != CellState.EMPTY:
                    return False
        else:
            if x + size > 10:
                return False
            for i in range(size):
                if self.board[x + i][y] != CellState.EMPTY:
                    return False
        return True
        
    def place_ship(self, x, y, size, horizontal):
        """Размещает корабль на игровом поле"""
        ship = Ship(size)
        self.placed_ships.append(ship)
        
        # Обновляем игровое поле
        if horizontal:
            for i in range(size):
                self.board[x][y + i] = CellState.SHIP
                self.buttons[x][y + i].setStyleSheet("""
                    QLabel {
                        border: 1px solid #cccccc;
                        background-color: #00008B;
                    }
                """)
        else:
            for i in range(size):
                self.board[x + i][y] = CellState.SHIP
                self.buttons[x + i][y].setStyleSheet("""
                    QLabel {
                        border: 1px solid #cccccc;
                        background-color: #00008B;
                    }
                """)
                
    def check_game_ready(self):
        """Проверяет, можно ли начать игру"""
        # Проверяем, размещены ли все корабли
        ship_counts = {4: 1, 3: 2, 2: 3, 1: 4}
        
        # Проверяем количество размещённых кораблей
        placed_counts = {
            4: sum(1 for ship in self.placed_ships if ship.size == 4),
            3: sum(1 for ship in self.placed_ships if ship.size == 3),
            2: sum(1 for ship in self.placed_ships if ship.size == 2),
            1: sum(1 for ship in self.placed_ships if ship.size == 1)
        }
        
        # Проверяем, размещены ли все корабли
        all_ships_placed = all(placed_counts[size] == count 
                              for size, count in ship_counts.items())
        
        # Активируем/деактивируем кнопку "Начать игру"
        self.start_button.setEnabled(all_ships_placed)
