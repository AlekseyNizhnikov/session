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
from kivymd.uix.filemanager import MDFileManager
from kivymd.uix.selectioncontrol import MDSwitch
from kivymd.uix.snackbar import Snackbar

from kivy.metrics import dp
from kivy.animation import Animation

import datetime
import json
import os
from PIL import Image
from io import BytesIO
import shutil
from kivy.utils import platform

from view.view import SetEvent, SetJournal, SetUser, AboutBox, SettingsBox, ContactsBox, DialogUserInfo, SetUserCard, CustomLogUser
from configurate.config import _MOUNTH, _DAYS, _MOUNTH_DAY, _RUS_DAYS
from configurate.colors import _GREEN, _GRAY, _RED

from controller.database import DataBase

__version__ = '1.0.0'

database = DataBase()

if platform == "android":
    from android.permissions import request_permissions, Permission
    request_permissions([Permission.WRITE_EXTERNAL_STORAGE, Permission.READ_EXTERNAL_STORAGE])
    from android.storage import primary_external_storage_path
    primary_ext_storage = primary_external_storage_path()
else:
    primary_ext_storage = "./"

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

        screen = self.parent.parent.parent
        name_screen = self.parent.parent.parent.name
        main_screen = self.parent.parent.parent.parent

        if name_screen in ("my_journal", "top_title"):
            app.dialog_journal()

        elif name_screen == "log_management":
            new_name_journal = screen.children[0].children[1].children[10].text.capitalize()
            old_name_journal = screen.children[0].children[1].children[10].hint_text

            if new_name_journal in ("", " "):
                new_name_journal = screen.children[0].children[1].children[10].hint_text
                
            description = screen.children[0].children[1].children[9].text.capitalize()
            if description in ("", " "):
                description = screen.children[0].children[1].children[9].hint_text

            configs = dict()
            for i, config in zip(range(8, 2, -1), ("three_day", "two_day", "sorted", "birthday", "money", "visit")):
                configs[config] = screen.children[0].children[1].children[i].children[0].active
            config = json.dumps(configs)
            app.update_journal(new_name_journal, old_name_journal, description, config)
            journal_id = database.get_journal_id(new_name_journal)

            main_screen.get_screen(old_name_journal).name = new_name_journal
            main_screen.get_screen(new_name_journal).children[0].children[1].children[0].clear_widgets()

            if configs["sorted"]:
                users = database.get_all_by_id_sorted(name_table="Users", name_col="journal_id", id=journal_id)
            else:
                users = database.get_all_by_id(name_table="Users", name_col="journal_id", id=journal_id)

            if users != []:
                for item, user in zip(range(1, len(users) + 1), users):
                    user_id = user[0]
                    session_log = database.get_session_log(user_id, journal_id)
                    app.download_users(item, new_name_journal, user, data=session_log, config=configs)

            main_screen.to_return_my_journals(screen)
    
        elif name_screen in ("statistics","settings","contacts","about", "data_base"):
            main_screen.current = "top_title"

        elif name_screen == "list_users":
            name_journal = self.parent.parent.parent.children[0].children[2].title
            app.dialog_card_user(name_journal)

        elif name_screen == "user":
            gender = screen.children[0].children[1].children[0].children[0].children[2].children[3].children[1].active
            lname = screen.children[0].children[1].children[0].children[0].children[2].children[2].text.capitalize()
            fname = screen.children[0].children[1].children[0].children[0].children[2].children[1].text.capitalize()
            faname = screen.children[0].children[1].children[0].children[0].children[2].children[0].text.capitalize()

            weight = screen.children[0].children[1].children[0].children[0].children[3].children[0].children[4].text
            height = screen.children[0].children[1].children[0].children[0].children[3].children[0].children[3].text
            age = screen.children[0].children[1].children[0].children[0].children[3].children[0].children[2].text
            phone = screen.children[0].children[1].children[0].children[0].children[3].children[0].children[1].text
            birthday = screen.children[0].children[1].children[0].children[0].children[3].children[0].children[0].text
            name_journal = self.parent.parent.parent.children[0].children[2].title
            journal_id = main_screen.data[1]
            user_id = main_screen.data[0]
            data = [fname, lname, faname, weight, height, age, phone, birthday, gender]
            database.update_row_user(user_id, journal_id, data)
            main_screen.to_return_user(screen)

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
        app.open_file()

    def fun_1(self, *args):
        path = primary_ext_storage
        self.file_manager = MDFileManager(exit_manager=self.exit_manager,select_path=self.select_path, background_color_toolbar=(0.11, 0.49, 0.27, 1), icon_color=(0.11, 0.49, 0.27, 1), background_color_selection_button=(0.11, 0.49, 0.27, 1))
        self.file_manager.show(path)

    def file_manager_open(self):
        self.file_manager.show(primary_ext_storage)  
        self.manager_open = True

    def select_path(self, path: str):
        self.exit_manager()
        shutil.copyfile('database/Journals.db', f"./{path}/Journals.db")

    def exit_manager(self, *args):
        self.manager_open = False
        self.file_manager.close()


