from kivymd.uix.textfield import MDTextField
from kivymd.uix.floatlayout import MDFloatLayout
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.card import MDCard
from kivymd.uix.fitimage import FitImage
from kivymd.uix.gridlayout import MDGridLayout
from kivymd.uix.label import MDLabel
from kivymd.uix.selectioncontrol import MDSwitch
from kivymd.uix.button import MDIconButton
from kivymd.uix.behaviors import TouchBehavior
from kivymd.uix.button import MDFlatButton, MDRectangleFlatIconButton
from kivymd.uix.scrollview import MDScrollView

from PIL import Image
from io import BytesIO
import os
import json
import datetime

from configurate.colors import _GREEN, _RED, _GRAY
from configurate.journal import _HELPER_TEXT_JOURNAL
from configurate.user import _HELPER_TEXT_USER, _HELPER_TEXT_USER_INFO
from content.about import _ABOUT_TEXT
from content.contacts import _CONTACTS

from controller.database import DataBase
database = DataBase()

from kivy.metrics import dp
from kivy.animation import Animation


class CustomTextField(MDTextField):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.font_size = "14sp"
        self.text_color_focus = _GREEN
        self.icon_left_color_focus = _GREEN
        self.icon_right_color_focus = _GREEN
        self.line_color_focus = _GREEN
        self.hint_text_color_focus = _GREEN
        self.helper_text_mode = "persistent"
        

class SetJournal(MDFloatLayout):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.size_hint = (None, None)
        self.size = ("100dp", "100dp")

        for i, helper_text in zip(range(len(_HELPER_TEXT_JOURNAL)), _HELPER_TEXT_JOURNAL):
            self.add_widget(CustomTextField(helper_text=helper_text, pos_hint={"center_x": 1.15, "center_y": 0.9 - (i * 0.5)}, size_hint_x = None, width = "240dp"))


