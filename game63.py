import sys
import sqlite3
from PyQt5 import uic
from PyQt5.QtWidgets import QApplication, QMainWindow, QInputDialog
from PyQt5.QtWidgets import QColorDialog
from PyQt5.QtGui import QPixmap, QFont
from random import shuffle

dict_values = {'2': '2', '3': '3', '4': '4', '5': '5', '6': '6', '7': '7', '8': '8',
               '9': '9', '10': '10', 'Джокер': 'j', 'Валет': 'v', 'Дама': 'd',
               'Король': 'k', 'Туз': 't'}
list_images = ['21.png', '22.png', '23.png', '24.png', '31.png', '32.png', '33.png',
               '34.png', '41.png', '42.png', '43.png', '44.png', '51.png', '52.png',
               '53.png', '54.png', '61.png', '62.png', '63.png', '64.png', '71.png',
               '72.png', '73.png', '74.png', '81.png', '82.png', '83.png', '84.png',
               '91.png', '92.png', '93.png', '94.png', '101.png', '102.png', '103.png',
               '104.png', 'v1.png', 'v2.png', 'v3.png', 'v4.png', 'd1.png', 'd2.png',
               'd3.png', 'd4.png', 'k1.png', 'k2.png', 'k3.png', 'k4.png', 't1.png',
               't2.png', 't3.png', 't4.png', 'j5.png', 'j6.png']


