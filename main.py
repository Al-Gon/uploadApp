import os
import sys
from kivy.resources import resource_add_path, resource_find
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.anchorlayout import AnchorLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.storage.jsonstore import JsonStore
from kivy.core.window import Window

import excel_functions as ex
from kivy.app import App
from kivy.properties import ObjectProperty, StringProperty

class ScreenTemplate(Screen):
    pass

class SettingLayout(FloatLayout):
    def __init__(self, **kwargs):
        super(SettingLayout, self).__init__(**kwargs)
        self.store = JsonStore('settings.json')
        if len(self.store.get('save_dir_path')['path']):
            self.save_dir_path.text = self.store.get('save_dir_path')['path']
        if len(self.store.get('file_path')['path']):
            self.file_path.text = self.store.get('file_path')['path']
        if len(self.store.get('images_path')['path']):
            self.images_path.text = self.store.get('images_path')['path']
        if len(self.store.get('cell_color')['value']):
            self.cell_color.text = self.store.get('cell_color')['value']

    def handle_path(self, name):
        if name == 'save_dir_path_button':
            if ex.check_folder_path(self.save_dir_path.text):
                self.store.put('save_dir_path', path=self.save_dir_path.text)
                self.console.text = 'Путь к папке успешно сохранен в настройках.'
            else:
                self.save_dir_path.text = 'Введите путь к папке для хранения файлов'
                self.console.text = 'Путь к папке указан не верно.'
        if name == 'file_path_button':
            if ex.check_file_path(self.file_path.text):
                self.store.put('file_path', path=self.file_path.text)
                self.console.text = 'Путь к файлу успешно сохранен в настройках.'
            else:
                self.file_path.text = 'Введите путь к файлу xlsx'
                self.console.text = 'Путь к файлу указан не верно.'
        if name == 'images_path_button':
            if ex.check_folder_path(self.images_path.text):
                self.store.put('images_path', path=self.images_path.text)
                self.console.text = 'Путь к папке успешно сохранен в настройках.'
            else:
                self.images_path.text = 'Введите путь к папке с фото'
                self.console.text = 'Путь к папке указан не верно либо в ней фотографий'
        if name == 'cell_color_button':
            self.store.put('cell_color', value=self.cell_color.text)
            self.console.text = 'Значение цвета успешно сохранено в настройках.'



class HandleLayout(GridLayout):
    pass

class UploadLayout(GridLayout):
    pass

class NewScreenManager(ScreenManager):
    pass


class Container(FloatLayout):
    def __init__(self, **kwargs):
        super(Container, self).__init__(**kwargs)
        self.table = None
        self.title = None
        self.del_table = None
        self.update_table = None

        self.settings_screen = ScreenTemplate(name='screen1')
        self.settings_screen.text_label.text = '[size=18]Настройки[/size]'
        self.settings_screen.main_screen.add_widget(SettingLayout())

        self.handle_screen = ScreenTemplate(name='screen2')
        self.handle_screen.text_label.text = '[size=18]Обработка[/size]'
        self.handle_screen.main_screen.add_widget(HandleLayout())
        self.upload_screen = ScreenTemplate(name='screen3')
        self.upload_screen.text_label.text = '[size=18]Выгрузка[/size]'

        self.upload_screen.main_screen.add_widget(UploadLayout())

        self._screen_manager.add_widget(self.settings_screen)
        self._screen_manager.add_widget(self.handle_screen)
        self._screen_manager.add_widget(self.upload_screen)


    # def handle_press(self):
    #     if self.step_button.text == 'Шаг 1':
    #         if ex.check_path(str(self.file_path.text).strip()):
    #             self.massage.text = 'Файл найден.'
    #             self.step_info.text = f'Обрабатывается файл : {str(self.file_path.text).strip()} \n'
    #             self.table, self.title = ex.get_worksheet(str(self.file_path.text).strip())
    #             if self.table is not None:
    #                 self.file_path.text = 'Выберите цвет шрифта выделенных ячеек: \n'
    #                 self.file_path.text += ' '.join([color for color in ex.search_cell_font_colors(self.table)])
    #             else:
    #                 self.file_path.text = 'Что-то пошло не так'
    #             self.step_button.text = 'Шаг 2'
    #         else:
    #             self.massage.text = 'Не верен путь или имя файла.'
    #     elif self.step_button.text == 'Шаг 2':
    #         color = str(self.file_path.text).strip()
    #         self.massage.text = 'Выбран цвет выделенных ячеек.'
    #         self.step_info.text += f'Выбран цвет выделенных ячеек: {color} \n'
    #         m_table, m_row = ex.get_table(self.table, 2, 10)
    #         update_table, _ = ex.get_table(self.table, m_row, 10)
    #         self.del_table, table_norm, table_err = ex.separate_table(m_table, color)
    #         start_id = max(m_table, key=lambda x: x[0].value)[0].value
    #         update_table = ex.set_value(update_table, 0, start_id, True)
    #         self.update_table = ex.set_value(update_table, 9, '#новые поступления#', False)
    #         self.file_path.text = 'Ведите путь к папке с фотографиями.'
    #         self.step_button.text = 'Шаг 3'
    #     elif self.step_button.text == 'Шаг 3':
    #         path = str(self.file_path.text).strip()
    #         self.step_info.text += f'Выбран путь к папке с фотографиями: {path} \n'
    #         ex.check_images(path, self.update_table)
    #         self.step_button.text = 'Шаг 4'


class ContainerApp(App):

    def build(self):
        return Container()


if __name__ == '__main__':
    if hasattr(sys, '_MEIPASS'):
        resource_add_path(os.path.join(sys._MEIPASS))
    Window.size = (700, 700)
    ContainerApp().run()