class CustomThreeMDSwitch(MDSwitch):
    def __init__(self, configs, **kwargs):
        super().__init__(**kwargs)
        self.count = 0
        self.active = configs
        self.icon_active = "check"
        self.icon_active_color = "white"
        self.pos_hint = {"center_y": 0.5}
        self.thumb_color_active = _GREEN
        self.track_color_active = (0.11, 0.49, 0.27, 0.7)

    def on_active(self, instance_switch, active_value: bool) -> None:
        if self.count > 0:
            app.check_three_switch()
        self.count += 1
        if self.theme_cls.material_style == "M3" and self.widget_style != "ios":
            size = (
                (
                    (dp(16), dp(16))
                    if not self.icon_inactive
                    else (dp(24), dp(24))
                )
                if not active_value
                else (dp(24), dp(24))
            )
            icon = "blank"
            color = (0, 0, 0, 0)

            if self.icon_active and active_value:
                icon = self.icon_active
                color = (
                    self.icon_active_color
                    if self.icon_active_color
                    else self.theme_cls.text_color
                )
            elif self.icon_inactive and not active_value:
                icon = self.icon_inactive
                color = (
                    self.icon_inactive_color
                    if self.icon_inactive_color
                    else self.theme_cls.text_color
                )

            Animation(size=size, t="out_quad", d=0.2).start(self.ids.thumb)
            Animation(color=color, t="out_quad", d=0.2).start(
                self.ids.thumb.ids.icon
            )
            self.set_icon(self, icon)

        self._update_thumb_pos()