class Cardinal(QMainWindow):
    def __init__(self):
        super().__init__()
        self.player = None  # номер игрока
        self.name1 = None  # имя певого игрока
        self.name2 = None  # имя второго игрока
        self.sum_real = None  # реальная сумма карт
        self.sum_not_real = None  # оглашённая сумма
        self.value = None  # значение оглашённой карты
        self.suit = None  # масть оглашённой карты
        self.list_images = None  # список перемешанной колоды
        self.pm_last_image = None  # изображение предыдущей оглашённой карты
        self.pm_ur_image = None  # изображение карты игрока
        self.flag_cb_activation = False  # флаг, показывающий активность ComboBox
        self.color_theme = None  # цвет интерфейса
        self.real_cards = None  # карты, которые были использованы за игру
        self.flag_error_name = False  # флаг, показывающий ошибку в длине имени
        self.real_price = None  # цена реальной карты
        self.flag_cb_turn = False  # флаг, показывающий активность CB отвечающего за ход
        self.back_pic = None  # название картинки, которая будет задним фоном
        self.started = False  # была ли начата игра?
        self.flag_dark = None  # тёмная тема?
        self.font_size = None  # размер шрифта
        self.menu()

    def menu(self):
        """ главное меню """
        uic.loadUi('menu.ui', self)

        self.design_menu()

        if self.flag_error_name:
            self.lbl_error.setText('Максимальная длинна имени - 12 символов!')
            self.flag_error_name = False

        if self.started:  # проявление кнопки ПРОДОЛЖИТЬ
            self.b_start.move(210, 230)
            self.b_continue.move(430, 230)
            self.b_continue.clicked.connect(self.remain)

        self.b_rules.clicked.connect(self.rules)
        self.b_settings.clicked.connect(self.settings)
        self.b_start.clicked.connect(self.new_game)

    def remain(self):
        """ Для передачи аргумента
        (чтобы понимать была ли начата игра) """
        self.resume(False)

    def rules(self):
        """ правила """
        uic.loadUi('rules.ui', self)

        self.design_rules()

        self.b_menu.clicked.connect(self.menu)

    def start(self):
        """ поле игры """
        uic.loadUi('game.ui', self)

        self.design_start()

        self.lbl_name.setText(self.player)
        self.lcd_sum.display(self.sum_not_real)

        self.cb_value.addItems(['2', '3', '4', '5', '6', '7', '8', '9', '10',
                                'Джокер', 'Валет', 'Дама', 'Король', 'Туз'])
        self.cb_suit.addItems(['Червы', 'Бубны', 'Трефы', 'Пики'])

        self.cb_value.activated[str].connect(self.cb_activated)  # активация ComboBox
        self.cb_suit.activated[str].connect(self.cb_activated)

        if not self.flag_cb_activation:  # значения по-умолчанию в CB
            self.value = '2'
            self.suit = 'Червы'

        if self.list_images:  # работа с изображениями (для избежания ошибок)
            image_name = self.list_images.pop(0)
            self.real_cards[str(54 - len(self.list_images)) + ' ' + self.player] = image_name

            with sqlite3.connect('cards.db') as con:  # работа с БД
                cur = con.cursor()
                self.real_price = cur.execute("""SELECT price FROM Cards
                            WHERE image = ?""", (image_name,)).fetchall()[0][0]

            self.pm_ur_image = QPixmap('images/{}'.format(image_name))

            self.lbl_ur_image.setPixmap(self.pm_ur_image)  # установка изображений
            if self.pm_last_image:
                self.lbl_last_image.setPixmap(self.pm_last_image)

        self.b_menu_g.clicked.connect(self.before_menu)
        self.b_ok.clicked.connect(self.finish_turn)
        self.b_pass.clicked.connect(self.win)

    def before_menu(self):
        """ специальная ф-ция для того, чтобы было можно продолжить игру """
        self.started = True
        self.list_images.append(self.real_cards.pop(str(54 - len(self.list_images))
                                                    + ' ' + self.player))
        shuffle(self.list_images)
        self.menu()

    def settings(self):
        """ окно для настройки интерфейса игры """
        uic.loadUi('settings.ui', self)

        self.design_settings()

        self.b_menu.clicked.connect(self.menu)
        self.b_color.clicked.connect(self.set_color)
        self.b_font_size.clicked.connect(self.set_font_size)

    def finish_turn(self):
        """ В момент нажатия кнопки ПАСС """
        if self.list_images:  # работа с изображениями
            with sqlite3.connect('cards.db') as con:  # работа с БД
                cur = con.cursor()

                suit = cur.execute("""SELECT id FROM Suits
                            WHERE name = ?""", (self.suit,)).fetchall()[0][0]
                value = dict_values[self.value]

                fake_image_name = cur.execute("""SELECT image FROM Cards
                            WHERE value = ? and suit = ? """, (value, suit)).fetchall()[0][0]

                not_real_price = cur.execute("""SELECT price FROM Cards
                            WHERE image = ?""", (fake_image_name,)).fetchall()[0][0]

            self.sum_not_real += not_real_price
            self.sum_real += self.real_price

            self.real_price = None  # для свободы памяти
            
            self.pm_last_image = QPixmap('images/{}'.format(fake_image_name))

            self.resume()
        else:
            self.lbl_stupid.setText('Не глупи! Нажимай кнопку ПАСС,\nсумма уже по-любому больше 63!')

    def resume(self, flag=True):
        """ доп экран для смены хода """
        uic.loadUi('resume.ui', self)

        self.design_resume()

        self.flag_cb_activation = False
        if flag:
            if self.player == self.name1:
                self.player = self.name2
            else:
                self.player = self.name1
        self.lbl_name.setText(self.player)
        self.b_resume.clicked.connect(self.start)

    def win(self):
        """ Экран победителя """
        uic.loadUi('pass.ui', self)
        self.started = False
        self.design_win()

        if self.sum_real > 63:  # выиграл игрок, который спассовал
            self.lbl_name.setText(self.player)
        else:  # игрок, который спассовал, проиграл
            if self.player == self.name1:
                self.player = self.name2
            else:
                self.player = self.name1
            self.lbl_name.setText(self.player)

        self.lcd_real_sum.display(self.sum_real)  # отображение реальной суммы

        self.b_menu.clicked.connect(self.menu)
        self.b_real_cards.clicked.connect(self.old_cards)

    def old_cards(self):
        """ окно с реальными картами """
        uic.loadUi('old_cards.ui', self)
        self.design_old_cards()

        for i in range(len(self.cb_turn)):
            self.cb_suit.removeItem(0)
        self.cb_turn.addItems(self.real_cards.keys())

        self.pic.setPixmap(QPixmap('images/{}'.format(self.real_cards[list(self.real_cards)[0]])))

        self.cb_turn.activated[str].connect(self.cb_activated)

        self.b_menu.clicked.connect(self.menu)

    def new_game(self):
        """ Первоначальные переменных для новой игры """
        self.player = False
        self.sum_real = 0
        self.sum_not_real = 0
        self.value = ''
        self.suit = ''
        self.list_images = list_images.copy()
        shuffle(self.list_images)
        self.real_cards = dict()
        self.pm_last_image = None
        self.ur_name()

    def ur_name(self):
        """ Диалоговый окна для получения имён игроков """
        self.name1, ok = QInputDialog.getText(self, "Введите имя", "Введите имя первого игрока")
        if self.check_names(self.name1, ok):
            self.name2, ok = QInputDialog.getText(self, "Введите имя", "Введите имя второго игрока")
            if self.check_names(self.name2, ok):
                self.resume()
            else:
                self.name2 = None
                self.menu()
        else:
            self.name1 = None
            self.menu()

    def check_names(self, name, ok):
        """ проверка длины имени """
        if len(name) > 12:
            self.flag_error_name = True
            return False
        return ok

    def cb_activated(self, text):
        """ Активация ComboBox """
        if self.sender() == self.cb_value:
            self.value = text
            if text == 'Джокер':
                self.remove_suits()
                self.cb_suit.addItems(['Красный', 'Чёрный'])
                self.suit = 'Красный'
            else:
                self.remove_suits()
                self.cb_suit.addItems(['Червы', 'Бубны', 'Трефы', 'Пики'])
                self.suit = 'Червы'
            self.flag_cb_activation = True
        elif self.sender() == self.cb_suit:
            self.suit = text
            self.flag_cb_activation = True
        elif self.sender() == self.cb_turn:
            # ставит картику в реальном времени
            self.pic.setPixmap(QPixmap('images/{}'.format(self.real_cards[text])))

    def remove_suits(self):
        """ удаление мастей из ComboBox """
        for i in range(len(self.cb_suit)):
            self.cb_suit.removeItem(0)

    def set_font_size(self):
        """ Диалоговое окно для получения размера шрифта """
        size, ok = QInputDialog.getText(self, "Размер шрифта",
                                        "Рекомендованный диапозон: от 8 до 14")
        if ok:
            if size.isdigit() and int(size) < 100:
                self.font_size = int(size)
                self.lbl_error.setText('')
                self.design_settings()  # для автоматического просмотра размера шрифта
            else:
                self.lbl_error.setText('Неправильный ввод: '
                                       'размер шрифта может быть только'
                                       'натуральным числом меньше 100')

    def set_color(self):
        """ Задача цветовой темы пользователем """
        color = QColorDialog.getColor()
        if color.isValid():
            self.color_theme = color.name()
            self.flag_dark = self.color_theme and int(self.color_theme[1:3], 16) + \
                int(self.color_theme[1:3], 16) + int(self.color_theme[1:3], 16) <= 200
            self.design_settings()  # для автоматического просмотра цветовой темы

    def design_settings(self):
        """ Дизайн поля настроек """
        self.setWindowTitle('63')
        if self.font_size:  # чтобы был шрифт по умолчанию
            self.lbl_settings.setFont(QFont("Times", self.font_size, QFont.Normal))
        else:
            self.lbl_settings.setFont(QFont("Times", 36, QFont.Normal))
        self.lbl_back_pic.setStyleSheet("background-color:{}".format(self.color_theme))
        if self.flag_dark:  # чтобы текст был виден
            self.lbl_settings.setStyleSheet("color: #ffffff")
            self.lbl_error.setStyleSheet("color: #ffffff")
        else:
            self.lbl_settings.setStyleSheet("color: #000000")
            self.lbl_error.setStyleSheet("color: #000000")

    def design_resume(self):
        """ Дизайн поля прехода """
        self.setWindowTitle('63')
        if self.font_size:  # чтобы был шрифт по умолчанию
            self.lbl_player.setFont(QFont("Times", self.font_size, QFont.Normal))
            self.lbl_name.setFont(QFont("Times", self.font_size, QFont.Normal))
        else:
            self.lbl_player.setFont(QFont("Times", 20, QFont.Normal))
            self.lbl_name.setFont(QFont("Times", 20, QFont.Normal))
        self.lbl_back_pic.setStyleSheet("background-color:{}".format(self.color_theme))
        if self.flag_dark:  # чтобы текст был виден
            self.lbl_player.setStyleSheet("color: #ffffff")
            self.lbl_name.setStyleSheet("color: #ffffff")

    def design_start(self):
        """ Дезайн основного поля игры """
        self.setWindowTitle('63')
        if self.font_size:  # чтобы был шрифт по умолчанию
            self.lbl_player.setFont(QFont("Times", self.font_size, QFont.Normal))
            self.lbl_sum.setFont(QFont("Times", self.font_size, QFont.Normal))
            self.lbl_ur_card.setFont(QFont("Times", self.font_size, QFont.Normal))
            self.lbl_last_card.setFont(QFont("Times", self.font_size, QFont.Normal))
            self.lbl_oglashenie.setFont(QFont("Times", self.font_size, QFont.Normal))
            self.lbl_name.setFont(QFont("Times", self.font_size, QFont.Normal))
        else:
            self.lbl_player.setFont(QFont("Times", 14, QFont.Normal))
            self.lbl_sum.setFont(QFont("Times", 14, QFont.Normal))
            self.lbl_ur_card.setFont(QFont("Times", 20, QFont.Normal))
            self.lbl_last_card.setFont(QFont("Times", 14, QFont.Normal))
            self.lbl_oglashenie.setFont(QFont("Times", 14, QFont.Normal))
            self.lbl_name.setFont(QFont("Times", 14, QFont.Normal))
        self.lbl_back_pic.setStyleSheet("background-color:{}".format(self.color_theme))
        if self.flag_dark:  # чтобы текст был виден
            self.lbl_player.setStyleSheet("color: #ffffff")
            self.lbl_sum.setStyleSheet("color: #ffffff")
            self.lbl_ur_card.setStyleSheet("color: #ffffff")
            self.lbl_last_card.setStyleSheet("color: #ffffff")
            self.lbl_oglashenie.setStyleSheet("color: #ffffff")
            self.lbl_name.setStyleSheet("color: #ffffff")

    def design_win(self):
        """ Дизайн поля победителя игры """
        self.setWindowTitle('63')
        if self.font_size:  # чтобы был шрифт по умолчанию
            self.lbl_ura.setFont(QFont("Times", self.font_size, QFont.Normal))
            self.lbl_name.setFont(QFont("Times", self.font_size, QFont.Normal))
            self.lbl_real_sum.setFont(QFont("Times", self.font_size, QFont.Normal))
            self.lbl_win.setFont(QFont("Times", self.font_size, QFont.Normal))
        else:
            self.lbl_ura.setFont(QFont("Times", 20, QFont.Normal))
            self.lbl_name.setFont(QFont("Times", 15, QFont.Normal))
            self.lbl_real_sum.setFont(QFont("Times", 14, QFont.Normal))
            self.lbl_win.setFont(QFont("Times", 18, QFont.Normal))
        self.lbl_pic.setPixmap(QPixmap('images/jackpot.png'))
        self.lbl_back_pic.setStyleSheet("background-color:{}".format(self.color_theme))
        if self.flag_dark:  # чтобы текст был виден
            self.lbl_ura.setStyleSheet("color: #ffffff")
            self.lbl_name.setStyleSheet("color: #ffffff")
            self.lbl_real_sum.setStyleSheet("color: #ffffff")
            self.lbl_win.setStyleSheet("color: #ffffff")

    def design_menu(self):
        """ Дизайн меню """
        self.setWindowTitle('63')
        if self.font_size:  # чтобы был шрифт по умолчанию
            self.lbl_menu.setFont(QFont("Times", self.font_size, QFont.Bold))
        else:
            self.lbl_menu.setFont(QFont("Times", 32, QFont.Bold))
        self.lbl_back_pic.setStyleSheet("background-color:{}".format(self.color_theme))
        if self.flag_dark:  # чтобы текст был виден
            self.lbl_menu.setStyleSheet("color: #ffffff")

    def design_old_cards(self):
        """ Дизайн окна для карт, использованных в игре """
        self.setWindowTitle('63')
        self.lbl_back_pic.setStyleSheet("background-color:{}".format(self.color_theme))
        if self.flag_dark:  # чтобы текст был виден
            self.lbl.setStyleSheet("color: #ffffff")

    def design_rules(self):
        """ Дизайн сведений об игре """
        self.setWindowTitle('63')
        self.lbl_back_pic.setStyleSheet("background-color:{}".format(self.color_theme))
        if self.flag_dark:
            self.lbl_rules.setStyleSheet("color: #ffffff")
            self.lbl_name.setStyleSheet("color: #ffffff")
            self.lbl_name_2.setStyleSheet("color: #ffffff")
            self.lbl_wow_2.setStyleSheet("color: #ffffff")
            self.lbl_wow.setStyleSheet("color: #ffffff")
            self.lbl_wow_1.setStyleSheet("color: #ffffff")
            self.lbl_wow_3.setStyleSheet("color: #ffffff")


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = Cardinal()
    ex.show()
    sys.exit(app.exec_())
