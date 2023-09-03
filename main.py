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
from kivymd.uix.snackbar import Snackbar
import datetime
import json
import os
from PIL import Image
from io import BytesIO
import shutil
from kivy.utils import platform

from settings import _GREEN, _GRAY, _RED, _MOUNTH, _DAYS
from data_base import DataBase

data_base = DataBase()

if platform == "android":
    from android.permissions import request_permissions, Permission
    request_permissions([Permission.WRITE_EXTERNAL_STORAGE, Permission.READ_EXTERNAL_STORAGE])
    from android.storage import primary_external_storage_path
    primary_ext_storage = primary_external_storage_path()
else:
    primary_ext_storage = "./"

#summ = self.ui.findChild(QtWidgets.QLineEdit, "summ")


# from kivy.core.window import Window
# Window.size = (370, 770)


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
            app.dialog_journal()

        elif name_screen == "log_management":
            pass

        elif name_screen in ("statistics","settings","contacts","about", "data_base"):
            main_screen.current = "top_title"

        else:
            name_journal = self.parent.parent.parent.name
            app.dialog_user(name_journal)
        
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


class JournalCard(MDCard, TouchBehavior):
    def on_touch_down(self, touch):
        red = [0.44, 0.16, 0.16, 1]
        green = [0.11, 0.49, 0.27, 1]
        white = [0.8, 0.8, 0.8, 1]

        name_user, *_ = self.parent.parent.parent.children[0].children[1].children[0].text.split("\n")
        name_journal = self.parent.parent.parent.parent.parent.parent.parent.children[0].children[4].title
        name_user = name_user.replace(" ", "")

        journal_id = data_base.get_journal_id(name_journal)
        name_user = name_user.replace(" ", "")

        user_id = data_base.cursor.execute(f"SELECT user_id FROM Users WHERE journal_id = '{journal_id}' AND lname = '{name_user[:-3]}'").fetchone()[0]

        data = data_base.get_session_log(user_id, journal_id)
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
                data_base.update_row("Data", "session_log", "user_id", user_id, data)

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


class SetJournal(MDFloatLayout):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.size_hint = (None, None)
        self.size = ("100dp", "100dp")
        self.add_widget(MDTextField(hint_text="Название журнала", pos_hint={"center_x": 1.4, "center_y": 0.9}, size_hint_x = None, width = "270dp"))
        self.add_widget(MDTextField(hint_text="Краткое описание", helper_text="Не более 100 символов", helper_text_mode="persistent", pos_hint={"center_x": 1.4, "center_y": 0.5}, size_hint_x = None, width = "270dp"))


class SetUser(MDFloatLayout):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.size_hint = (None, None)
        self.size = ("100dp", "350dp")
        text_box = MDFloatLayout(MDTextField(hint_text="Фамилия пользователя", pos_hint={"center_x": 0.5, "center_y": 0.8}, size_hint_x = None, width = "290dp"),
                                 MDTextField(hint_text="Имя пользователя", pos_hint={"center_x": 0.5, "center_y": 0.65}, size_hint_x = None, width = "290dp"),
                                 MDTextField(hint_text="Отчество пользователя", pos_hint={"center_x": 0.5, "center_y": 0.5}, size_hint_x = None, width = "290dp"),
                                 pos_hint={"center_x": 1.4, "center_y": 0.1})
        
        user_box = MDBoxLayout(MDCard(FitImage(source="./Images/user.png", size_hint_x=None, size_hint_y=None, height="195dp", width="130dp"),
                                      size_hint_x=None, size_hint_y=None, height="195dp", width="130dp", pos_hint={"center_x": 0.5, "center_y": 0.1}, md_bg_color=(1, 0.3, 0.5, 1)),
                                orientation="horizontal", size_hint_y=None, height="200dp", pos_hint={"center_x": 0.4, "center_y": 0.98}, padding = "4dp", spacing="70dp")
        user_box.add_widget(MDFloatLayout(MDTextField(hint_text="Вес", pos_hint={"center_x": 0.5, "center_y": 0.8}, size_hint_x = None, width = "100dp"),
                                          MDTextField(hint_text="Рост", pos_hint={"center_x": 0.5, "center_y": 0.6}, size_hint_x = None, width = "100dp"),
                                          MDTextField(hint_text="Возраст", pos_hint={"center_x": 0.5, "center_y": 0.4}, size_hint_x = None, width = "100dp"),
                                          MDTextField(hint_text="Телефон", pos_hint={"center_x": 0.5, "center_y": 0.2}, size_hint_x = None, width = "100dp"),
                                          MDTextField(hint_text="Пол", pos_hint={"center_x": 0.5, "center_y": 0.0}, size_hint_x = None, width = "100dp"),
                                          size_hint_y=None, height="200dp", pos_hint={"center_x": 0.5, "center_y": 0.2}),)
        
        self.add_widget(user_box)
        self.add_widget(text_box)


