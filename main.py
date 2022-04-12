import os
import sys
import excel_functions as ex
from kivy.resources import resource_add_path, resource_find
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.storage.jsonstore import JsonStore
from kivy.core.window import Window
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
    def __init__(self, **kwargs):
        super(HandleLayout, self).__init__(**kwargs)
        self.store = JsonStore('settings.json')
        self.table = None
        self.title = None
        self.del_table = None
        self.update_table = None

    def handle_press_step_button(self, text):
        if text == 'Шаг 1':
            file_path = self.store.get('file_path')['path']
            self.console.text = 'Файл найден.\n'
            self.console.text += f'Обрабатывается файл : {str(file_path)} \n'
            self.table, self.title = ex.get_worksheet(file_path)
            self.step_button.text = 'Шаг 2'

        elif text == 'Шаг 2':
            color = self.store.get('cell_color')['value']
            self.console.text += f'Выбран цвет выделенных ячеек: {color} \n'
            m_table, m_row = ex.get_table(self.table, 2, 10)
            update_table, _ = ex.get_table(self.table, m_row, 10)
            self.del_table, table_norm, table_err = ex.separate_table(m_table, color)
            start_id = max(m_table, key=lambda x: x[0].value)[0].value
            update_table = ex.set_value(update_table, 0, start_id, True)
            self.update_table = ex.set_value(update_table, 9, '#новые поступления#', False)
            self.step_button.text = 'Шаг 3'

        elif text == 'Шаг 3':
            images_path = self.store.get('images_path')['path']
            self.console.text += f'Выбран путь к папке с фотографиями: {images_path} \n'
            response, flag = ex.check_images(images_path, self.update_table)
            self.console.text += response
            if flag:
                self.step_button.text = 'Шаг 4'

        elif text == 'Шаг 4':
            folder_path = self.store.get('save_dir_path')['path']
            response = ex.get_file_from_table(folder_path, 'update', self.update_table, self.title)
            self.console.text += response
            response = ex.get_file_from_table(folder_path, 'del', self.del_table, self.title)
            self.console.text += response
            self.console.text += f'Обработка файла успешно завершена.\n'
            self.console.text += f'Можно переходить к загрузки данных на сервер.\n'
            self.step_button.text = 'Шаг 1'

class UploadLayout(GridLayout):
    pass

class NewScreenManager(ScreenManager):
    pass

class Container(FloatLayout):
    def __init__(self, **kwargs):
        super(Container, self).__init__(**kwargs)
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

class ContainerApp(App):

    def build(self):
        return Container()


if __name__ == '__main__':
    if hasattr(sys, '_MEIPASS'):
        resource_add_path(os.path.join(sys._MEIPASS))
    Window.size = (700, 700)
    ContainerApp().run()
