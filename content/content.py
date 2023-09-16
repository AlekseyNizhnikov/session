from kivymd.uix.floatlayout import MDFloatLayout
from kivymd.uix.label import MDLabel
import os
from PIL import Image
from io import BytesIO
from kivymd.uix.dialog import MDDialog
from kivymd.uix.fitimage import FitImage
from kivymd.uix.gridlayout import MDGridLayout
from settings import _GREEN

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
            

class SettingsBox(MDFloatLayout):
    pass


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

        