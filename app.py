import requests
import json
import pygame
from PyQt5.QtWidgets import QMainWindow, QLabel, QApplication, QPushButton, QVBoxLayout, QWidget
from PyQt5.QtCore import Qt, QTimer, QPoint
from PyQt5.QtGui import QPixmap, QColor, QPalette, QMovie
import sys
import random

API_KEY = '----'  # апишник для погоды
CITY = '----' # город для погоды

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)  # -рамка окно + выше других
        self.setAttribute(Qt.WA_TranslucentBackground)  # прозрачный фон
        self.setGeometry(0, 0, 1920, 1080)
        self.gaming = QMovie("gaming.gif")
        self.cheerleader = QMovie("cheerleader.gif")
        self.eating = QMovie("eating.gif")
        #self.default_gif = QMovie("default.gif")

        self.character = QLabel(self)
        self.character.setPixmap(QPixmap("wm.png"))
        self.character.setScaledContents(True)
        self.character.setFixedSize(300, 300)  # размер пикчи

        # хангри
        self.hunger = 100  # Начальный уровень голода
        self.hunger_decrease_timer = QTimer()
        self.hunger_decrease_timer.timeout.connect(self.decrease_hunger)
        self.hunger_decrease_timer.start(10000)  # decrease timer хангера

        # саунды
        pygame.mixer.init()
        self.hunger_sound = pygame.mixer.Sound("arigato.wav")
        self.hunger_warning_played = False # флаг

        # панелька с кнопками
        self.button_panel = QWidget(self)
        self.button_layout = QVBoxLayout(self.button_panel)

        # чет не понял работает или нет
        self.button_panel.setAutoFillBackground(True)
        palette = self.button_panel.palette()
        palette.setColor(QPalette.Background, QColor(100, 100, 100, 180))
        self.button_panel.setPalette(palette)

        self.button_panel.setWindowFlags(Qt.Window | Qt.FramelessWindowHint)
        self.button_panel.setAttribute(Qt.WA_TranslucentBackground)

        # выход
        self.exit_button = QPushButton("Quit", self.button_panel)
        self.exit_button.clicked.connect(self.close)

        # остановка
        self.stop_button = QPushButton("Pause", self.button_panel)
        self.stop_button.clicked.connect(self.stop_character)

        # продолжение
        self.continue_button = QPushButton("Continue", self.button_panel)
        self.continue_button.clicked.connect(self.continue_character)

        # клей :)
        self.follow_button = QPushButton("Glue", self.button_panel)
        self.follow_button.clicked.connect(self.start_following)

        # чилл
        self.change_button = QPushButton("Mwo", self.button_panel)
        self.change_button.clicked.connect(self.change_character)

        # чилл2
        self.change2_button = QPushButton("Mwo2", self.button_panel)
        self.change2_button.clicked.connect(self.cheerleader_character)

        # еда
        self.feed_button = QPushButton("Mwo3", self.button_panel)
        self.feed_button.clicked.connect(self.feed_character)

        # кнопки в панель
        self.button_layout.addWidget(self.exit_button)
        self.button_layout.addWidget(self.stop_button)
        self.button_layout.addWidget(self.continue_button)
        self.button_layout.addWidget(self.follow_button)
        self.button_layout.addWidget(self.change_button)
        self.button_layout.addWidget(self.change2_button)
        self.button_layout.addWidget(self.feed_button)

        self.button_panel.setLayout(self.button_layout)
        self.button_panel.move(0 + 10, 0 + 10)
        self.button_panel.show()

        # параметры движения
        self.timer = QTimer()
        self.timer.timeout.connect(self.move_character)
        self.timer.start(5)  # фпс

        self.mouse_dragging = False  # проверка для отслеживания перетаскивания окна
        self.drag_position = None  # позиция мыши при нажатии

        self.speed = 1  # скорость движения персонажа
        self.is_moving = True  # проверка на движение

        self.center_character()

        self.following = False  # клей выключен

        #self.timer = QTimer()                                              блок кода для погоды
        #self.timer.timeout.connect(self.update_weather)                    блок кода для погоды
        #self.timer.start(600000)  # проверка погоды минута = 60000         блок кода для погоды
        #self.update_weather()  # проверка на запуске                       блок кода для погоды

    '''
    купите апишку :)
    def update_weather(self):
        """ Получаем данные о погоде и обновляем иконку персонажа при дожде """
        try:
            response = requests.get(
                f"http://api.openweathermap.org/data/2.5/weather?q={CITY}&appid={API_KEY}&units=metric",
                timeout=5  # тайм-аут в 5 секунд
            )
            data = response.json()
            if response.status_code == 200:
                weather_conditions = data['weather'][0]['main']
                print(f"Погода в {CITY}: {weather_conditions}")
                if weather_conditions.lower() == 'rain':
                    self.character.setPixmap(QPixmap("sad.png"))  # иконка1
                else:
                    self.character.setPixmap(QPixmap("happy.png"))  # иконка2
            else:
                print("Ошибка при получении данных о погоде:", data.get('message'))
        except requests.exceptions.Timeout:
            print("Запрос к API истек по времени.")
        except requests.exceptions.RequestException as e:
            print("Произошла ошибка при запросе:", str(e))
    '''

    def decrease_hunger(self):
        """ Уменьшаем голод на 10% каждые 10 секунд. """
        if self.hunger > 0:
            self.hunger -= 10
            print(f"Уровень голода: {self.hunger}%")
            # Проверяем уровень голода для звукового предупреждения
            if self.hunger < 50 and not self.hunger_warning_played:
                self.hunger_sound.play()
                self.hunger_warning_played = True
            elif self.hunger >= 50:
                self.hunger_warning_played = False  # Сбрасываем флаг, если голод снова выше 50%

    def feed_character(self):
        if self.hunger < 100:
            self.hunger += 20
            if self.hunger > 100:
                self.hunger = 100
            print(f"Кормежка: {self.hunger}%")
            self.character.setMovie(self.cheerleader)
            self.cheerleader.start()  # запуск анимации
            self.default_timer = QTimer()
            self.default_timer.setSingleShot(True)
            self.default_timer.timeout.connect(self.set_default_animation)
            self.default_timer.start(5000)  # 5 секунд

    def closeEvent(self, event):
        """ Сохраняем состояние перед закрытием приложения. """
        self.save_state()

    def save_state(self):
        state = {
            'hunger': self.hunger
        }
        with open("state.json", "w") as f:
            json.dump(state, f)

    def center_character(self):
        # размеры окна и персонажа
        window_width = self.width()
        window_height = self.height()
        character_width = self.character.width()
        character_height = self.character.height()

        # координаты центра окна
        center_x = (window_width - character_width) // 2
        center_y = (window_height - character_height) // 2

        # установка позиции персонажа в центр
        self.character.move(center_x, center_y)

    def change_character(self):
        self.character.setMovie(self.gaming)
        self.gaming.start()  # запуск анимации

    def cheerleader_character(self):
        self.character.setMovie(self.cheerleader)
        self.cheerleader.start()  # запуск анимации

    def move_character(self):
        if self.following:
            # позиция курсора
            cursor_pos = self.mapFromGlobal(QApplication.instance().desktop().cursor().pos())

            # центрирование персонажа на курсоре
            target_x = cursor_pos.x() - self.character.width() // 2
            target_y = cursor_pos.y() - self.character.height() // 2
            character_pos = self.character.pos()

            # расстояние по X и Y
            delta_x = target_x - character_pos.x()
            delta_y = target_y - character_pos.y()

            # расстояние до курсора
            distance = (delta_x**2 + delta_y**2)**0.5

            # зависимость скорости от расстояния
            max_speed = 10#self.speed*2
            min_speed = 1#int(self.speed/2)
            speed = min(max_speed, max(min_speed, distance / 10))

            # шаги движения по X и Y
            step_x = int(speed * (delta_x / distance)) if distance != 0 else 0
            step_y = int(speed * (delta_y / distance)) if distance != 0 else 0

            # новая позиция персонажа
            new_x = character_pos.x() + step_x
            new_y = character_pos.y() + step_y

            # перемещение персонажа
            self.character.move(new_x, new_y)

            # когда персонан в курсоре центрируем его на позиции курсора
            if distance < self.speed:
                self.character.move(target_x, target_y)
        # else:
        #     # случайное движение
        #     x_move = random.choice([-self.speed, 0, self.speed])
        #     y_move = random.choice([-self.speed, 0, self.speed])
        #     current_position = self.character.pos()
        #     new_position = current_position + QPoint(x_move, y_move)

        #     # проверка границ
        #     if (0 <= new_position.x() <= self.width() - self.character.width() and
        #         0 <= new_position.y() <= self.height() - self.character.height()):
        #         self.character.move(new_position)


    def start_following(self):
        if(self.following):
            self.following = False
        else:
            self.following = True

    def stop_character(self):
        self.is_moving = False  # остановить движение персонажа

    def continue_character(self):
        self.is_moving = True  # продолжить движение персонажа

    def set_default_animation(self):
        # self.character.setMovie(self.default_gif)
        # self.default_gif.start()
        pass

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.mouse_dragging = True
            self.drag_position = event.pos()  # начальная позиция мыши
            self.is_moving = False  # останавливаем движение персонажа при перетаскивании окна
            self.timer.stop()

    def mouseMoveEvent(self, event):
        if self.mouse_dragging:
            # перемещение окна
            self.move(self.pos() + event.pos() - self.drag_position)

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.mouse_dragging = False  # остановить перетаскивание
            self.is_moving = True  # включаем движение персонажа, когда окно перестает перетаскиваться
            self.timer.start()

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Q:
            if self.button_panel.isHidden():
                # положение панели относительно главного окна
                self.button_panel.move(0 + 10, 0 + 10)
                self.button_panel.show()
            else:
                self.button_panel.hide()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