class CustomTwoMDSwitch(MDSwitch):
    def __init__(self, configs, **kwargs):
        super().__init__(**kwargs)
        self.count = 0
        self.active = configs
        self.icon_active = "check"
        self.icon_active_color = "white"
        self.pos_hint = {"center_y": .5}
        self.thumb_color_active = _GREEN
        self.track_color_active = (0.11, 0.49, 0.27, 0.7)

    def on_active(self, instance_switch, active_value: bool) -> None:
        if self.count > 0:
            app.check_two_switch()
        self.count += 1
        if self.theme_cls.material_style == "M3" and self.widget_style != "ios":
            size = (
                (
                    (dp(16), dp(16))
                    if not self.icon_inactive
                    else (dp(24), dp(24))
                )
                if not active_value
                else (dp(24), dp(24))
            )
            icon = "blank"
            color = (0, 0, 0, 0)

            if self.icon_active and active_value:
                icon = self.icon_active
                color = (
                    self.icon_active_color
                    if self.icon_active_color
                    else self.theme_cls.text_color
                )
            elif self.icon_inactive and not active_value:
                icon = self.icon_inactive
                color = (
                    self.icon_inactive_color
                    if self.icon_inactive_color
                    else self.theme_cls.text_color
                )

            Animation(size=size, t="out_quad", d=0.2).start(self.ids.thumb)
            Animation(color=color, t="out_quad", d=0.2).start(
                self.ids.thumb.ids.icon
            )
            self.set_icon(self, icon)

        self._update_thumb_pos()


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
    
    def add_screen(self, title_name, screen_name, name_journal=None, description="", data=None):   
        self.name_journal = name_journal
        self.data = data
        screen = MDScreen(name=screen_name)
        
        top_bar = MDTopAppBar(title=title_name, pos_hint={"top": 1}, md_bg_color=(0.11, 0.49, 0.27, 1))
        down_bar = MDBottomAppBar(CallableDownBar(icon="home", type="bottom", icon_color=(0.11, 0.49, 0.27, 1),
                                                 mode="end", elevation=0),
                                 md_bg_color=(0.11, 0.49, 0.27, 1))
        
        box = MDBoxLayout(orientation="vertical")
        box.add_widget(top_bar)

        if screen_name == "log_management":
            box_1 = MDFloatLayout()
            box_1.add_widget(MDTextField(font_size = "14sp", text_color_focus = _GREEN, icon_left_color_focus = _GREEN, line_color_focus = _GREEN, hint_text_color_focus = _GREEN, hint_text=f"{name_journal}", max_text_length = 30, size_hint_x = None, width = "290dp", pos_hint = {"center_x":0.5, "center_y": 0.95}))
            box_1.add_widget(MDTextField(font_size = "14sp", text_color_focus = _GREEN, icon_left_color_focus = _GREEN, line_color_focus = _GREEN, hint_text_color_focus = _GREEN, hint_text=f"{description}", max_text_length = 50, size_hint_x = None, width = "290dp", pos_hint = {"center_x":0.5, "center_y": 0.88}))
            
            journal_id = database.get_journal_id(name_journal)
            configs = database.get_config_journal(journal_id)

            self.three_week = MDBoxLayout(MDLabel(text = "Трехдневная неделя:", bold = True), CustomThreeMDSwitch(configs["three_day"]),
                                          pos_hint = {"center_x": .49, "center_y": 0.80}, size_hint_x = None, width = "290dp")
            self.two_week = MDBoxLayout(MDLabel(text = "Двухдневная неделя:", bold = True), CustomTwoMDSwitch(configs["two_day"]),
                                         pos_hint = {"center_x": .49, "center_y": 0.73},
                                         size_hint_x = None, width = "290dp")

            box_1.add_widget(self.three_week)
            box_1.add_widget(self.two_week)

            box_1.add_widget(MDBoxLayout(MDLabel(text = "Сортировка списка учеников:", bold = True), MDSwitch(active = configs["sorted"], icon_active = "check", icon_active_color = "white", pos_hint = {"center_y": .5}, thumb_color_active = _GREEN, track_color_active = (0.11, 0.49, 0.27, 0.7)),
                                         pos_hint = {"center_x": .49, "center_y": 0.66},
                                         size_hint_x = None, width = "290dp"))
            box_1.add_widget(MDBoxLayout(MDLabel(text = "Отображать день рождения:", bold = True), MDSwitch(active = configs["birthday"], icon_active = "check", icon_active_color = "white", pos_hint = {"center_y": .5}, thumb_color_active = _GREEN, track_color_active = (0.11, 0.49, 0.27, 0.7)),
                                         pos_hint = {"center_x": .49, "center_y": 0.59},
                                         size_hint_x = None, width = "290dp"))
            box_1.add_widget(MDBoxLayout(MDLabel(text = "Уведомление об оплате:", bold = True), MDSwitch(active = configs["money"], icon_active = "check", icon_active_color = "white", pos_hint = {"center_y": .5}, thumb_color_active = _GREEN, track_color_active = (0.11, 0.49, 0.27, 0.7)),
                                         pos_hint = {"center_x": .49, "center_y": 0.52},
                                         size_hint_x = None, width = "290dp"))
            box_1.add_widget(MDBoxLayout(MDLabel(text = "Уведомление об отсутсвии:", bold = True), MDSwitch(active = configs["visit"], icon_active = "check", icon_active_color = "white", pos_hint = {"center_y": .5}, thumb_color_active = _GREEN, track_color_active = (0.11, 0.49, 0.27, 0.7)),
                                         pos_hint = {"center_x": .49, "center_y": 0.45},
                                         size_hint_x = None, width = "290dp"))


            box_1.add_widget(MDRectangleFlatIconButton(icon = "account", theme_text_color="Custom", _min_width = "300dp", line_color = _GREEN, icon_color = "white", text_color = "white", text = "К списку учеников", pos_hint = {"center_x":0.5, "center_y": 0.35}, md_bg_color = _GREEN, on_release = lambda x: app.view_users(name_journal)))
            box_1.add_widget(MDRectangleFlatIconButton(icon = "calendar", theme_text_color="Custom", _min_width = "300dp", line_color = _GREEN, icon_color = "white", text_color = "white", text = "Добавить событие", pos_hint = {"center_x":0.5, "center_y": 0.25}, md_bg_color = _GREEN, on_release = lambda x: app.set_event()))
            box_1.add_widget(MDRectangleFlatIconButton(icon = "finance", theme_text_color="Custom", _min_width = "300dp", line_color = _GREEN, icon_color = "white", text_color = "white", text = "Статистика", pos_hint = {"center_x":0.5, "center_y": 0.15}, md_bg_color = _GREEN))

            box.add_widget(box_1)
            down_bar.children[1].icon = "content-save-outline"
            down_bar.children[1].left_action_items=[["chevron-double-left", lambda x: self.to_return_my_journals(screen)]]
            down_bar.children[1].title="К журналам..."

        elif screen_name == "statistics":
            # box_2 = MDGridLayout(cols = 2, rows = 8, spacing = "10dp", padding = "10dp", size_hint_y = None, height = "200dp", pos_hint = {"center_x":0.57, "center_y": 0.68})
            # box_2.add_widget(MDLabel(text=f"Кол-во учеников:", size_hint_x = None, width = "180"))
            # box_2.add_widget(MDLabel(text=f"20 чел.", size_hint_x = None, width = "110dp", halign = "right"))
            # box_2.add_widget(MDLabel(text=f"Кол-во девочек: 10", size_hint_x = None, width = "180dp"))
            # box_2.add_widget(MDLabel(text=f"10 чел.", size_hint_x = None, width = "110dp", halign = "right"))
            # box_2.add_widget(MDLabel(text=f"Кол-во мальчиков: 10", size_hint_x = None, width = "180dp"))
            # box_2.add_widget(MDLabel(text=f"10 чел.", size_hint_x = None, width = "110dp", halign = "right"))
            # box_2.add_widget(MDLabel(text=f"Мин. возраст:", size_hint_x = None, width = "180dp"))
            # box_2.add_widget(MDLabel(text=f"6 лет.", size_hint_x = None, width = "110dp", halign = "right"))
            # box_2.add_widget(MDLabel(text=f"Макс.возраст:", size_hint_x = None, width = "180dp"))
            # box_2.add_widget(MDLabel(text=f"12 лет.", size_hint_x = None, width = "110dp", halign = "right"))
            # box_2.add_widget(MDLabel(text=f"Коф. успеваемости:", size_hint_x = None, width = "180dp"))
            # box_2.add_widget(MDLabel(text=f"1.0     ", size_hint_x = None, width = "110dp", halign = "right"))
            # box_2.add_widget(MDLabel(text=f"Коф. посещаемость:", size_hint_x = None, width = "180dp"))
            # box_2.add_widget(MDLabel(text=f"1.0     ", size_hint_x = None, width = "110dp", halign = "right"))
            # box_2.add_widget(MDLabel(text=f"Средний рост:", size_hint_x = None, width = "180dp"))
            # box_2.add_widget(MDLabel(text=f"130.0  ", size_hint_x = None, width = "110dp", halign = "right"))
            # box_1.add_widget(box_2)
            pass

        elif screen_name == "list_users":
            box_1 = MDFloatLayout()
            box_1.add_widget(MDScrollView(MDList(spacing = "8dp"), pos_hint = {"top": 1}))
            box.add_widget(box_1)
            down_bar.children[1].icon="plus"
            down_bar.children[1].left_action_items=[["chevron-double-left", lambda x: self.to_return_log_management(screen)]]
            down_bar.children[1].title="К настройкам..."

        elif screen_name == "user":
            box_1 = MDFloatLayout()
            box_1.add_widget(MDScrollView(SetUserCard(data), size_hint_y = None, height = "600dp", pos_hint={"center_x":0.60, "center_y":0.50}))
            name_journal = database.get_all_by_id(name_table="journals", id = data[1], name_col="journal_id")[0][1]
            top_bar.title = name_journal
            box.add_widget(box_1)
            down_bar.children[1].icon="content-save-outline"
            down_bar.children[1].left_action_items=[["chevron-double-left", lambda x: self.to_return_user(screen)]]
            down_bar.children[1].title="К журналу..."

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

    def to_return_my_journals(self, screen):
        self.remove_widget(screen)
        self.ids.screen_manager.current = "my_journal"
    
    def to_return_log_management(self, screen):
        self.remove_widget(screen)
        self.current = "log_management"

    def to_return_user(self, screen):
        self.remove_widget(screen)
        self.remove_widget(self.get_screen("list_users"))
        name_journal = screen.children[0].children[2].title
        app.view_users(name_journal)
        self.current = "list_users"


