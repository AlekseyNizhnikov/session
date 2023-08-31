from kivymd.app import MDApp
from kivymd.uix.scrollview import MDScrollView
from kivymd.uix.floatlayout import MDFloatLayout
from kivymd.uix.toolbar import MDTopAppBar, MDBottomAppBar
from kivymd.uix.label import MDLabel
from kivymd.uix.screenmanager import MDScreenManager
from kivymd.uix.screen import MDScreen
from kivymd.uix.list import MDList, OneLineIconListItem, IconLeftWidget, TwoLineIconListItem, OneLineListItem
from kivymd.uix.card import MDCardSwipe, MDCardSwipeLayerBox, MDCardSwipeFrontBox, MDCard
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.textfield import MDTextField
from kivymd.uix.button import MDFlatButton, MDRectangleFlatIconButton
from kivymd.uix.scrollview import MDScrollView
from kivymd.uix.gridlayout import MDGridLayout
from kivymd.uix.behaviors import TouchBehavior
from kivymd.uix.dialog import MDDialog
from kivymd.uix.fitimage import FitImage
from kivymd.uix.filemanager import MDFileManager
from kivymd.uix.expansionpanel import MDExpansionPanel, MDExpansionPanelOneLine
from kivymd.uix.pickers import MDDatePicker
import datetime
import sqlite3
import json
import os
from PIL import Image
from io import BytesIO
import shutil
from kivy.utils import platform

if platform == "android":
    from android.permissions import request_permissions, Permission
    request_permissions([Permission.WRITE_EXTERNAL_STORAGE, Permission.READ_EXTERNAL_STORAGE])
    from android.storage import primary_external_storage_path
    primary_ext_storage = primary_external_storage_path()
else:
    primary_ext_storage = "./"

#summ = self.ui.findChild(QtWidgets.QLineEdit, "summ")


from kivy.core.window import Window
Window.size = (370, 770)


class CallableDownBar(MDTopAppBar):
    """
    Класс обеспечивает функционирование кнопки нижнего топ-бара.
    """

    def callable(self):
        """
        Метод обрабатывает нажатие кнопки нижнего топ-бара. В зависимости от экрана, с которого произошел вызов,
        выполняется, добавление нового журнала, его удалание, либо перемещение на домашнюю страницу.
        :return:
        """
  
        name_screen = self.parent.parent.parent.name
        main_screen = self.parent.parent.parent.parent

        if name_screen in ("my_journal", "top_title"):
            self.parent.parent.parent.parent.parent.parent.parent.add_screen("Завести новый журнал", "input_data_journal")
            self.parent.parent.parent.parent.parent.parent.parent.current = "input_data_journal"
        
        elif name_screen == "set_user":
            name = self.parent.parent.children[0].children[1].title # имя журнала
            screen = self.parent.parent

            weight = screen.children[2].children[0].children[3].text.capitalize()
            height = screen.children[2].children[0].children[2].text.capitalize()
            age = screen.children[2].children[0].children[1].text
            phone = screen.children[2].children[0].children[0].text

            father_name = screen.children[1].children[0].text.capitalize()
            first_name = screen.children[1].children[1].text.capitalize()
            second_name = screen.children[1].children[2].text.capitalize()

            journal_id = app.cursor_base.execute(f"SELECT journal_id FROM Journals WHERE name_journal = '{name}'").fetchall()[-1][0]
            user_id = app.cursor_base.execute(f"SELECT user_id FROM Users").fetchall() or 1
            
            if user_id != 1:
                user_id = user_id[-1][0] + 1
            if not os.path.isfile(f"./users_avatar/{name}/test_user.png"):
                with Image.open(f"./Images/user.png") as img:
                    b = BytesIO()
                    img.save(b, "png")
                    b.seek(0)
                    byteImg = b.read()
                
            else:
                with Image.open(f"./users_avatar/{name}/test_user.png") as img:
                    b = BytesIO()
                    img.save(b, "png")
                    b.seek(0)
                    byteImg = b.read()
                os.remove(f"./users_avatar/{name}/test_user.png")

            app.cursor_base.execute(f"""INSERT INTO Users (user_id, journal_id, fname, lname, faname, weight, height, age, phone, img)
                                   VALUES('{user_id}', '{journal_id}', '{first_name}', '{second_name}', '{father_name}', '{weight}', '{height}', '{age}', '{phone}', ?);""", [byteImg])

            date = json.dumps([{datetime.datetime.today().strftime("%Y %b"):{datetime.datetime.today().strftime("%d"): 2}}])
            app.cursor_base.execute(f"""INSERT INTO Data (user_id, journal_id, session_log) VALUES('{user_id}', '{journal_id}','{date}');""")
            
            app.base.commit()

            app.update_users(name, [user_id, journal_id, first_name, second_name, father_name, weight, height, age, phone], data=date)
            
            self.parent.parent.parent.parent.current = name
            screen.parent.parent.remove_widget(screen.parent)

        elif name_screen == "input_data_journal":
            screen = self.parent.parent.parent.parent.get_screen(name_screen)

            name_journal = screen.children[0].children[1].children[1].text.capitalize()
            description = screen.children[0].children[1].children[0].text.capitalize() or "Добавить комментарий"
            app.cursor_base.execute(f"""INSERT INTO Journals (name_journal, description) VALUES('{name_journal}', '{description}');""")

            app.base.commit()
            app.update_journals(name_journal, description)

            self.parent.parent.parent.current = "TopScreen"
            screen.parent.remove_widget(screen)

        elif name_screen in ("statistics","settings","contacts","about", "data_base"):
            main_screen.current = "top_title"

        else:
            name_journal = self.parent.parent.parent.name
            main_screen.add_screen("Добавить пользователя", "set_user", name_journal)
            main_screen.current = "set_user"
        
    on_action_button = callable


