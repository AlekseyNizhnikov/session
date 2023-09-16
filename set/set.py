from kivymd.uix.textfield import MDTextField
from kivymd.uix.floatlayout import MDFloatLayout
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.card import MDCard
from kivymd.uix.fitimage import FitImage
from kivymd.uix.gridlayout import MDGridLayout
from kivymd.uix.label import MDLabel
from kivymd.uix.selectioncontrol import MDSwitch
from settings import _GREEN


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


class SetEvent(MDFloatLayout):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.size_hint = (None, None)
        self.size = ("100dp", "350dp")
        all_box = MDGridLayout(cols = 1, rows = 12, spacing = "4dp", padding = "4dp", pos_hint = {"center_x": 0.5, "center_y": 0.5})
        all_box.add_widget(MDBoxLayout(MDLabel(text = "Сдача зачетов:", bold = True), MDSwitch(active = True, icon_active = "check", icon_active_color = "white", pos_hint = {"center_y": .5}, thumb_color_active = _GREEN, track_color_active = (0.11, 0.49, 0.27, 0.7)),
                                         pos_hint = {"center_x": 0.49, "center_y": 0.5}, size_hint_x = None, width = "200dp"))
        all_box.add_widget(MDBoxLayout(MDLabel(text = "Уведомление:", bold = True), MDSwitch(active = True, icon_active = "check", icon_active_color = "white", pos_hint = {"center_y": .5}, thumb_color_active = _GREEN, track_color_active = (0.11, 0.49, 0.27, 0.7)),
                                         pos_hint = {"center_x": 0.49, "center_y": 0.2}, size_hint_x = None, width = "200dp"))
        self.add_widget(all_box)