import os
import sys
import excel_functions as ex
import sql_functions as sql
from kivy.resources import resource_add_path
from kivy.uix.scrollview import ScrollView
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.storage.jsonstore import JsonStore
from kivy.core.window import Window
from kivy.app import App


class ScreenTemplate(Screen):
    pass

class SettingLayout(BoxLayout):
    pass

class LoadLayout(BoxLayout):
    pass

class HandleLayout(BoxLayout):
    pass

class UploadLayout(BoxLayout):
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
        self.upload_widget = self.upload_screen.main_screen.children[0]

        if len(self.store.get('save_dir_path')['path']):
            self.settings_widget.save_dir_path.input.text = self.store.get('save_dir_path')['path']
        if len(self.store.get('file_name')['name']):
            self.settings_widget.file_name.input.text = self.store.get('file_name')['name']
        if len(self.store.get('images_path')['path']):
            self.settings_widget.images_path.input.text = self.store.get('images_path')['path']
        if len(self.store.get('cell_color')['value']):
            self.settings_widget.cell_color.input.text = self.store.get('cell_color')['value']
        if len(self.store.get('update_file_name')['name']):
            self.settings_widget.update_file_name.input.text = self.store.get('update_file_name')['name']
        if len(self.store.get('del_file_name')['name']):
            self.settings_widget.del_file_name.input.text = self.store.get('del_file_name')['name']
        if len(self.store.get('columns')['names']):
            self.columns = self.store.get('columns')['names']
            self.load_widget.console.text = 'Колонки и представления для выгрузки в файл:\n'
            self.load_widget.console.text += '\n'.join([f'{i}. {col[0]} "{col[1]}"' for i, col in enumerate(self.columns)])
            self.load_widget.console.text += f'\nЕсли нужно выгрузить данные из данных колонок в файл нажмите "Шаг 4".'\
                                             f'\nЕсли нужно изменить колонки нажмите "Шаг 1" и выполните шаги с 1 по 3.'

    def check_settings(self, settings: list):
        missing = []
        for setting in settings:
            for k, v in self.store.get(setting).items():
                if not v:
                    missing.append(f'{setting}"{k}"')
        return missing

    @staticmethod
    def settings_report(missing: list):
        report = 'Отсутствуют следующие настройки для выполнения операции:\n'
        report += '\n'.join([f'{i + 1}. {s}' for i, s in enumerate(missing)])
        report += f'\nПерейдите к настройкам, заполните необходимые поля,' \
                  f'\nсохраните их и вернитесь к выполнению операции.'
        return report

    def save_file_name(self, input_obj: object, field: str):
        file_name = input_obj.text.strip()
        if not ex.check_file_name(file_name):
            file_name = ex.make_file_name(file_name)
        if len(file_name):
            self.store.put(field, name=file_name)
            input_obj.text = file_name
            self.settings_widget.console.text = f'Имя файла "{file_name}" успешно сохранено в настройках.'
        else:
            input_obj.text = 'Введите имя файла (будет преобразованно к "имя_месяц_дата.xlsx").'
            self.settings_widget.console.text = 'Имя файла указано не верно.'


    def handle_path(self, name: str):
        if name == 'save_dir_path_button':
            if ex.check_folder_path(self.settings_widget.save_dir_path.input.text):
                self.store.put('save_dir_path', path=self.settings_widget.save_dir_path.input.text)
                self.settings_widget.console.text = 'Путь к папке успешно сохранен в настройках.'
            else:
                self.settings_widget.save_dir_path.input.text = 'Введите путь к папке для хранения файлов'
                self.settings_widget.console.text = 'Путь к папке указан не верно.'

        if name == 'file_name_button':
            self.save_file_name(self.settings_widget.file_name.input, 'file_name')

        if name == 'images_path_button':
            images_path = self.settings_widget.images_path.input.text
            if ex.check_folder_path(self.settings_widget.images_path.input.text):
                self.store.put('images_path', path=images_path)
                self.settings_widget.console.text = 'Путь к папке успешно сохранен в настройках.'
            else:
                self.settings_widget.images_path.input.text = 'Введите путь к папке с фото'
                self.settings_widget.console.text = 'Путь к папке указан не верно либо в ней фотографий'

        if name == 'cell_color_button':
            cell_color = self.settings_widget.cell_color.input.text
            self.store.put('cell_color', value=cell_color)
            self.settings_widget.console.text = 'Значение цвета успешно сохранено в настройках.'

        if name == 'update_file_name_button':
            self.save_file_name(self.settings_widget.update_file_name.input, 'update_file_name')

        if name == 'del_file_name_button':
            self.save_file_name(self.settings_widget.del_file_name.input, 'del_file_name')

    def load_press_step(self, text):
        missing = self.check_settings(['save_dir_path', 'file_name'])
        if missing:
            self.load_widget.console.text = self.settings_report(missing)
        else:
            if text == 'Шаг 1':
                self.columns = sql.get_table_columns()
                self.load_widget.console.text = 'В таблице определены следующие поля:\n'
                self.load_widget.console.text += '\n'.join([f'{i + 1}. {col}' for i, col in enumerate(self.columns[1:])])
                self.load_widget.input.text = f'Введите номера выбранных полей таблицы через запятую.' \
                                              f'\nКолонка "id" будет добавлена по умолчанию.'
                self.load_widget.step_button_2.text = 'Шаг 2'

            elif text == 'Шаг 2':
                numbers_ = self.load_widget.input.text.split(',')
                numbers = []
                info = ''
                for num in numbers_:
                    num = num.strip()
                    try:
                        num = int(num)
                        if num not in list(range(1, len(self.columns))):
                            info += f'Номера "{num}" нет в списке колонок.\n'
                        else:
                            numbers.append(num)
                    except ValueError:
                        info += f'Значение "{num}" не является числом.\n'

                if len(numbers) == len(numbers_):
                    self.columns = [self.columns[0]] + [self.columns[num] for num in numbers]
                    self.load_widget.console.text = 'Определены следующие колонки:\n'
                    self.load_widget.console.text += '\n'.join([f'{i + 1}. {col}' for i, col in enumerate(self.columns)])
                    # self.load_widget.console.texture_update()
                    self.load_widget.input.text = 'Введите представления имён выбранных колонок в файле через запятую.'
                    self.load_widget.step_button_1.text = 'Шаг 2'
                    self.load_widget.step_button_2.text = 'Шаг 3'
                else:
                    self.load_widget.console.text = info + 'Попробуйте ещё раз.'
                    self.load_widget.input.text = 'Введите номера выбранных колонок таблицы через запятую.'

            elif text == 'Шаг 3':
                names = self.load_widget.input.text.split(',')
                if len(names) == len(self.columns):
                    self.columns = [(self.columns[i], names[i].strip()) for i in range(len(names))]
                    self.load_widget.console.text = 'Определены следующие колонки:\n'
                    m1, m2 = [max(map(len, col)) for col in zip(*self.columns)]
                    temp = f'{{}}. {{:>{m1 + 2}}} -- {{:<{m2 + 2}}}'
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
                    file_name = self.store.get('file_name')['name']
                    info = sql.get_file_from_data(save_dir_path, file_name, self.columns)
                    self.load_widget.console.text += f'\n{info}'
                else:
                    self.console.text = f'Нет наименований колонок таблицы для выгрузки.' \
                                        f'\nВыполните шаги с 1 по 3.'

    def handle_press_step(self, text: str):
        missing = self.check_settings(['save_dir_path', 'file_name', 'images_path', 'cell_color'])
        if missing:
            self.handle_widget.console.text = self.settings_report(missing)
        else:
            if text == 'Шаг 1':
                file_name = self.store.get('file_name')['name']
                save_dir_path = self.store.get('save_dir_path')['path']
                file_path = os.path.join(save_dir_path, file_name)
                if ex.check_file_path(file_path):
                    self.handle_widget.console.text = 'Файл найден.\n'
                    self.handle_widget.console.text += f'Обрабатывается файл : {str(file_path)} \n'
                    self.table, self.title = ex.get_worksheet(file_path)
                    self.handle_widget.step_button.text = 'Шаг 2'
                else:
                    self.handle_widget.console.text = f'Файл "{file_path}" не найден, либо имя указанно не верно.' \
                                                      f'\nПроверьте указанный путь и измените настройки.' \
                                                      f'\nПовторите операцию заново.'

            elif text == 'Шаг 2':
                color = self.store.get('cell_color')['value']
                m_table, m_row = ex.get_table(self.table, 2, 10)
                self.handle_widget.console.text += f'Основная таблица содержит {len(m_table)} строк.\n'
                update_table, _ = ex.get_table(self.table, m_row, 10)
                self.handle_widget.console.text += f'Таблица для обнавления содержит {len(update_table)} строк.\n'
                if not update_table:
                    self.handle_widget.console.text += f'Файл для обновления создан не будет.\n'
                else:
                    start_id = max(m_table, key=lambda x: x[0].value)[0].value
                    update_table = ex.set_value(update_table, 0, start_id, True)
                    self.update_table = ex.set_value(update_table, 9, '#новые поступления#', False)

                self.handle_widget.console.text += f'Выбран цвет выделенных ячеек: {color} \n'
                del_table, table_norm, table_err = ex.separate_table(m_table, color)
                self.handle_widget.console.text += f'Таблица для удаления содержит {len(del_table)} строк.\n'
                if not del_table:
                    self.handle_widget.console.text += f'Файл для удаления создан не будет.\n'
                else:
                    self.del_table = del_table

                self.handle_widget.step_button.text = 'Шаг 3'

            elif text == 'Шаг 3':
                if self.update_table:
                    images_path = self.store.get('images_path')['path']
                    self.handle_widget.console.text += f'Выбран путь к папке с фотографиями: {images_path} \n'
                    response, flag = ex.check_images(images_path, self.update_table)
                    self.handle_widget.console.text += response
                    if flag:
                        self.handle_widget.step_button.text = 'Шаг 4'
                else:
                    self.handle_widget.console.text += f'Проверка фотографий не произведена из-за отсутствия \
                                                        файла обновления.\n'
                    self.handle_widget.step_button.text = 'Шаг 4'

            elif text == 'Шаг 4':
                folder_path = self.store.get('save_dir_path')['path']
                update_file_name = self.store.get('update_file_name')['name']
                del_file_name = self.store.get('del_file_name')['name']
                if self.update_table:
                    response = ex.get_file_from_table(folder_path, update_file_name, self.update_table, self.title)
                    self.handle_widget.console.text += response
                else:
                    self.handle_widget.console.text += f'Файл обновления не создан.\n'
                if self.del_table:
                    response = ex.get_file_from_table(folder_path, del_file_name, self.del_table, self.title)
                    self.handle_widget.console.text += response
                else:
                    self.handle_widget.console.text += f'Файл для удаления не создан.\n'
                self.handle_widget.console.text += f'Обработка файла успешно завершена.'
                self.handle_widget.step_button.text = 'Шаг 1'

    def upload_step(self):
        missing = self.check_settings(['save_dir_path', 'update_file_name', 'images_path', 'columns'])
        if missing:
            self.upload_widget.console.text = self.settings_report(missing)
        elif not self.update_table:
            self.upload_widget.console.text = f'Нет данных для загрузки.\n' \
                                              f'Перейдите к операции "Обработка"'
        else:
            images_path = self.store.get('images_path')['path']
            queries = ex.get_insert_queries(images_path, self.update_table, self.store.get('columns')['names'])
            messages = sql.make_query(queries)
            if messages:
                self.upload_widget.console.text = 'Произошли следующие ошибки:'
                self.upload_widget.console.text += '\n'.join(messages)
            else:
                self.upload_widget.console.text = f'Было успешно добавлено {len(self.update_table)} записей.'
                self.update_table = None

    def delete_step(self):
        missing = self.check_settings(['save_dir_path', 'del_file_name'])
        if missing:
            self.upload_widget.console.text = self.settings_report(missing)
        elif not self.del_table:
            self.upload_widget.console.text = f'Нет данных для удаления.\n' \
                                              f'Перейдите к операции "Обработка"'
        else:
            queries = ex.get_delete_query(self.del_table)
            messages = sql.make_query(queries)
            if messages:
                self.upload_widget.console.text = 'Произошли следующие ошибки:'
                self.upload_widget.console.text += '\n'.join(messages)
            else:
                self.upload_widget.console.text = f'Было успешно удалено {len(self.del_table)} записей.'
                self.del_table = None


class ContainerApp(App):

    def build(self):
        return Container()


if __name__ == '__main__':
    if hasattr(sys, '_MEIPASS'):
        resource_add_path(os.path.join(sys._MEIPASS))

    if not ex.check_file_path('settings.json'):
        file = open('settings.json', 'w', encoding='utf-8',)
        file.write('{\
                    "save_dir_path": {"path": ""},\
                    "file_name": {"name": ""},\
                    "images_path": {"path": ""},\
                    "cell_color": {"value": ""},\
                    "update_file_name": {"name": ""},\
                    "del_file_name": {"name": ""},\
                    "columns": {"names": []}\
                    }')
        file.close()

    Window.size = (700, 700)
    ContainerApp().run()