class GenderBox(MDFloatLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.size_hint = (None, None)
        self.size = ("240dp", "20dp")

        woman = MDLabel(text = "Пол:     [color=#a5a5a5][b]Ж[/b][/color]", font_size = "14sp", markup = True, text_color = (0.8, 0.8, 0.8, 0.5), halign = "center", pos_hint = {"center_x": 0.5, "center_y": 0.5})
        man = MDLabel(text = "[color=#a5a5a5]М[/color]", font_size = "14sp", bold = True, markup = True, halign = "center", pos_hint = {"center_x": 0.97, "center_y": 0.5})
        
        self.add_widget(woman)
        self.add_widget(GenderSwitch(woman, man))
        self.add_widget(man)
        

class GenderSwitch(MDSwitch):
    def __init__(self, woman, man, **kwargs):
        super().__init__(**kwargs)
        self.woman = woman
        self.man = man
        self.active = True
        self.icon_active = "check"
        self.icon_active_color = "white"
        self.pos_hint = {"center_x": 0.75, "center_y": 0.5}
        self.thumb_color_active = _GREEN
        self.track_color_active = (0.11, 0.49, 0.27, 0.7)       

    def on_active(self, instance_switch, active_value: bool) -> None:
        self.check_three_switch(active_value)

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

    def check_three_switch(self, active_value):
        if active_value:
            self.man.text = "[color=#000000][b]М[/b][/color]"
            self.woman.text = "Пол:     [color=#a5a5a5][b]Ж[/b][/color]"
        else:
            self.man.text = "[color=#a5a5a5][b]М[/b][/color]"
            self.woman.text = "Пол:     [color=#000000][b]Ж[/b][/color]"


class SetUser(MDFloatLayout):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.size_hint = (None, None)
        self.size = ("100dp", "350dp")

        name_box = MDFloatLayout(GenderBox(), pos_hint={"center_x": 1.4, "center_y": 0.0})
        for i, helper_text in zip(range(len(_HELPER_TEXT_USER)), _HELPER_TEXT_USER):
            name_box.add_widget(CustomTextField(helper_text=helper_text, pos_hint={"center_x": 0.3, "center_y": 0.8 - (i * 0.12)}, size_hint_x = None, width = "240dp"),)
        
        top_box = MDBoxLayout(MDCard(FitImage(source="./assets/images/user.png", size_hint_x=None, size_hint_y=None, height="195dp", width="130dp"),
                                      size_hint_x=None, size_hint_y=None, height="195dp", width="130dp", pos_hint={"center_x": 0.5, "center_y": 0.1}, md_bg_color=_GREEN),
                                orientation="horizontal", size_hint_y=None, height="200dp", pos_hint={"center_x": 0.3, "center_y": 0.98}, padding = "4dp", spacing="70dp")
        
        info_box = MDFloatLayout(md_bg_color = (0.3, 0.4, 0.7, 1), size_hint_y=None, height="200dp", pos_hint={"center_x": 0.5, "center_y": 0.2})
        for i, info in zip(range(len(_HELPER_TEXT_USER_INFO)), _HELPER_TEXT_USER_INFO.keys()):
            info_box.add_widget(CustomTextField(helper_text=info, icon_right = _HELPER_TEXT_USER_INFO[info], input_filter = "float", pos_hint={"center_x": 0.5, "center_y": 0.8 - (i * 0.2)}, size_hint_x = None, width = "123dp"))
        
        top_box.add_widget(info_box)
        self.add_widget(top_box)
        self.add_widget(name_box)
     

class CustomLogUser(MDBoxLayout):
    def __init__(self, session_log, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.orientation = "vertical"
        self.spacing = "8dp"
        self.size_hint = (None, None)
        self.size = ("300dp", "220dp")

        session_log = json.loads(session_log)

        box_0 = MDBoxLayout(size_hint = (None, None), size = ("300dp", "50dp"), md_bg_color = _GREEN)
        box_0.add_widget(MDLabel(text = "История посещений", halign = "center", theme_text_color = "Custom", text_color = "white"))

        box = MDGridLayout(cols = 7, spacing = "4dp", size_hint = (None, None), size = ("230dp", "160dp"), pos_hint={"center_x": 0.5})
        for day in ["Пн", "Вт", "Ср", "Чт", "Пт", "Сб", "Вс"]:
            box.add_widget(MDLabel(text = day, bold = True, halign = "center", font_style = "Caption"))

        for i in range(1, 32):
            card = MDCard(elevation=1, ripple_behavior=True, md_bg_color=_GRAY, size_hint=(None, None), size=("23dp", "23dp"))
            card.add_widget(MDLabel(text = str(i), halign = "center", font_style = "Caption"))
            data_today = datetime.datetime.today().strftime("%Y %b")
            day_today = str(i)
            if int(day_today) < 10:
                day_today = "0" + day_today

            if data_today in session_log[0] and day_today in session_log[0].get(data_today):
                if session_log[0].get(data_today).get(day_today) == 1:
                    card.md_bg_color = _GREEN
                elif session_log[0].get(data_today).get(day_today) == 0:
                    card.md_bg_color = (0.44, 0.16, 0.16, 1)

            box.add_widget(card)

        self.add_widget(box_0)
        self.add_widget(box)


class SetUserCard(MDBoxLayout):
    def __init__(self, data, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.size_hint = (None, None)
        self.size = ("300dp", "720dp")
        self.orientation = "vertical"
        self.spacing = "4dp"
        self.pos_hint={"center_x":0.50}
        
        session_log = database.cursor.execute(f"SELECT session_log FROM Data WHERE user_id = '{data[0]}' AND journal_id = '{data[1]}'").fetchone()[0]

        gb = GenderBox()
        if data[-2] == "False":
            gb.children[1].active = False
        else:
            gb.children[1].active = True

        name_box = MDBoxLayout(size_hint = (None, None), size = ("300dp", "200dp"), orientation = "vertical", padding = ("30dp", "30dp", "30dp", "30dp"), spacing = "-12dp")
        name_box.add_widget(gb)
        for i, helper_text, dt in zip(range(len(_HELPER_TEXT_USER)), _HELPER_TEXT_USER, data[2:5]):
            name_box.add_widget(CustomTextField(text = str(dt), helper_text=helper_text, size_hint_x = None, width = "240dp"),)
        
        top_box = MDBoxLayout(MDCard(FitImage(source="./assets/images/user.png", size_hint_x=None, size_hint_y=None, height="195dp", width="130dp"),
                                      size_hint_x=None, size_hint_y=None, height="195dp", width="130dp", pos_hint={"center_x": 0.5, "center_y": 0.5}, md_bg_color=_GREEN),
                                orientation="horizontal", size_hint=(None, None), size=("300dp", "250dp"), padding = "15dp", spacing="10dp")
        
        info_box = MDBoxLayout(orientation = "vertical", spacing = "-15dp", size_hint=(None, None), size=("200dp", "250dp"))
        for i, info, dt in zip(range(len(_HELPER_TEXT_USER_INFO)), _HELPER_TEXT_USER_INFO.keys(), data[5:]):
            info_box.add_widget(CustomTextField(text=str(dt), helper_text=info, icon_right = _HELPER_TEXT_USER_INFO[info], input_filter = "float", size_hint_x = None, width = "123dp"))
        
        top_box.add_widget(info_box)
        self.add_widget(top_box)
        self.add_widget(name_box)
        self.add_widget(CustomLogUser(session_log))
        self.add_widget(MDBoxLayout(size_hint = (None, None), size = ("300dp", "20dp")))


class CustomThreeMDSwitch(MDSwitch):
    def __init__(self, period, not_period, text_period, **kwargs):
        super().__init__(**kwargs)
        self.icon_active = "check"
        self.icon_active_color = "white"
        self.thumb_color_active = _GREEN
        self.track_color_active = (0.11, 0.49, 0.27, 0.7)
        self.period = period
        self.not_period = not_period
        self.text_period = text_period

    def on_active(self, instance_switch, active_value: bool) -> None:
        if active_value == True:
            self.period.text_color = _GRAY
            self.not_period.text_color = _GREEN
            self.text_period.disabled = True
        else:
            self.period.text_color = _GREEN
            self.not_period.text_color = _GRAY
            self.text_period.disabled = False

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
    def __init__(self, passing_tests, notification, tests, **kwargs):
        super().__init__(**kwargs)
        self.icon_active = "check"
        self.icon_active_color = "white"
        self.thumb_color_active = _GREEN
        self.track_color_active = (0.11, 0.49, 0.27, 0.7)
        self.passing_tests = passing_tests
        self.notification = notification
        self.tests = tests

    def on_active(self, instance_switch, active_value: bool) -> None:
        if active_value == True:
            self.passing_tests.text_color = _GRAY
            self.notification.text_color = _GREEN
            for test in self.tests:
                test.disabled = True
        else:
            self.passing_tests.text_color = _GREEN
            self.notification.text_color = _GRAY
            for test in self.tests:
                test.disabled = False

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


# class ReleaseEvent()


class SetEvent(MDScrollView):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.size_hint_y = None
        self.height = "350dp"

        top_box = MDBoxLayout(size_hint = (None, None), size = ("270dp", "610dp"), orientation = "vertical", spacing = "-15dp")

        period = MDLabel(text = "Регулярно", bold = True, theme_text_color = "Custom", text_color = _GRAY, font_style = "Body2", pos_hint = {"center_y": 0.5})
        not_peripd = MDLabel(text = "                 Один раз", bold = True, theme_text_color = "Custom", text_color = _GRAY, font_style = "Body2", pos_hint = {"center_y": 0.5})
        text_period = CustomTextField(text = "30", helper_text="Укажите периодичность события в днях...", size_hint_x = None, width = "270dp", input_filter = "int")
        
        top_box.add_widget(MDBoxLayout(period, CustomThreeMDSwitch(period, not_peripd, text_period, pos_hint = {"center_y": 0.5}),
                                       not_peripd, size_hint = (None, None), size = ("270dp", "20dp"), spacing = "0dp", padding = ("0dp", "0dp", "0dp", "60dp")))
        

        passing_tests = MDLabel(text = "Сдача зачетов", bold = True, theme_text_color = "Custom", text_color = _GRAY, font_style = "Body2", pos_hint = {"center_y": 0.5})
        notification = MDLabel(text = "       Уведомление", bold = True, theme_text_color = "Custom", text_color = _GREEN, font_style = "Body2", pos_hint = {"center_y": 0.5})
        tests = []
        for _ in range(1, 10):
            tests.append(CustomTextField(helper_text="Введите задание...", size_hint_x = None, width = "270dp"))

        top_box.add_widget(MDBoxLayout(passing_tests, CustomTwoMDSwitch(passing_tests, notification, tests, pos_hint = {"center_y": 0.5}),
                                       notification, size_hint = (None, None), size = ("270dp", "20dp"), spacing = "0dp", padding = ("0dp", "40dp", "0dp", "40dp")))
        
        top_box.add_widget(text_period)
        top_box.add_widget(CustomTextField(text = datetime.datetime.today().strftime("%d.%m.%Y"), helper_text="Введите дату события...", size_hint_x = None, width = "270dp"))
        top_box.add_widget(CustomTextField(helper_text="Введите текст события...", size_hint_x = None, width = "270dp"))
        
        for test in tests:
            top_box.add_widget(test)

        self.add_widget(top_box)


class AboutBox(MDFloatLayout):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.add_widget(MDIconButton(icon = "information-variant", icon_size = "136dp", pos_hint = {"center_x": 0.5, "center_y": 0.85}))
        self.add_widget(MDLabel(text="О приложении", halign="center", font_style="H4", pos_hint={"center_x": 0.5, "center_y": 0.72}))
        self.add_widget(MDLabel(text=_ABOUT_TEXT, font_size = "12sp", padding=12, pos_hint={"center_x": 0.5, "center_y": 0.45}))


class ContactsBox(MDFloatLayout):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        label = MDLabel(text="АВТОРЫ", bold = True, halign="center", pos_hint={"center_x": 0.5, "center_y": 0.97})
        label.font_size = "14sp"
        self.add_widget(label)
        label = MDLabel(text=f"[b]Разработчик:[/b] {_CONTACTS['Разработчик']}", markup = True, halign="left", pos_hint={"center_x": 0.52, "center_y": 0.93})
        label.font_size = "14sp"
        self.add_widget(label)
        label = MDLabel(text=f"[b]Дизайнер:[/b] {_CONTACTS['Дизайнер']}", markup = True, halign="left", pos_hint={"center_x": 0.52, "center_y": 0.89})
        label.font_size = "14sp"
        self.add_widget(label)
        self.add_widget(MDFloatLayout(size_hint_y = None, height = "2dp", md_bg_color = _GREEN, pos_hint = {"center_x": 0.5, "center_y": 0.85}))

        label = MDLabel(text="КОНТАКТЫ", bold = True, halign="center", pos_hint={"center_x": 0.5, "center_y": 0.81})
        label.font_size = "14sp"
        self.add_widget(label)

        label = MDLabel(text=f"[b]Почта:[/b] {_CONTACTS['Почта']}", markup = True, halign="left", pos_hint={"center_x": 0.52, "center_y": 0.77})
        label.font_size = "14sp"
        self.add_widget(label)
        label = MDLabel(text=f"[b]Телефон:[/b] {_CONTACTS['Телефон']}", markup = True, halign="left", pos_hint={"center_x": 0.52, "center_y": 0.73})
        label.font_size = "14sp"
        self.add_widget(label)
        self.add_widget(MDFloatLayout(size_hint_y = None, height = "2dp", md_bg_color = _GREEN, pos_hint = {"center_x": 0.5, "center_y": 0.69}))

        label = MDLabel(text="ОРГАНИЗАЦИЯ", bold = True, halign="center", pos_hint={"center_x": 0.5, "center_y": 0.65})
        label.font_size = "14sp"
        self.add_widget(label)

        label = MDLabel(text=f"[b]Организация:[/b] {_CONTACTS['Организация']}", markup = True, halign="left", pos_hint={"center_x": 0.52, "center_y": 0.61})
        label.font_size = "14sp"
        self.add_widget(label)
        label = MDLabel(text=f"[b]Адрес:[/b] {_CONTACTS['Адрес']}", markup = True, halign="left", pos_hint={"center_x": 0.52, "center_y": 0.57})
        label.font_size = "14sp"
        self.add_widget(label)
        self.add_widget(MDFloatLayout(size_hint_y = None, height = "2dp", md_bg_color = _GREEN, pos_hint = {"center_x": 0.5, "center_y": 0.53}))
            

class SettingsBox(MDFloatLayout):
    pass


class DialogUserInfo(MDFloatLayout):
    def __init__(self, name_journal, user_info, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.size_hint = (None, None)
        self.size = ("100dp", "200dp")

        user_id, journal_id, second_name, first_name, father_name, weight, height, age, phone, gender, birthday, img = user_info
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