class ContentNavigation(MDList):
    """
    Класс содержит методы для управления пунктами навигационного меню.
    """

    def add_item_menu(self, title_name, screen_name, icon_name):
        """
        Метод добавляет в меню навигации дополнительный элемент.
        На вход принимает наименование пункта меню, имя иконки и имя страницы на которую нужно перейти при касание.

        :param title_name: название пункта меню.
        :param screen_name: имя экрана для перехода по касанию.
        :param icon_name: имя иконки из библиотеки kivy.
        :return:
        """

        self.add_widget(OneLineIconListItem(IconLeftWidget(icon=icon_name), id=screen_name, text=title_name,
                                            on_press=lambda x: self.callable(screen_name)))

    def callable(self, screen_name):
        """
        Метод вызывает при касании пункта меню и выполняет переход на страницу.
        На вход принимает имя страницы.

        :param screen_name: имя страницы для перехода.
        :return:
        """

        navigation_drawer = self.parent.parent.parent
        screen_manager = self.parent.parent.parent.parent.children[1]

        screen_manager.current = screen_name
        navigation_drawer.set_state("close")


class ScreenMenu(MDScreenManager):
    """
    Класс менеджера экрана. Осуществляет добавление экрана в менеджер экранов.
    """

    def add_screen(self, title_name, screen_name, nav_drawer):
        """
        Метод создает новый экран в менеджере экранов. Здесь же осуществляется наполение его контентом.
        :param title_name: титульная надпись страницы.
        :param screen_name: имя страницы для обращения внутри классов.
        :param nav_drawer: ссылка на объект навигационной панели.
        :return:
        """

        screen = MDScreen(name=f"{screen_name}")

        top_bar = MDTopAppBar(title=title_name, pos_hint={"top": 1}, md_bg_color=(0.11, 0.49, 0.27, 1),
                              left_action_items=[['menu', lambda x: nav_drawer.set_state("open")]])
        down_bar = MDBottomAppBar(CallableDownBar(icon="home", type="bottom", icon_color=(0.11, 0.49, 0.27, 1),
                                                  mode="end", elevation=0),
                                  md_bg_color=(0.11, 0.49, 0.27, 1))
        box = MDBoxLayout(orientation="vertical")
        box.add_widget(top_bar)

        if screen_name == "top_title":
            down_bar.children[1].icon = "plus"
            box.add_widget(MDScrollView(MDList(spacing="8dp")))

        if screen_name == "my_journal":
            down_bar.children[1].icon = "plus"
            box.add_widget(MDScrollView(MDList(spacing="8dp")))

        if screen_name == "settings":
            box.add_widget(SettingsBox())

        if screen_name == "statistics":
            box.add_widget(MDBoxLayout())

        if screen_name == "contacts":
            box.add_widget(ContactsBox())

        if screen_name == "data_base":
            box.add_widget(MDFloatLayout(MDRectangleFlatIconButton(text="Сохранить базу данных", icon="database-export", line_color=(0,0,0,0), on_press=lambda x: self.fun_1(), font_size="20sp", pos_hint={"center_x": 0.5, "center_y": 0.9}, theme_text_color="Custom", icon_color = (0.11, 0.49, 0.27, 1), text_color=(0.11, 0.49, 0.27, 1)),
                                       MDRectangleFlatIconButton(text="Загрузить базу данных", icon="database-import", line_color=(0,0,0,0), on_press=lambda x: self.fun_2(), font_size="20sp", pos_hint={"center_x": 0.5, "center_y": 0.8}, theme_text_color="Custom", icon_color = (0.11, 0.49, 0.27, 1), text_color=(0.11, 0.49, 0.27, 1)),))

        if screen_name == "about":
            box.add_widget(AboutBox())

        box.add_widget(down_bar)
        screen.add_widget(box)
        self.add_widget(screen)

    def fun_2(self):
        pass

    def fun_1(self, *args):
        path = primary_ext_storage
        self.file_manager = MDFileManager(exit_manager=self.exit_manager,select_path=self.select_path, background_color_toolbar=(0.11, 0.49, 0.27, 1), icon_color=(0.11, 0.49, 0.27, 1), background_color_selection_button=(0.11, 0.49, 0.27, 1))
        self.file_manager.show(path)

    def file_manager_open(self):
        self.file_manager.show(primary_ext_storage)  
        self.manager_open = True

    def select_path(self, path: str):
        self.exit_manager()
        shutil.copyfile('Journals.db', f"./{path}/Journals.db")

    def exit_manager(self, *args):
        self.manager_open = False
        self.file_manager.close()


