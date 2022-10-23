import os
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.label import Label
from kivy.uix.scrollview import ScrollView
from kivy.properties import StringProperty
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.lang import Builder
from base_classes.config import Config
from modules import excel_functions as ex, parser_functions as pr, request_functions as rq

Builder.load_file('base_classes/kv/base_widgets.kv')

class ButtonGetColors(FloatLayout):
    button_text = StringProperty('')
    pass

class ButtonSaveColor(FloatLayout):
    pass

class ItemLabel(Label):
    message = StringProperty('')

class ScrollLabel(ScrollView):
    message = StringProperty('')

class ScreenTemplate(Screen):
    pass

class NewScreenManager(ScreenManager):
    pass

class InputBlock(FloatLayout):
    input_string = StringProperty('')
    conf = Config()
    console_message = StringProperty('')

    def save_file_name(self, input_obj: object, field, extension: str):
        file_name = input_obj.text.strip()
        substr = bool(field.count('site'))
        message = f'Введите имя файла (будет преобразованно к "имя_месяц_дата{extension}").'
        if substr:
            message = f'Введите имя файла (будет преобразованно к "имя_сайт_месяц_дата{extension}").'
        if not ex.check_file_name(file_name):
            file_name = ex.make_file_name(file_name, extension, substr)
        if len(file_name):
            self.conf.put(field, file_name)
            input_obj.text = file_name
            self.console_message = f'Имя файла "{file_name}" успешно сохранено в настройках.'
        else:
            input_obj.text = message
            self.console_message = 'Имя файла указано не верно.'

    def handle_path(self, name: str):
        if name == 'save_dir_path_button':
            if ex.check_folder_path(self.input.text):
                self.conf.put('save_dir_path', self.input.text)
                self.console_message = 'Путь к папке успешно сохранен в настройках.'
            else:
                self.input.text = 'Введите путь к папке для хранения файлов'
                self.console_message = 'Путь к папке указан не верно.'

        if name == 'db_file_name_button':
            self.save_file_name(self.input, 'db_file_name', '.db')

        if name == 'file_name_button':
            self.save_file_name(self.input, 'file_name', '.xlsx')

        if name == 'php_file_path_button':
            php_file_path = self.input.text.strip()
            response = rq.do_request(url=php_file_path)
            if response is not None and response.ok:
                self.conf.put('php_file_path', php_file_path)
                self.console_message = 'URL адрес PHP файла успешно сохранён в настройках.'
            else:
                self.input.text = 'Введите путь к папке с фото'
                self.console_message = 'URL адрес PHP файла указан не верно либо он отсутствует.'

        if name == 'images_folder_name_button':
            images_folder_name = self.input.text.strip()
            save_dir_path = self.conf['save_dir_path']
            folder_path = os.path.join(save_dir_path, images_folder_name)
            if ex.check_folder_path(folder_path):
                self.conf.put('images_folder_name', images_folder_name)
                self.console_message = 'Имя папки успешно сохранено в настройках.'
            else:
                self.input.text = 'Введите путь к папке с фото'
                self.console_message = 'Путь к папке указан не верно либо в ней фотографий'

        if name == 'update_file_name_button':
            self.save_file_name(self.input, 'update_file_name', '.xlsx')

        if name == 'del_file_name_button':
            self.save_file_name(self.input, 'del_file_name', '.xlsx')

        if name == 'category_site_file_name_button':
            self.save_file_name(self.input, 'category_site_file_name', '.xlsx')

        if name == 'data_site_file_name_button':
            self.save_file_name(self.input, 'data_site_file_name', '.xlsx')

        if name == 'category_site_urls_button':
            urls_ = self.input.text.split(',')
            urls = [url.strip() for url in urls_ if rq.do_request(url=url.strip()).ok]
            if urls:
                self.conf.put('category_site_urls', urls)
                message = ' ,\n'.join(urls)
                self.console_message = f'Данные url: "{message}" сохранены в настройках.'
            else:
                self.console_message = 'Ни одного url не было сохранено.'
                self.input.text = 'Введите url адреса страниц категорий сайтов (через запятую).'