class ListJournals(TwoLineIconListItem):
    def __init__(self, name_journal, description, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.name_journal = name_journal
        self.text = name_journal
        self.secondary_text = description
        self._no_ripple_effect = True
        self.pos_hint = {"center_x":0.5, "center_y":0.5}
        self.bg_color = (0.9,0.9,0.9,1)
        self.add_widget(IconLeftWidget(icon="book-open-page-variant-outline"))

    def on_release(self):
        app.open_journal(self.name_journal)

    def update(self, name_journal, description):
        self.name_journal = name_journal
        self.text = name_journal
        self.secondary_text = description


class CardListJournal(MDCardSwipe):
    def __init__(self, name_journal, journal:object, description, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.name_journal = name_journal
        self.description = description
        self.journal = journal
        self.size_hint_y = None
        self.height = "70dp"
        self.type_swipe = "auto"

        self.add_widget(MDCardSwipeLayerBox(IconLeftWidget(icon="delete")))
        self.add_widget(MDCardSwipeFrontBox(TwoLineIconListItem(IconLeftWidget(icon="book-open-page-variant-outline"),
                                                                text=name_journal,
                                                                secondary_text=description,
                                                                _no_ripple_effect=True,
                                                                bg_color=(0.9,0.9,0.9,1),
                                                                on_release = lambda x: self.log_management(name_journal, description))))

    def on_swipe_complete(self):
        app.remove_journal(self, self.journal, self.name_journal)

    def log_management(self, name_journal, description):
        app.root.add_screen(title_name=self.name_journal, screen_name="log_management", name_journal=self.name_journal, description=self.description)
        app.root.current = "log_management"

    def update(self, name_journal, description):
        self.name_journal = name_journal
        self.description = description
        self.children[0].children[0].text = name_journal
        self.children[0].children[0].secondary_text = description


class JournalCard(MDCard, TouchBehavior):
    def on_release(self):
        day_today = str(datetime.datetime.today().strftime("%d")).removeprefix("0")
        if self.children[0].text == day_today:
            name_user, *_ = self.parent.parent.parent.children[0].children[1].children[0].text.split("\n")
            name_journal = self.parent.parent.parent.parent.parent.parent.parent.children[0].children[4].title
            name_user = name_user.replace(" ", "")
            
            journal_id = database.get_journal_id(name_journal)
            user_id = database.cursor.execute(f"SELECT user_id FROM Users WHERE journal_id = '{journal_id}' AND lname = '{name_user[:-3]}'").fetchone()[0]

            session_log = database.get_session_log(user_id, journal_id)
            event_today = session_log[0].get(datetime.datetime.today().strftime("%Y %b"), {datetime.datetime.today().strftime("%d"): 0})

            if self.md_bg_color == _GRAY:
                event_today[datetime.datetime.today().strftime("%d")] = 1
                self.md_bg_color = _GREEN

            elif self.md_bg_color == _GREEN:
                event_today[datetime.datetime.today().strftime("%d")] = 0
                self.md_bg_color = _RED

            else:
                event_today[datetime.datetime.today().strftime("%d")] = 2
                self.md_bg_color = _GRAY

            session_log = json.dumps([{datetime.datetime.today().strftime("%Y %b"):event_today}])
            database.update_row_data(user_id, database.get_journal_id(name_journal), session_log)
        

class CardListUsers(MDCardSwipe):
    def __init__(self, data, user_id, journal_id, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.user_id = user_id
        self.journal_id = journal_id
        self.data = data
        self.size_hint_y = None
        self.height = "70dp"
        self.type_swipe = "auto"

        self.add_widget(MDCardSwipeLayerBox(IconLeftWidget(icon="delete")))
        self.add_widget(MDCardSwipeFrontBox(TwoLineIconListItem(IconLeftWidget(icon="account-school"),
                                                                text=f"{data[3]} {data[2]} {data[4]}",
                                                                secondary_text=f"Вес: {data[5]} Рост: {data[6]} Возраст: {data[7]}",
                                                                _no_ripple_effect=True,
                                                                bg_color=(0.9,0.9,0.9,1),
                                                                on_release = lambda x: self.user(data))))

    def on_swipe_complete(self):
        app.remove_users(self, self.user_id, self.journal_id)

    def user(self, data):
        app.root.add_screen(title_name="Управление пользователем", screen_name="user", data=data)
        app.root.current = "user" 


class SessionLog(MDApp):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.journals = []

    def on_start(self):
        """
        Метод запускает приложение. Инициализирует переменные и формирует интерфейс приложения.
        """
        if platform == "android":
            from android.permissions import request_permissions, Permission
            request_permissions([Permission.WRITE_EXTERNAL_STORAGE, Permission.READ_EXTERNAL_STORAGE])

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

        journals = database.get_all("Journals")

        for journal in journals:
            journal_id, name_journal, description = journal
            config = database.get_config_journal(journal_id)

            self.download_journal(name_journal, description)
            if config["sorted"]:
                users = database.get_all_by_id_sorted(name_table="Users", name_col="journal_id", id=journal_id)
            else:
                users = database.get_all_by_id(name_table="Users", name_col="journal_id", id=journal_id)

            if users != []:
                for item, user in zip(range(1, len(users) + 1), users):
                    user_id = user[0]
                    session_log = database.get_session_log(user_id, journal_id)
                    self.download_users(item, name_journal, user, data=session_log, config=config)

    def download_journal(self, name_journal:str, description:str): 
        """
        Метод принимает на вход словарь журналов, добавляя их на стараницу журналов.
        """

        self.journals.append(self.root.add_screen(name_journal, name_journal))
        journal = ListJournals(name_journal, description)
        self.root.ids.screen_manager.get_screen("top_title").children[0].children[1].children[0].add_widget(journal)

        card_journal = CardListJournal(name_journal, journal, description)
        self.root.ids.screen_manager.get_screen("my_journal").children[0].children[1].children[0].add_widget(card_journal)

    def download_users(self, item:int, name_journal:str, users:list, data=None, config=None):
        """
        Метод добавляет список пользователей в журнале.
        """
        def get_week_date() -> list:
            day_week =int(datetime.datetime.today().strftime("%w"))
            day_mounth = int(datetime.datetime.today().strftime("%d"))
            all_days_today_mounth = _MOUNTH[datetime.datetime.today().strftime("%b")]
            
            if day_week == 0:
                day_week = 7

            if day_week == 1:
                if day_mounth + 7 <= all_days_today_mounth:
                    return [str(i) for i in range(day_mounth, day_mounth + 7)]
                elif day_mounth + 7 > all_days_today_mounth:
                    days_1 = [str(i) for i in range(day_mounth, day_mounth + (all_days_today_mounth - day_mounth) + 1)]
                    days_2 = [str(i) for i in range(1, int((datetime.datetime.today() + datetime.timedelta(days = 7)).strftime("%d")))]
                    return days_1 + days_2
            else:
                if day_mounth - day_week >= 0:
                    days_1 = [str(i) for i in range((day_mounth - day_week) + 1, day_mounth)]
                    days_2 = [str(i) for i in range(day_mounth, day_mounth + (7 - day_week))]
                    days_3 = [str(i) for i in range(1, 8 - (len(days_1) + len(days_2)))]
                    return days_1 + days_2 + days_3
                elif day_mounth - day_week < 0:
                    all_days_old_mounth = _MOUNTH[(datetime.datetime.today() - datetime.timedelta(days = abs(day_mounth - day_week))).strftime("%b")]
                    days_1 = [str(i) for i in range(int((datetime.datetime.today() - datetime.timedelta(days = day_week)).strftime("%d")) + 1, all_days_old_mounth + 1)]
                    days_2 = [str(i) for i in range(1, day_mounth + 1)]
                    return days_1 + days_2
        
        screen = self.root.get_screen(name_journal)
        journals = screen.children[0].children[1].children[0]
        
        box_childrens = MDBoxLayout(MDLabel(text=str(item), pos_hint={"left": 1,"center_y":0.5}, size_hint_x=None, width="15dp", font_style="Caption"),
                                    orientation="horizontal", padding="10dp", spacing="2dp")
        user_labels = MDBoxLayout(MDFlatButton(text=f"{users[3]} {users[2][0]}.{users[4][0]}\n{users[8]}", font_style="Caption", pos_hint={"center_y":0.5}, on_press=lambda x: dialog_user_info(name_journal, users)),
                                   size_hint_x=None, width="115dp")

        week_days = get_week_date()
        number_day_labels = [MDLabel(text=item, halign="center", font_style="Overline") for item in week_days]
        card_days_week = MDGridLayout(pos_hint={"center_y":0.45}, spacing="7dp", padding="4dp", cols=7, rows=3)

        if config["three_day"]:
            x = [0, 2, 4]
        elif config["two_day"]:
            x = [1, 3]

        for day, i in zip(number_day_labels, range(0, 7)):
            card_day = JournalCard(elevation=1, ripple_behavior=True, md_bg_color=_GRAY, size_hint=(None, None), size=("23dp", "23dp"))
            day_today = day.text
            if int(day_today) < 10:
                day_today = "0" + day_today

            data_today = datetime.datetime.today().strftime("%Y %b")
            # result = datetime.datetime.today() + datetime.timedelta(days=int(day_today))
            # result = result.strftime("%Y %b")
            # print(data[0].get(data_today).keys())
            if data_today in data[0] and day_today in data[0].get(data_today):# and :#result in data[0].keys():
                if data[0].get(data_today).get(day_today) == 1:
                    card_day.md_bg_color = _GREEN
                elif data[0].get(data_today).get(day_today) == 0:
                    card_day.md_bg_color = (0.44, 0.16, 0.16, 1)

            if i not in x:
                card_day.add_widget(MDLabel(text=""))
                card_day.md_bg_color = [1, 1, 1, 1]
            else:
                card_day.add_widget(day)
            card_days_week.add_widget(card_day)

        box_childrens.add_widget(user_labels)
        box_childrens.add_widget(card_days_week)
        card_swipe = MDCard(box_childrens, size_hint_y=None, height="60dp")
        journals.add_widget(card_swipe)

        def dialog_user_info(name_journal, user_info):
            """
            Метод выводит диалоговое окно с информацией о пользователе.
            """
            MDDialog(radius=[dp(20), dp(7), dp(20), dp(7)], size_hint=(None, None), size=("340dp", "200dp"), title="Карточка пользователя", type="custom", content_cls=DialogUserInfo(name_journal, user_info)).open()

    def open_journal(self, name_journal):
        """
        Метод создает экран журнала, на котором отображает список пользователей.
        """
        self.root.current = name_journal

    def add_screen(self, new_name_journal, old_name_journal):
        self.journals.pop(self.journals.index(self.root.get_screen(old_name_journal)))
        self.journals.append(self.root.add_screen(new_name_journal, new_name_journal))

    def remove_users(self, card_user, user_id, journal_id):
        """
        Метод удаляет виджет из списка двух экранов.
        :param card_journal: ссылка на карточку с журналом экрана my_journal.
        :param journal: ссылка на журнал с экрана top_title.
        :return:
        """
        
        dialog = MDDialog(radius=[dp(20), dp(7), dp(20), dp(7)], size_hint=(None, None), size=("340dp", "200dp"), title="Вы уверены что хотите удалить пользователя?", buttons=[MDFlatButton(text="Нет", md_bg_color = _GREEN, on_release = lambda x: dont(dialog)),
                                                                                                                                                 MDFlatButton(text="Да", md_bg_color = _GREEN, on_release = lambda x: yeas()),
                                                                                                                                                 ])
        dialog.open()

        def yeas():
            database.del_row_user(user_id, journal_id)
            card_user.parent.remove_widget(card_user)

        def dont(instance):
            card_user.open_progress = 0
            instance.dismiss(force = True)

    def remove_journal(self, card_journal, journal, name_journal):
        """
        Метод удаляет виджет из списка двух экранов.
        :param card_journal: ссылка на карточку с журналом экрана my_journal.
        :param journal: ссылка на журнал с экрана top_title.
        :return:
        """
        
        dialog = MDDialog(radius=[dp(20), dp(7), dp(20), dp(7)], size_hint=(None, None), size=("340dp", "200dp"), title="Вы уверены что хотите удалить журнал?", buttons=[MDFlatButton(text="Нет", md_bg_color = _GREEN, on_release = lambda x: dont(dialog)),
                                                                                                                                                 MDFlatButton(text="Да", md_bg_color = _GREEN, on_release = lambda x: yeas()),
                                                                                                                                                 ])
        dialog.open()

        def yeas():
            journal_id = database.get_journal_id(name_journal)

            database.del_row(("Data", "Users", "Journals"), journal_id)
            self.journals.pop(self.journals.index(self.root.get_screen(name_journal)))

            card_journal.parent.remove_widget(card_journal)
            journal.parent.remove_widget(journal)

        def dont(instance):
            card_journal.open_progress = 0
            instance.dismiss(force = True)

    def dialog_journal(self):
        content = SetJournal()
        dialog = MDDialog(radius=[dp(20), dp(7), dp(20), dp(7)], title = "Добавить новый журнал", type = "custom", content_cls = content,
                          buttons = [MDFlatButton(text = "Добавить", md_bg_color = _GREEN, theme_text_color = "Custom", text_color = "white", on_release = lambda x: set_journal(dialog, content))])
        dialog.open()

        def set_journal(other, content):
            """
            Метод добавляет журнал в базу данных.
            """
            name_table = "Journals"
            journal_id = database.get_last_id("journal_id", "Journals") + 1

            name_journal = content.children[1].text.capitalize()
            description = content.children[0].text.capitalize() or "Добавить комментарий"
            data = json.dumps({"three_day": True, "two_day": False, "sorted": False, "birthday": False, "money": False, "visit": False})
            config = (database.get_last_id("config_id", "ConfigJournals") + 1, journal_id, data)

            if not database.search_journal(journal_id - 1, name_journal): 
                database.set_row(name_table, (journal_id, name_journal, description))
                database.set_row("ConfigJournals", config)
                app.download_journal(name_journal, description)
                other.dismiss(force = True)
            else:
                error_create_journal(name_journal)

        def error_create_journal(name_journal):
            Snackbar(text = f"Журнал {name_journal} уже существует", font_size = "16dp", height = "100dp").open()

    def dialog_user(self, name_journal):
        content = SetUser()
        dialog = MDDialog(radius=[dp(20), dp(7), dp(20), dp(7)], title = "Добавить пользователя", type = "custom", content_cls = content,
                          buttons = [MDFlatButton(text = "Добавить", md_bg_color = _GREEN, theme_text_color = "Custom", text_color = "white", on_release = lambda x: set_user(name_journal, dialog, content))])
        dialog.open()

        def set_user(name_journal, dialog, content):
            journal_id = database.get_journal_id(name_journal)
            user_id = database.get_last_id("user_id", "Users") + 1

            user_name_info = [content.children[0].children[i].text.capitalize() if content.children[0].children[i].text not in ("", " ") else None for i in range(2, -1, -1)]
            user_info = [content.children[1].children[0].children[i].text.capitalize() if content.children[1].children[0].children[i].text not in ("", " ") else None for i in range(4, -1, -1)]
            gender = content.children[0].children[3].children[1].active

            if None in user_name_info or None in user_info:
                Snackbar(text = f"Заполните все поля...", font_size = "16dp", height = "100dp").open()
            else:
                if not os.path.isfile(f"./users_avatar/{name_journal}/test_user.png"):
                    with Image.open(f"./assets/images/user.png") as img:
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
                result.append(gender)
                result.append(byteImg)
                result.insert(0, journal_id)
                result.insert(0, user_id)

                database.set_row(name_table="Users", data=result)
                
                session_log = json.dumps([{datetime.datetime.today().strftime("%Y %b"):{datetime.datetime.today().strftime("%d"): 2}}])
                database.set_row(name_table="Data", data=[database.get_last_id("data_id", "Data") + 1, user_id, journal_id, session_log])

                config = database.get_config_journal(journal_id)
                self.root.get_screen(name_journal).children[0].children[1].children[0].clear_widgets()
                if config["sorted"]:
                    users = database.get_all_by_id_sorted(name_table="Users", name_col="journal_id", id=journal_id)
                else:
                    users = database.get_all_by_id(name_table="Users", name_col="journal_id", id=journal_id)

                if users != []:
                    for item, user in zip(range(1, len(users) + 1), users):
                        user_id = user[0]
                        session_log = database.get_session_log(user_id, journal_id)
                        app.download_users(item, name_journal, user, data=session_log, config=config)
                dialog.dismiss(force = True)

    def dialog_card_user(self, name_journal):
        content = SetUser()
        dialog = MDDialog(radius=[dp(20), dp(7), dp(20), dp(7)], title = "Добавить пользователя", type = "custom", content_cls = content,
                          buttons = [MDFlatButton(text = "Добавить", md_bg_color = _GREEN, theme_text_color = "Custom", text_color = "white", on_release = lambda x: set_user(name_journal, dialog, content))])
        dialog.open()

        def set_user(name_journal, dialog, content):
            journal_id = database.get_journal_id(name_journal)
            user_id = database.get_last_id("user_id", "Users") + 1

            user_name_info = [content.children[0].children[i].text.capitalize() if content.children[0].children[i].text not in ("", " ") else None for i in range(2, -1, -1)]
            user_info = [content.children[1].children[0].children[i].text.capitalize() if content.children[1].children[0].children[i].text not in ("", " ") else None for i in range(4, -1, -1)]
            gender = content.children[0].children[3].children[1].active

            if None in user_name_info or None in user_info:
                Snackbar(text = f"Заполните все поля...", font_size = "16dp", height = "100dp").open()
            else:
                if not os.path.isfile(f"./users_avatar/{name_journal}/test_user.png"):
                    with Image.open(f"./assets/images/user.png") as img:
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
                result.append(gender)
                result.append(byteImg)
                result.insert(0, journal_id)
                result.insert(0, user_id)

                database.set_row(name_table="Users", data=result)
                
                session_log = json.dumps([{datetime.datetime.today().strftime("%Y %b"):{datetime.datetime.today().strftime("%d"): 2}}])
                database.set_row(name_table="Data", data=[database.get_last_id("data_id", "Data") + 1, user_id, journal_id, session_log])

                self.root.get_screen("list_users").children[0].children[1].children[0].children[0].clear_widgets()
                app.update_card_user(name_journal)
                dialog.dismiss(force = True)

    def check_three_switch(self):
        screen = self.root.get_screen("log_management")
        sw_1 = screen.children[0].children[1].children[8].children[0]
        sw_2 = screen.children[0].children[1].children[7].children[0]

        if sw_1.active == True:
            sw_2.active = False
            return
        if sw_1.active == False:
            sw_2.active = True
            return
        
    def check_two_switch(self):
        screen = self.root.get_screen("log_management")
        sw_1 = screen.children[0].children[1].children[8].children[0]
        sw_2 = screen.children[0].children[1].children[7].children[0]

        if sw_2.active == True:
            sw_1.active = False
            return
        if sw_2.active == False:
            sw_1.active = True
            return
        
    def set_event(self):
        content = SetEvent()
        dialog = MDDialog(radius=[dp(20), dp(7), dp(20), dp(7)], title = "Добавить событие", type = "custom", content_cls = content,
                          buttons = [MDFlatButton(text = "Добавить", md_bg_color = _GREEN, theme_text_color = "Custom", text_color = "white", on_release = lambda x: self.set_user(name_journal, dialog, content))])
        dialog.open()

    def on_save_event(self, instance, value, date_range):
        print(instance, value, date_range)

    def update_journal(self, new_name_journal, old_name_journal, description, config=None):
        journal_id = database.get_journal_id(old_name_journal)

        database.update_row_journals(journal_id, new_name_journal, description)
        database.update_row_config(journal_id, config)

        journals = self.root.ids.screen_manager.get_screen("top_title").children[0].children[1].children[0].children
        card_journals = self.root.ids.screen_manager.get_screen("my_journal").children[0].children[1].children[0].children

        for journal, card_journal in zip(journals, card_journals):
            if journal.name_journal == old_name_journal:
                journal.update(new_name_journal, description) 
            if card_journal.name_journal == old_name_journal:
                card_journal.update(new_name_journal, description) 

    def view_users(self, name_journal):
        self.root.add_screen(name_journal, "list_users")
        self.root.current = "list_users"
        app.update_card_user(name_journal)

    def update_card_user(self, name_journal):
        journal_id = database.get_journal_id(name_journal=name_journal)
        users = database.get_all_by_id(name_table="Users", name_col="journal_id", id=journal_id)
        for user in users:
            user_id, journal_id, *data = user

            card_journal = CardListUsers(user, user_id, journal_id)
            self.root.get_screen("list_users").children[0].children[1].children[0].children[0].add_widget(card_journal)


if __name__ == "__main__":
    app = SessionLog()
    app.run()