class SettingsBox(MDFloatLayout):
    pass


class AboutBox(MDFloatLayout):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        about_text = "Приложение предназначено для хранения, редактирования, создания и удаления журналов посещений, " \
                     "а также для фиксации посещаемости людей различных мероприятий, кружков или уроков.Программа позволяет" \
                     "отслеживать актуальные события, такие как: день рождения, пришел / не пришел, назначенное событие вами или" \
                     "время проведения тестирования сдача нормативов или ГТО.В приложении есть возможность создавать собственные" \
                     "анкеты тестирования, для отслеживания физического состояния человека, его эмоционального состояния."

        self.add_widget(MDLabel(text="О приложении",
                                halign="center",
                                font_style="H4",
                                pos_hint={"center_x": 0.5, "center_y": 0.83}))

        self.add_widget((MDLabel(text=about_text,
                                 padding=12,
                                 pos_hint={"center_x": 0.5, "center_y": 0.50})))


class ContactsBox(MDFloatLayout):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        dict_contacts = {"Разработчик": "Нижников Алексей Сергеевич",
                         "Дизайнер": "Возженникова Елизавета Константиновна",
                         "Почта": "leha_nizhnikov@mail.ru",
                         "Телефон": "8(951)-784-73-32",
                         "Название организации": '"НижниковКорпорейшен"',
                         "Адрес": "Россия, Челябинская обл., г. Челябинск"}

        for key, val, i in zip(dict_contacts.keys(), dict_contacts.values(), range(1, len(dict_contacts) + 1)):
            self.add_widget(MDLabel(text=f"{key}: {val}",
                                    halign="left",
                                    pos_hint={"center_x": 0.52, "center_y": 1 - i / 12}))


