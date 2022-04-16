import os
import sys
import excel_functions as ex
import sql_functions as sql
from kivy.resources import resource_add_path, resource_find
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.storage.jsonstore import JsonStore
from kivy.core.window import Window
from kivy.app import App
from kivy.properties import ObjectProperty, StringProperty

class ScreenTemplate(Screen):
    pass

class SettingLayout(FloatLayout):
    pass

class LoadLayout(BoxLayout):
    pass

class HandleLayout(GridLayout):
    pass

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

        self.load_screen = ScreenTemplate(name='screen2')
        self.load_screen.text_label.text = '[size=18]Загрузка[/size]'
        self.load_screen.main_screen.add_widget(LoadLayout())

        self.handle_screen = ScreenTemplate(name='screen3')
        self.handle_screen.text_label.text = '[size=18]Обработка[/size]'
        self.handle_screen.main_screen.add_widget(HandleLayout())

        self.upload_screen = ScreenTemplate(name='screen4')
        self.upload_screen.text_label.text = '[size=18]Выгрузка[/size]'
        self.upload_screen.main_screen.add_widget(UploadLayout())

        self._screen_manager.add_widget(self.settings_screen)
        self._screen_manager.add_widget(self.load_screen)
        self._screen_manager.add_widget(self.handle_screen)
        self._screen_manager.add_widget(self.upload_screen)

        self.store = JsonStore('settings.json')
        self.table = None
        self.title = None
        self.del_table = None
        self.update_table = None
        self.columns = None
        self.settings_widget = self.settings_screen.main_screen.children[0]
        self.load_widget = self.load_screen.main_screen.children[0]
        self.handle_widget = self.handle_screen.main_screen.children[0]

        if len(self.store.get('save_dir_path')['path']):
            self.settings_widget.save_dir_path.input.text = self.store.get('save_dir_path')['path']
        if len(self.store.get('file_name')['path']):
            self.settings_widget.file_name.input.text = self.store.get('file_name')['path']
        if len(self.store.get('images_path')['path']):
            self.settings_widget.images_path.input.text = self.store.get('images_path')['path']
        if len(self.store.get('cell_color')['value']):
            self.settings_widget.cell_color.input.text = self.store.get('cell_color')['value']
        if len(self.store.get('columns')['names']):
            self.columns = self.store.get('columns')['names']
            self.load_widget.console.text = 'Колонки и представления для выгрузки в файл:\n'
            self.load_widget.console.text += '\n'.join([f'{i}. {col[0]} "{col[1]}"' for i, col in enumerate(self.columns)])
            self.load_widget.console.text += '\nЕсли нужно выгрузить данные из данных колонок в файл нажмите "Шаг 4".'
            self.load_widget.console.text += '\nЕсли нужно изменить колонки нажмите "Шаг 1" и выполните шаги с 1 по 3.'

    def handle_path(self, name: str):
        if name == 'save_dir_path_button':
            if ex.check_folder_path(self.settings_widget.save_dir_path.input.text):
                self.store.put('save_dir_path', path=self.settings_widget.save_dir_path.input.text)
                self.settings_widget.console.text = 'Путь к папке успешно сохранен в настройках.'
            else:
                self.settings_widget.save_dir_path.input.text = 'Введите путь к папке для хранения файлов'
                self.settings_widget.console.text = 'Путь к папке указан не верно.'
        if name == 'file_name_button':
            file_name = self.settings_widget.file_name.input.text.strip()
            if len(file_name):
                self.store.put('file_name', path=self.settings_widget.file_name.input.text)
                self.settings_widget.console.text = 'Имя файла успешно сохранено в настройках.'
            else:
                self.settings_widget.file_name.input.text = 'Введите имя файла для выгрузки xlsx'
                self.settings_widget.console.text = 'Имя файла указано не верно.'

        if name == 'images_path_button':
            if ex.check_folder_path(self.settings_widget.images_path.input.text):
                self.store.put('images_path', path=self.settings_widget.images_path.input.text)
                self.settings_widget.console.text = 'Путь к папке успешно сохранен в настройках.'
            else:
                self.settings_widget.images_path.input.text = 'Введите путь к папке с фото'
                self.settings_widget.console.text = 'Путь к папке указан не верно либо в ней фотографий'
        if name == 'cell_color_button':
            self.store.put('cell_color', value=self.settings_widget.cell_color.input.text)
            self.settings_widget.console.text = 'Значение цвета успешно сохранено в настройках.'

    def handle_press_step_button(self, text: str):
        if text == 'Шаг 1':
            file_name = self.store.get('file_name')['path']
            self.handle_widget.console.text = 'Файл найден.\n'
            self.handle_widget.console.text += f'Обрабатывается файл : {str(file_name)} \n'
            self.table, self.title = ex.get_worksheet(file_name)
            self.handle_widget.step_button.text = 'Шаг 2'

        elif text == 'Шаг 2':
            color = self.store.get('cell_color')['value']
            m_table, m_row, raws = ex.get_table(self.table, 2, 10)
            self.handle_widget.console.text += f'Основная таблица содержит {raws} строк.\n'
            update_table, _, raws = ex.get_table(self.table, m_row, 10)
            self.handle_widget.console.text += f'Таблица для обнавления содержит {raws} строк.\n'
            self.handle_widget.console.text += f'Выбран цвет выделенных ячеек: {color} \n'
            self.del_table, table_norm, table_err = ex.separate_table(m_table, color)
            self.handle_widget.console.text += f'Таблица для удаления содержит {len(self.del_table)} строк.\n'
            start_id = max(m_table, key=lambda x: x[0].value)[0].value
            update_table = ex.set_value(update_table, 0, start_id, True)
            self.update_table = ex.set_value(update_table, 9, '#новые поступления#', False)
            self.handle_widget.step_button.text = 'Шаг 3'

        elif text == 'Шаг 3':
            images_path = self.store.get('images_path')['path']
            self.handle_widget.console.text += f'Выбран путь к папке с фотографиями: {images_path} \n'
            response, flag = ex.check_images(images_path, self.update_table)
            self.handle_widget.console.text += response
            if flag:
                self.handle_widget.step_button.text = 'Шаг 4'

        elif text == 'Шаг 4':
            folder_path = self.store.get('save_dir_path')['path']
            response = ex.get_file_from_table(folder_path, 'update', self.update_table, self.title)
            self.handle_widget.console.text += response
            response = ex.get_file_from_table(folder_path, 'del', self.del_table, self.title)
            self.handle_widget.console.text += response
            self.handle_widget.console.text += f'Обработка файла успешно завершена.'\
                                               f'\nМожно переходить к загрузки данных на сервер.\n'
            self.handle_widget.step_button.text = 'Шаг 1'

    def load_press_step_button(self, text):
        if text == 'Шаг 1':
            self.columns = sql.get_table_columns()
            self.load_widget.console.text = '\n'.join([f'{i}. {col}' for i, col in enumerate(self.columns)])
            self.load_widget.input.text = 'Введите номера выбранных колонок таблицы через запятую.'
            self.load_widget.step_button_2.text = 'Шаг 2'

        elif text == 'Шаг 2':
            numbers_ = self.load_widget.input.text.split(',')
            numbers = []
            for num in numbers_:
                num = num.strip()
                try:
                    num = int(num)
                    numbers.append(num)
                except ValueError:
                    self.load_widget.console.text = f'Значение "{num}" не является числом.' \
                                                    f'\nПопробуйте ещё раз.'
                    self.load_widget.input.text = 'Введите номера выбранных колонок таблицы через запятую.'
                    break
            if len(numbers_) == len(numbers):
                self.columns = [self.columns[num] for num in numbers]
                self.load_widget.console.text = 'Определены следующие колонки:\n'
                self.load_widget.console.text += '\n'.join([f'{i}. {col}' for i, col in enumerate(self.columns)])
                self.load_widget.input.text = 'Введите представления имён выбранных колонок в файле через запятую.'
                self.load_widget.step_button_1.text = 'Шаг 2'
                self.load_widget.step_button_2.text = 'Шаг 3'

        elif text == 'Шаг 3':
            names = self.load_widget.input.text.split(',')
            if len(names) == len(self.columns):
                self.columns = [(self.columns[i], names[i].strip()) for i in range(len(names))]
                self.load_widget.console.text = 'Определены следующие колонки:\n'
                m1, m2 = [max(map(len, col)) for col in zip(*self.columns)]
                temp = f"""{{}}. {{:>{m1 + 2}}} -- {{:<{m2 + 2}}}"""
                self.load_widget.console.text += '\n'.join([temp.format(i + 1, *col) for i, col in enumerate(self.columns)])
                self.load_widget.console.text += f'\nНажмите кнопку "Шаг 4" чтобы выгрузить данные в файл.' \
                                                 f'\nНажмите кнопку "Шаг 1" если хотите изменить выбранные колонки.'
                self.load_widget.input.text = ''
                self.store.put('columns', names=self.columns)
                self.load_widget.step_button_1.text = 'Шаг 1'
                self.load_widget.step_button_2.text = 'Шаг 4'
            else:
                self.load_widget.input.text = 'Количество выбранных имён не соответствует числу колонок. Попробуйте ещё раз.'

        elif text == 'Шаг 4':
            if self.store.get('columns')['names']:
                self.columns = self.store.get('columns')['names']
                save_dir_path = self.store.get('save_dir_path')['path']
                file_name = self.store.get('file_name')['path']
                sql.get_file_from_data(save_dir_path, file_name, self.columns)
                self.load_widget.console.text += '\nДанные выгружены в файл.'
            else:
                self.console.text = f'Нет наименований колонок таблицы для выгрузки.' \
                                    f'\nВыполните шаги с 1 по 3.'

class ContainerApp(App):

    def build(self):
        return Container()


if __name__ == '__main__':
    if hasattr(sys, '_MEIPASS'):
        resource_add_path(os.path.join(sys._MEIPASS))

    if not ex.check_file_path('settings.json'):
        file = open('settings.json', 'w', encoding='utf-8',)
        file.write('{"save_dir_path": {"path": ""}, "file_name": {"path": ""}, "images_path": {"path": ""}, "cell_color": {"value": ""}, "columns": {"names": []}}')
        file.close()

    Window.size = (700, 700)
    ContainerApp().run()