class DialogUserInfo(MDFloatLayout):
    def __init__(self, name_journal, user_info, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.size_hint = (None, None)
        self.size = ("100dp", "200dp")

        user_id, journal_id, second_name, first_name, father_name, weight, height, age, phone, gender, img = user_info
        name_user = f"{second_name} {first_name[0]}.{father_name[0]}."

        io_bytes = BytesIO(img)
        img = Image.open(io_bytes)

        if not os.path.isdir("users_avatar"):
            os.mkdir("users_avatar")

        if not os.path.isdir(f"./users_avatar/{name_journal}"):
            os.mkdir(f"./users_avatar/{name_journal}")

        path_file = f'./users_avatar/{name_journal}/{user_id}_{second_name}_{first_name}_{father_name}.png'

        img.save(path_file)
        self.add_widget(MDLabel(markup = True, text = f"[color=#000000]{name_user}[/color]", pos_hint = {"center_x": 0.5, "center_y": 1}))
        self.add_widget(FitImage(source = path_file, size_hint_x=None, size_hint_y=None, height="160dp", width="100dp", md_bg_color = _GREEN, pos_hint = {"center_x": 0.5, "center_y": 0.5}))
        
        box_info = MDGridLayout(cols = 1, rows = 8, spacing = "4dp", padding = "4dp", pos_hint = {"center_x": 1.6, "center_y": 0.43})
        box_info.add_widget(MDLabel(text = f"Возраст: {age} лет", size_hint_x = None, width = "160dp"))
        box_info.add_widget(MDLabel(text = f"Вес: {weight} кг", size_hint_x = None, width = "160dp"))
        box_info.add_widget(MDLabel(text = f"Рост: {height} см", size_hint_x = None, width = "160dp"))
        box_info.add_widget(MDLabel(text = f"Пол: {gender}", size_hint_x = None, width = "160dp"))
        box_info.add_widget(MDLabel(text = f"Телефон: {phone}", size_hint_x = None, width = "160dp"))
        box_info.add_widget(MDLabel(text = f"Посещаемость: 1.0", size_hint_x = None, width = "160dp"))
        box_info.add_widget(MDLabel(text = f"Успеваемость: 1.0", size_hint_x = None, width = "160dp"))
        box_info.add_widget(MDLabel(text = f"", size_hint_x = None, width = "160dp"))

        self.add_widget(box_info)


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

        if screen_name == "log_management":
            box_content = MDGridLayout(cols = 2, rows = 4, spacing = "4dp", padding = "4dp")
            box_content.add_widget(MDTextField(hint_text="Название журнала", pos_hint={"center_x": 0.5, "center_y": 0.8}, size_hint_x = None, width = "290dp"))
            box_content.add_widget(MDTextField(hint_text="Название журнала", pos_hint={"center_x": 0.5, "center_y": 0.8}, size_hint_x = None, width = "290dp"))
            box_content.add_widget(MDTextField(hint_text="Название журнала", pos_hint={"center_x": 0.5, "center_y": 0.8}, size_hint_x = None, width = "290dp"))
            box_content.add_widget(MDTextField(hint_text="Название журнала", pos_hint={"center_x": 0.5, "center_y": 0.8}, size_hint_x = None, width = "290dp"))
            box_content.add_widget(MDTextField(hint_text="Название журнала", pos_hint={"center_x": 0.5, "center_y": 0.8}, size_hint_x = None, width = "290dp"))
            box_content.add_widget(MDTextField(hint_text="Название журнала", pos_hint={"center_x": 0.5, "center_y": 0.8}, size_hint_x = None, width = "290dp"))
            box_content.add_widget(MDTextField(hint_text="Название журнала", pos_hint={"center_x": 0.5, "center_y": 0.8}, size_hint_x = None, width = "290dp"))
            box_content.add_widget(MDTextField(hint_text="Название журнала", pos_hint={"center_x": 0.5, "center_y": 0.8}, size_hint_x = None, width = "290dp"))

            box.add_widget(box_content)
        else:
            down_bar.children[1].icon="plus"
            down_bar.children[1].left_action_items=[["chevron-double-left", lambda x: self.to_return_journals()]]
            down_bar.children[1].title="К журналам..."
            dict_mounth = {"01":"Января", "02":"Февраля", "03":"Марта", "04":"Апреля", "05":"Майя", "06":"Июня", "07":"Июля", "08":"Августа", "09":"Сентября", "10":"Октября", "11":"Ноября", "12":"Декабря"}
            year, mounth, day = str(datetime.date.today()).split("-")

            box.add_widget(MDBoxLayout(MDLabel(text=f"{day} {dict_mounth.get(mounth)} {year} г.", halign="center", font_size="18dp", text_color=(1,1,1,1), theme_text_color="Custom"),
                                    orientation="vertical", md_bg_color=(0.11, 0.49, 0.27, 1), size_hint_y=None, height="50dp"))

            scr = MDScrollView()
            scr.add_widget(MDList(spacing="4dp"))
            layout = MDGridLayout(pos_hint={"center_y":0.60}, spacing="14dp", padding="4dp", cols=8, rows=1, size_hint=(None, None), size=("355dp", "10dp"))
            layout.add_widget(MDBoxLayout(size_hint=(None, None), size = ("130dp", "10dp"), pos_hint={"top": 1}))
            
            for day, val in _DAYS.items():
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

    def to_return_journals(self):
        self.current = "TopScreen"


class SessionLog(MDApp):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.journals = []

    def on_start(self):
        """
        Метод запускает приложение. Инициализирует переменные и формирует интерфейс приложения.
        """

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

        journals = data_base.get_all_journals()
        for journal in journals:
            journal_id, name_journal, description = journal

            self.update_journals(name_journal, description)
            users = data_base.get_all_users(journal_id)

            if users != []:
                for user in users:
                    self.update_users(name_journal, user)

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
                                            on_release = lambda x: self.log_management(name_journal))),
                                    size_hint_y=None,
                                    height="70dp",
                                    type_swipe="auto",
                                    on_swipe_complete=lambda x: self.remove_journal(card_journal, journal, name_journal))

        self.root.ids.screen_manager.get_screen("my_journal").children[0].children[1].children[0].add_widget(card_journal)

    def log_management(self, name_journal):
        self.root.add_screen(name_journal, "log_management")
        self.root.current = "log_management"

    def update_users(self, name_journal:str, users:list, data=None):
        """
        Метод обновляет список пользователей в журнале.
        """

        screen = self.root.get_screen(name_journal)
        journals = screen.children[0].children[1].children[0]

        day_mounth = int(datetime.datetime.today().strftime("%d"))
        week_days = self.get_week_date()

        box_childrens = MDBoxLayout(MDLabel(text=str(users[0]), pos_hint={"left": 1,"center_y":0.5}, size_hint_x=None, width="15dp", font_style="Caption"),
                                    orientation="horizontal", padding="10dp", spacing="2dp")
        user_labels = MDBoxLayout(MDFlatButton(text=f"{users[3]} {users[2][0]}.{users[4][0]}\n{users[8]}", font_style="Caption", pos_hint={"center_y":0.5}, on_press=lambda x: self.dialog_user_info(name_journal, users)),
                                   size_hint_x=None, width="115dp")


        day_labels = [MDLabel(text=item, halign="center", font_style="Overline") for item in week_days]
        layout = MDGridLayout(pos_hint={"center_y":0.45}, spacing="7dp", padding="4dp", cols=7, rows=1)
        flag = False
        for day_mounth in day_labels:
            card = JournalCard(elevation=1, ripple_behavior=True, md_bg_color=_GRAY, size_hint=(None, None), size=("23dp", "23dp"))
            dd = day_mounth.text
            if int(dd) < 10:
                dd = "0" + dd

            if int(dd) == int(datetime.datetime.today().strftime("%d")):
                flag = True

            if flag == False:
                mon = datetime.datetime.today().strftime("%Y %b")
                # if mon in data[0] and dd in data[0].get(mon):
                #     if data[0].get(mon).get(dd) == 1:
                #         card.md_bg_color = _GREEN
                #     elif data[0].get(mon).get(dd) == 0:
                #         card.md_bg_color = (0.44, 0.16, 0.16, 1)
                if day_mounth.text == "Р":
                    card.line_color = _GREEN
            card.add_widget(day_mounth)
            
            layout.add_widget(card)

        box_childrens.add_widget(user_labels)
        box_childrens.add_widget(layout)
        card_swipe = MDCard(box_childrens, size_hint_y=None, height="60dp")
        journals.add_widget(card_swipe)

    def dialog_user_info(self, name_journal, user_info):
        dialog_1 = MDDialog(radius=[20, 7, 20, 7], size_hint=(None, None), size=("340dp", "200dp"),
                            title="Карточка пользователя", type="custom",
                            content_cls=DialogUserInfo(name_journal, user_info))
        
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

        journal_id = data_base.get_journal_id(name_journal)
        data_base.del_row(("Data", "Users", "Journals"), journal_id)
        self.journals.pop(self.journals.index(self.root.get_screen(name_journal)))

        card_journal.parent.remove_widget(card_journal)
        journal.parent.remove_widget(journal)

    def get_week_date(self) -> list:
        day_week =int(datetime.datetime.today().strftime("%w"))
        day_mounth = int(datetime.datetime.today().strftime("%d"))
        all_days_today_mounth = _MOUNTH[datetime.datetime.today().strftime("%b")]
        
        if day_week == 0:
            day_week = 7

        if day_week == 1:
            if day_mounth + 7 <= all_days_today_mounth:
                return [str(i) for i in range(day_mounth, day_mounth + (all_days_today_mounth - day_mounth) + 1)]
            elif day_mounth + 7 > all_days_today_mounth:
                days_1 = [str(i) for i in range(day_mounth, day_mounth + (all_days_today_mounth - day_mounth) + 1)]
                days_2 = [str(i) for i in range(1, int((datetime.datetime.today() + datetime.timedelta(days = 7)).strftime("%d")))]
                return days_1 + days_2
        else:
            if day_mounth - day_week >= 0:
                days_1 = [str(i) for i in range((day_mounth - day_week) + 1, day_mounth)]
                days_2 = [str(i) for i in range(day_mounth, day_mounth + (7 - day_week) + 1)]
                return days_1 + days_2
            elif day_mounth - day_week < 0:
                all_days_old_mounth = _MOUNTH[(datetime.datetime.today() - datetime.timedelta(days = abs(day_mounth - day_week))).strftime("%b")]
                days_1 = [str(i) for i in range(int((datetime.datetime.today() - datetime.timedelta(days = day_week)).strftime("%d")) + 1, all_days_old_mounth + 1)]
                days_2 = [str(i) for i in range(1, day_mounth + 1)]
                return days_1 + days_2

    def dialog_journal(self):
        content = SetJournal()
        dialog = MDDialog(radius=[20, 7, 20, 7], title = "Добавить новый журнал", type = "custom", content_cls = content,
                          buttons = [MDFlatButton(text = "Добавить", md_bg_color = _GREEN, theme_text_color = "Custom", text_color = "white", on_release = lambda x: self.set_journal(dialog, content))])
        dialog.open()

    def set_journal(self, other, content):
        name_table = "Journals"
        journal_id = data_base.get_last_journal_id() + 1

        name_journal = content.children[1].text.capitalize()
        description = content.children[0].text.capitalize() or "Добавить комментарий"

        if data_base.search_journal(journal_id - 1, name_journal):
            data_base.set_row(name_table, (journal_id, name_journal, description))
            app.update_journals(name_journal, description)
            other.dismiss(force = True)
        else:
            self.error_create_journal(name_journal)

    def error_create_journal(self, name_journal):
        Snackbar(text = f"Журнал {name_journal} уже существует", font_size = "16dp", height = "100dp").open()

    def dialog_user(self, name_journal):
        content = SetUser()
        dialog = MDDialog(radius=[20, 7, 20, 7], title = "Добавить пользователя", type = "custom", content_cls = content,
                          buttons = [MDFlatButton(text = "Добавить", md_bg_color = _GREEN, theme_text_color = "Custom", text_color = "white", on_release = lambda x: self.set_user(name_journal, dialog, content))])
        dialog.open()

    def set_user(self, name_journal, dialog, content):
        journal_id = data_base.get_journal_id(name_journal)
        user_id = data_base.get_last_user_id() + 1

        user_name_info = [content.children[0].children[i].text.capitalize() for i in range(2, -1, -1)]
        user_info = [content.children[1].children[0].children[i].text.capitalize() for i in range(4, -1, -1)]

        if not os.path.isfile(f"./users_avatar/{name_journal}/test_user.png"):
            with Image.open(f"./Images/user.png") as img:
                b = BytesIO()
                img.save(b, "png")
                b.seek(0)
                byteImg = b.read()
            
        else:
            with Image.open(f"./users_avatar/{name_journal}/test_user.png") as img:
                b = BytesIO()
                img.save(b, "png")
                b.seek(0)
                byteImg = b.read()
            os.remove(f"./users_avatar/{name_journal}/test_user.png")

        result = user_name_info + user_info
        result.append(byteImg)
        result.insert(0, journal_id)
        result.insert(0, user_id)

        data_base.set_row(name_table="Users", data=result)
        
        session_log = json.dumps([{datetime.datetime.today().strftime("%Y %b"):{datetime.datetime.today().strftime("%d"): 2}}])
        data_base.set_row(name_table="Data", data=[data_base.get_last_data_id() + 1, user_id, journal_id, session_log])
        app.update_users(name_journal, result, data=session_log)
        dialog.dismiss(force = True)


if __name__ == "__main__":
    app = SessionLog()
    app.run()