class Content_2(MDBoxLayout):
    def __init__(self, name_journal, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.size_hint_y = None
        self.height = "200dp"
        sc = MDScrollView()
        ls = MDList()
        journal_id = app.cursor_base.execute(f"SELECT journal_id FROM Journals WHERE name_journal = '{name_journal}'").fetchone()[0]
        data = app.cursor_base.execute(f"SELECT fname, lname, faname FROM Users WHERE journal_id = '{journal_id}'").fetchall()
        for dt in data:
            ls.add_widget(OneLineIconListItem(text = f"{dt[1]} {dt[0][0]}.{dt[0][0]}."))
        sc.add_widget(ls)
        self.add_widget(sc)

class MainScreen(MDScreenManager):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.list = MDList(spacing="4dp")

    def my_callback(self, *args):
        path = os.path.expanduser("~")
        self.file_manager = MDFileManager(
            exit_manager=self.exit_manager,
            select_path=self.select_path,
        )
        self.file_manager.show(path)

    def file_manager_open(self):
        self.file_manager.show(os.path.expanduser("~"))  
        self.manager_open = True

    def select_path(self, pathh: str):
        self.exit_manager()
        with Image.open(pathh) as img:
            img.load()
            low_res_img = img.resize((img.width // 8, img.height // 8))
            if not os.path.isdir("users_avatar"):
                os.mkdir("users_avatar")
            if not os.path.isdir(f"./users_avatar/{self.name_journal}"):
                os.mkdir(f"./users_avatar/{self.name_journal}")
            low_res_img.save(f"./users_avatar/{self.name_journal}/test_user.png")

        app.root.get_screen("set_user").children[0].children[2].children[1].children[0].source = f"./users_avatar/{self.name_journal}/test_user.png"


    def exit_manager(self, *args):
        self.manager_open = False
        self.file_manager.close()

    def add_screen(self, title_name, screen_name, name_journal=None):
        self.name_journal = name_journal
        screen = MDScreen(name=screen_name)
        
        top_bar = MDTopAppBar(title=title_name, pos_hint={"top": 1}, md_bg_color=(0.11, 0.49, 0.27, 1))
        down_bar = MDBottomAppBar(CallableDownBar(icon="home", type="bottom", icon_color=(0.11, 0.49, 0.27, 1),
                                                 mode="end", elevation=0),
                                 md_bg_color=(0.11, 0.49, 0.27, 1))
        
        box = MDBoxLayout(orientation="vertical")
        box.add_widget(top_bar)

        if screen_name == "input_data_journal":
            down_bar.children[1].icon = "chevron-right"
            down_bar.children[1].left_action_items=[["chevron-double-left", lambda x: self.fun(screen_name)]]
            down_bar.children[1].title="К журналам..."
            text_box = MDFloatLayout(MDTextField(hint_text="Название журнала", pos_hint={"center_x": 0.5, "center_y": 0.8}, size_hint_x=0.8),
                                     MDTextField(hint_text="Краткое описание", helper_text="Не более 100 символов", helper_text_mode="persistent",
                                      pos_hint={"center_x": 0.5, "center_y": 0.7}, size_hint_x=0.8))
            box.add_widget(text_box)
        
        elif screen_name == "statistic_journal":
            box_content = MDFloatLayout()
            box_grid = MDGridLayout(spacing="4dp", padding="4dp", cols=2, rows=4, size_hint_y = None, height = "150 dp", pos_hint = {"top": 1})
            box_grid.add_widget(MDLabel(text = "Кол-во учеников: ", halign = "left"))
            box_grid.add_widget(MDLabel(text = "Макс. возраст: ", halign = "left"))
            box_grid.add_widget(MDLabel(text = "Мин. возраст: ", halign = "left"))
            box_grid.add_widget(MDLabel(text = "Кол-во мальчиков: ", halign = "left"))
            box_grid.add_widget(MDLabel(text = "Кол-во девочек: ", halign = "left"))
            box_grid.add_widget(MDLabel(text = "Средняя посещаемость: ", halign = "left"))

            sc = MDScrollView(pos_hint = {"center_x": 0.51, "center_y": 0.5})
            ls = MDList()
            panel_1 = MDRectangleFlatIconButton(text=" Добавить событие...", pos_hint = {"center_x": 0.5})
            panel_2 = MDExpansionPanel(panel_cls = MDExpansionPanelOneLine(text=" Список учеников..."), content = Content_2(title_name))
            ls.add_widget(box_grid)
            ls.add_widget(panel_1)
            ls.add_widget(panel_2)
            sc.add_widget(ls)
            box_content.add_widget(sc)
            box.add_widget(box_content)

        elif screen_name == "set_user":
            down_bar.children[1].icon = "chevron-right"
            down_bar.children[1].left_action_items=[["chevron-double-left", lambda x: self.fun_1(screen_name, name_journal)]]
            down_bar.children[1].title=name_journal
            text_box = MDFloatLayout(MDTextField(hint_text="Фамилия пользователя", pos_hint={"center_x": 0.5, "center_y": 0.8}, size_hint_x=0.8),
                                     MDTextField(hint_text="Имя пользователя", pos_hint={"center_x": 0.5, "center_y": 0.7}, size_hint_x=0.8),
                                     MDTextField(hint_text="Отчество пользователя", pos_hint={"center_x": 0.5, "center_y": 0.6}, size_hint_x=0.8))
            
            user_box = MDBoxLayout(MDCard(FitImage(source="./Images/user.png", size_hint_x=None, size_hint_y=None, height="195dp", width="130dp", pos_hint={"center_x": 0.5, "center_y": 0.5}),
                                          size_hint_x=None, size_hint_y=None, height="195dp", width="130dp", pos_hint={"center_x": 0.5, "center_y": 0.1}, md_bg_color=(1, 0.3, 0.5, 1),
                                          on_press=lambda x: self.my_callback()),
                                   MDFloatLayout(MDTextField(hint_text="Вес", pos_hint={"center_x": 0.5, "center_y": 0.8}, size_hint_x=0.5),
                                               MDTextField(hint_text="Рост", pos_hint={"center_x": 0.5, "center_y": 0.6}, size_hint_x=0.5),
                                               MDTextField(hint_text="Возраст", pos_hint={"center_x": 0.5, "center_y": 0.4}, size_hint_x=0.5),
                                               MDTextField(hint_text="Телефон", pos_hint={"center_x": 0.5, "center_y": 0.2}, size_hint_x=0.5),
                                               MDTextField(hint_text="Пол", pos_hint={"center_x": 0.5, "center_y": 0.0}, size_hint_x=0.5),
                                               size_hint_y=None, height="200dp", pos_hint={"center_x": 0.5, "center_y": 0.35}),
                                    orientation="horizontal", size_hint_y=None, height="200dp", pos_hint={"center_x": 0.5, "center_y": 0.35}, padding="40dp")
            box.add_widget(user_box)
            box.add_widget(text_box)

        else: 
            down_bar.children[1].icon="plus"
            down_bar.children[1].left_action_items=[["chevron-double-left", lambda x: self.fun_2(screen_name)]]
            down_bar.children[1].title="К журналам..."
            dict_mounth = {"01":"Января", "02":"Февраля", "03":"Марта", "04":"Апреля", "05":"Майя", "06":"Июня", "07":"Июля", "08":"Августа", "09":"Сентября", "10":"Октября", "11":"Ноября", "12":"Декабря"}
            year, mounth, day = str(datetime.date.today()).split("-")

            box.add_widget(MDBoxLayout(MDLabel(text=f"{day} {dict_mounth.get(mounth)} {year} г.", halign="center", font_size="18dp", text_color=(1,1,1,1), theme_text_color="Custom"),
                                    orientation="vertical", md_bg_color=(0.11, 0.49, 0.27, 1), size_hint_y=None, height="50dp"))

            scr = MDScrollView()
            scr.add_widget(MDList(spacing="4dp"))
            layout = MDGridLayout(pos_hint={"center_y":0.60}, spacing="14dp", padding="4dp", cols=8, rows=1, size_hint=(None, None), size=("355dp", "10dp"))
            layout.add_widget(MDBoxLayout(size_hint=(None, None), size = ("130dp", "10dp"), pos_hint={"top": 1}))
            days = {"Mon": "Пн", "Tue": "Вт", "Wed": "Ср", "Thu": "Чт", "Fri": "Пт", "Sat": "Сб", "Sun": "Вс"}
            for day, val in days.items():

                card =  MDLabel(text=val, halign="center", font_style="Overline", theme_text_color="Custom")
                if datetime.datetime.today().strftime("%a") == day:
                    card.font_style = "Caption"
                    card.text_color = "blue"
                    card.text = val.upper()
                layout.add_widget(card)
            b = OneLineListItem(height="10dp", size_hint_y=None, text="№        ФИО")

            b.add_widget(layout)
            box.add_widget(b)
            box.add_widget(scr)

        box.add_widget(down_bar)
        screen.add_widget(box)
        self.add_widget(screen)

        return screen

    def fun_2(self, screen_name):
        screen = self.get_screen(screen_name)
        self.current = "TopScreen"

    def fun(self, screen_name):
        print("Нажали кнопку вернуться к журналам")
        screen = self.get_screen(screen_name)
        self.current = "TopScreen"
        self.remove_widget(screen)

    def fun_1(self, screen_name, name_journal):
        print("Нажали кнопку вернуться к журналам")
        screen = self.get_screen(screen_name)
        self.current = name_journal
        self.remove_widget(screen)


class JournalCard(MDCard, TouchBehavior):

    # 0 - Отсутствовал
    # 1 - Присутствовал
    # 2 - Не числился

    def on_touch_down(self, touch):
        red = [0.44, 0.16, 0.16, 1]
        green = [0.11, 0.49, 0.27, 1]
        white = [0.8, 0.8, 0.8, 1]

        name_user, *_ = self.parent.parent.parent.children[0].children[1].children[0].text.split("\n")
        name_journal = self.parent.parent.parent.parent.parent.parent.parent.children[0].children[4].title
        name_user = name_user.replace(" ", "")

        journal_id = app.cursor_base.execute(f"SELECT journal_id FROM Journals WHERE name_journal = '{name_journal}'").fetchone()[0]
        name_user = name_user.replace(" ", "")

        user_id = app.cursor_base.execute(f"SELECT user_id FROM Users WHERE journal_id = '{journal_id}' AND lname = '{name_user[:-3]}'").fetchone()[0]

        data = json.loads(app.cursor_base.execute(f"""SELECT session_log FROM Data WHERE user_id = '{user_id}';""").fetchone()[0])
        res = data[0].get(datetime.datetime.today().strftime("%Y %b"), {datetime.datetime.today().strftime("%d"): 0})

        if self.collide_point(*touch.pos):
            if touch.is_double_tap:
                if self.md_bg_color == white:
                    res[datetime.datetime.today().strftime("%d")] = 1
                    self.md_bg_color = green

                elif self.md_bg_color == green:
                    res[datetime.datetime.today().strftime("%d")] = 0
                    self.md_bg_color = red

                else:
                    res[datetime.datetime.today().strftime("%d")] = 2
                    self.md_bg_color = white

                data = json.dumps([{datetime.datetime.today().strftime("%Y %b"):res}])
                app.cursor_base.execute(f"""UPDATE Data SET session_log = '{data}' WHERE user_id = '{user_id}';""") 
                app.base.commit()

    def on_long_touch(self, *args):
        red = [0.44, 0.16, 0.16, 1]
        green = [0.11, 0.49, 0.27, 1]
        white = [1, 1, 1, 1]
        
        if self.children[0].text == "Р":
            dialog = MDDialog(text="Оплачено?", size_hint=(None, None), size=("300dp", "90dp"),
                            buttons=[
                                MDFlatButton(text="Да", text_color=white, md_bg_color=green, on_press=lambda x: fun_1()),
                                MDFlatButton(text="Нет", text_color=white, md_bg_color=red, on_press=lambda x: fun_2())])
            dialog.open()   
            
        def fun_1():
            self.line_color=(1, 1, 1, 1)
            dialog.dismiss(force=True)

        def fun_2():
            dialog.dismiss(force=True)


class Content(MDBoxLayout):
    pass


class SessionLog(MDApp):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.journals = []

    def update_journals(self, name_journal:str, description=""): 
        """
        Метод принимает на вход словарь журналов, добавляя их на стараницу журналов.
        """

        self.journals.append(self.root.add_screen(name_journal, name_journal))

        journal = TwoLineIconListItem(IconLeftWidget(icon="book-open-page-variant-outline"),
                                        on_press=lambda x: self.open_journal(name_journal),
                                        text=name_journal,
                                        secondary_text=description,
                                        _no_ripple_effect=True,
                                        pos_hint={"center_x":0.5, "center_y":0.5},
                                        bg_color=(0.9,0.9,0.9,1))
        
        self.root.ids.screen_manager.get_screen("top_title").children[0].children[1].children[0].add_widget(journal)

        card_journal = MDCardSwipe(MDCardSwipeLayerBox(IconLeftWidget(icon="delete")),
                                    MDCardSwipeFrontBox(
                                        TwoLineIconListItem(
                                            IconLeftWidget(icon="book-open-page-variant-outline"),
                                            text=name_journal,
                                            secondary_text=" ",
                                            _no_ripple_effect=True,
                                            bg_color=(0.9,0.9,0.9,1),
                                            on_press=lambda x: self.fun_4(name_journal))),
                                    size_hint_y=None,
                                    height="70dp",
                                    type_swipe="auto",
                                    on_swipe_complete=lambda x: self.remove_journal(card_journal, journal, name_journal),
                                    )

        self.root.ids.screen_manager.get_screen("my_journal").children[0].children[1].children[0].add_widget(card_journal)

    def fun_4(self, name_journal):
        self.root.add_screen(name_journal, "statistic_journal")
        self.root.current = "statistic_journal"

    def update_users(self, name_journal:str, users:list, data=""):
        """
        Метод обновляет список пользователей в журнале.
        """

        data = json.loads(self.cursor_base.execute(f"SELECT session_log FROM Data WHERE user_id = '{users[0]}'").fetchone()[0])

        screen = self.root.get_screen(name_journal)

        ls = screen.children[0].children[1].children[0]
        j =int(datetime.datetime.today().strftime("%w"))
        day = int(datetime.datetime.today().strftime("%d"))
        mounth = {"Jan":31, "Feb":28, "Mar":31, "Apr":30, "May":31,"Jun":30,"Jul":31,"Aug":31,"Sep":30, "Oct":31,"Nov":30,"Dec":31}

        if day + 7 <= mounth[datetime.datetime.today().strftime("%b")]:
            _DAYS = [str(i) for i in range(day - (6 - (7 - j)), day + (8 - j))]
            count = 0
            for i in (range(6, -1, -1)):
                if int(_DAYS[i]) <= 0:
                   test = datetime.datetime.today() - datetime.timedelta(days = day + count)
                   _DAYS[i] = test.strftime("%d")
                   count += 1
        else:
            _DAYS = [str(i) for i in range(day, 31 + 1)]
            ln = len(_DAYS)
            for i in range(1, (8 - ln)):
                _DAYS.append(str(i))

        box_childrens = MDBoxLayout(MDLabel(text=str(users[0]), pos_hint={"left": 1,"center_y":0.5}, size_hint_x=None, width="15dp", font_style="Caption"),
                                    orientation="horizontal", padding="10dp", spacing="2dp")
        user_labels = MDBoxLayout(MDFlatButton(text=f"{users[3]} {users[2][0]}.{users[4][0]}\n{users[8]}", font_style="Caption", pos_hint={"center_y":0.5}, on_press=lambda x: self.fun(x)),
                                   size_hint_x=None, width="115dp")


        day_labels = [MDLabel(text=item, halign="center", font_style="Overline") for item in _DAYS]
        layout = MDGridLayout(pos_hint={"center_y":0.45}, spacing="7dp", padding="4dp", cols=7, rows=1)
        flag = False
        for day in day_labels:
            card = JournalCard(elevation=1, ripple_behavior=True, md_bg_color=(0.8, 0.8, 0.8, 1), size_hint=(None, None), size=("23dp", "23dp"))
            dd = day.text
            if int(dd) < 10:
                dd = "0" + dd

            if int(dd) == int(datetime.datetime.today().strftime("%d")):
                flag = True

            if flag == False:
                mon = datetime.datetime.today().strftime("%Y %b")
                if mon in data[0] and dd in data[0].get(mon):
                    if data[0].get(mon).get(dd) == 1:
                        card.md_bg_color = (0.11, 0.49, 0.27, 1)
                    elif data[0].get(mon).get(dd) == 0:
                        card.md_bg_color = (0.44, 0.16, 0.16, 1)
                if day.text == "Р":
                    card.line_color=(0.11, 0.49, 0.27, 1)
            card.add_widget(day)
            
            layout.add_widget(card)

        box_childrens.add_widget(user_labels)
        box_childrens.add_widget(layout)
        card_swipe = MDCard(box_childrens, size_hint_y=None, height="60dp")
        ls.add_widget(card_swipe)

    def fun(self, instance):
        name_user, *_ = instance.children[0].text.split("\n")
        user_id = instance.parent.parent.children[2].text
        result = app.cursor_base.execute(f"SELECT * FROM Users WHERE user_id = '{user_id}'").fetchone()
        name_journal = app.cursor_base.execute(f"SELECT name_journal FROM Journals WHERE journal_id = '{result[1]}'").fetchone()[0]
        
        box = MDBoxLayout(orientation="vertical", spacing="8dp", padding="8dp")
        box.add_widget(MDLabel(text=name_user))
        box.add_widget(MDLabel(text=f"Возраст: {result[7]} лет"))
        box.add_widget(MDLabel(text=f"Вес: {result[5]} кг"))
        box.add_widget(MDLabel(text=f"Рост: {result[6]} см"))
        box.add_widget(MDLabel(text="Пол: М"))
        box.add_widget(MDLabel(text=f"Телефон: {result[8]}"))
        io_bytes = BytesIO(result[9])
        img = Image.open(io_bytes)

        if not os.path.isdir("users_avatar"):
            os.mkdir("users_avatar")
        if not os.path.isdir(f"./users_avatar/{name_journal}"):
            os.mkdir(f"./users_avatar/{name_journal}")

        img.save(f'./users_avatar/{name_journal}/{user_id}_{result[1]}_{name_user}.png')
        dialog_1 = MDDialog(size_hint=(None, None), size=("340dp", "200dp"), title="Карточка пользователя", type="custom",
                            content_cls=Content(FitImage(source=f'./users_avatar/{name_journal}/{user_id}_{result[1]}_{name_user}.png', size_hint_x=None, size_hint_y=None, height="120dp", width="80dp"),
                                                box))
        
        dialog_1.open()   

    def open_journal(self, name_journal):
        """
        Метод создает экран журнала, на котором отображает список пользователей.
        """

        self.root.current = name_journal

    def remove_journal(self, card_journal, journal, name_journal):
        """
        Метод удаляет виджет из списка двух экранов.
        :param card_journal: ссылка на карточку с журналом экрана my_journal.
        :param journal: ссылка на журнал с экрана top_title.
        :return:
        """

        journal_id = self.cursor_base.execute(f"SELECT journal_id FROM Journals WHERE name_journal = '{name_journal}'").fetchone()[0]
        self.cursor_base.execute(f"DELETE FROM Data WHERE journal_id='{journal_id}';")
        self.cursor_base.execute(f"DELETE FROM Users WHERE journal_id='{journal_id}';")
        self.cursor_base.execute(f"DELETE FROM Journals WHERE journal_id='{journal_id}';")

        self.base.commit()
        self.journals.pop(self.journals.index(self.root.get_screen(name_journal)))

        card_journal.parent.remove_widget(card_journal)
        journal.parent.remove_widget(journal)

    def on_start(self):
        """
        Метод запускает приложение. Инициализирует переменные и формирует интерфейс приложения.
        """

        _NAME_DB = "Journals.db" 
        nav_drawer = self.root.ids.nav_drawer
        screen_names = {"Журнал посещений": ("top_title", "home"),
                        "Управление журналами": ("my_journal", "book-open-variant"),
                        "Статистика": ("statistics", "finance"),
                        "Настройки": ("settings", "cog"),
                        "Контакты": ("contacts", "phone-classic"),
                        "База данных": ("data_base", "database"),
                        "О приложении": ("about", "information-outline")}

        """Создаем экраны меню."""
        for title_name, data in screen_names.items():
            screen_name, icon_name = data
            self.root.ids.screen_manager.add_screen(title_name, screen_name, nav_drawer)
            self.root.ids.cnd.add_item_menu(title_name, screen_name, icon_name)

        """Подключаемся к базе данных."""
        self.base = sqlite3.connect(_NAME_DB)
        self.cursor_base = self.base.cursor()
        
        app.cursor_base.execute(f"""CREATE TABLE IF NOT EXISTS Journals(
                                                                        journal_id INTEGER PRIMARY KEY AUTOINCREMENT,
                                                                        name_journal TEXT,
                                                                        description TEXT);""")

        app.cursor_base.execute(f"""CREATE TABLE IF NOT EXISTS Users(
                                                                    user_id INTEGER PRIMARY KEY,
                                                                    journal_id INTEGER REFERENCES JOURNALS(journal_id) ON UPDATE CASCADE,
                                                                    fname TEXT,
                                                                    lname TEXT,
                                                                    faname TEXT,
                                                                    weight TEXT,
                                                                    height TEXT,
                                                                    age INT,
                                                                    phone TEXT,
                                                                    img BLOB );""")

        app.cursor_base.execute(f"""CREATE TABLE IF NOT EXISTS Data(
                                                                    data_id INTEGER PRIMARY KEY AUTOINCREMENT,
                                                                    user_id INTEGER REFERENCES USERS(user_id) ON UPDATE CASCADE,
                                                                    journal_id INTEGER REFERENCES JOURNALS(journal_id) ON UPDATE CASCADE,
                                                                    session_log TEXT);""")

        journals = self.cursor_base.execute(f"SELECT * FROM Journals;").fetchall()

        for journal in journals:
            self.update_journals(journal[1], journal[2])
            users = self.cursor_base.execute(f"SELECT * FROM Users WHERE journal_id = '{journal[0]}'").fetchall()

            if users != []:
                for user in users:
                    self.update_users(journal[1], user)

    def par(self, other):
        other.md_bg_color = (0.2, 0.1, 1, 1)


if __name__ == "__main__":
    app = SessionLog()
    app.run()
