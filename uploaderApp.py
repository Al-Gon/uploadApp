import os
import sys
import excel_functions as ex
import sql_functions as sql
from kivy.resources import resource_add_path
from kivy.uix.gridlayout import GridLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.scrollview import ScrollView
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.properties import StringProperty, ListProperty, ObjectProperty, NumericProperty
from kivy.storage.jsonstore import JsonStore
from kivy.core.window import Window
from kivy.app import App
from kivy.lang import Builder

Builder.load_file('base_widgets.kv')
Builder.load_file('setting_layout.kv')
Builder.load_file('handle_layout.kv')
Builder.load_file('load_layout.kv')
Builder.load_file('upload_layout.kv')

class ButtonGetColors(FloatLayout):
    button_text = StringProperty('')
    pass

class ButtonSaveColor(FloatLayout):
    pass

class ChooseColorItem(GridLayout):
    label_color = StringProperty('')
    check_box = ObjectProperty()

class ChooseColor(GridLayout):
    cols = 1
    padding: [5, 5, 5, 5]
    size_hint = (1, None)
    save_button = ObjectProperty()
    items = ListProperty([])
    color = StringProperty('')
    height = NumericProperty()

    def set_height(self):
        height = 0
        for child in self.children:
            height += child.height
        self.height = height + 10

    def on_items(self, instance, items):
        self.clear_widgets()
        for item in self.items:
            new_item = ChooseColorItem()
            new_item.label_color = item
            if len(self.items) == 1:
                new_item.check_box.active = True
                self.color = item
            new_item.check_box.bind(active=self.choose_color)
            self.add_widget(new_item)
            self.set_height()

    def choose_color(self, instance, is_active):
        self.color = instance.parent.label_color

    def add_button(self):
        self.save_button = ButtonSaveColor()
        self.add_widget(self.save_button)
        self.set_height()

    def remove_button(self):
        self.remove_widget(self.save_button)
        self.set_height()

class CheckBoxColors(GridLayout):
    text_color = ObjectProperty()
    fill_color = ObjectProperty()

class ItemLabel(Label):
    message = StringProperty('')

class ScrollLabel(ScrollView):
    message = StringProperty('')

class InputBlock(FloatLayout):
    input_string = StringProperty('')

class ScreenTemplate(Screen):
    pass

class SettingLayout(BoxLayout):
    grid_height = NumericProperty()
    pass

class LoadLayout(BoxLayout):
    pass

class HandleLayout(BoxLayout):
    pass

class UploadLayout(BoxLayout):
    pass

class NewScreenManager(ScreenManager):
    pass

class Uploader(FloatLayout):
    def __init__(self, **kwargs):
        super(Uploader, self).__init__(**kwargs)
        layouts = [(SettingLayout(), 'Настройки'),
                   (LoadLayout(), 'Загрузка'),
                   (HandleLayout(), 'Обработка'),
                   (UploadLayout(), 'Выгрузка')]
        widgets = []
        for i in range(len(layouts)):
            screen = ScreenTemplate(name=f'screen{i + 1}')
            screen.text_label.text = f'[size=18]{layouts[i][1]}[/size]'
            screen.main_screen.add_widget(layouts[i][0])
            self._screen_manager.add_widget(screen)
            widgets.append(screen.main_screen.children[0])

        self.settings_widget = widgets[0]
        self.load_widget = widgets[1]
        self.handle_widget = widgets[2]
        self.upload_widget = widgets[3]
        self.store = JsonStore('settings.json')
        self.keeper = {}

        for key, obj in self.settings_widget.ids.items():
            if key in self.store.keys():
                value = self.store.get(key)[key.rsplit('_', 1)[-1]]
                if value:
                    obj.input.text = value

        if len(self.store.get('cell_color')['type']):
            c_type = self.store.get('cell_color')['type']
            if c_type == 'text':
                self.settings_widget.checkbox_colors.text_color.active = True
                self.settings_widget.get_colors.button_text = 'Получить цвет шрифта ячеек'
            if c_type == 'fill':
                self.settings_widget.checkbox_colors.fill_color.active = True
                self.settings_widget.get_colors.button_text = 'Получить цвет заливки ячеек'
        if len(self.store.get('cell_color')['value']):
            color = self.store.get('cell_color')['value']
            self.settings_widget.choose_color.items = [color]

        self.settings_widget.checkbox_colors.fill_color.bind(active=self.check_cell_colors)
        self.settings_widget.checkbox_colors.text_color.bind(active=self.check_cell_colors)
        self.settings_widget.grid_height = self.grid_height(self.settings_widget.grid)

        if len(self.store.get('columns')['names']):
            self.keeper['columns'] = self.store.get('columns')['names']
            self.load_widget.console.message = 'Колонки и представления для выгрузки в файл:\n'
            self.load_widget.console.message += '\n'.join([f'{i}. {col[0]} "{col[1]}"' for i, col in enumerate(self.keeper['columns'])])
            self.load_widget.console.message += f'\nЕсли нужно выгрузить данные из данных колонок в файл нажмите "Шаг 4".'\
                                             f'\nЕсли нужно изменить колонки нажмите "Шаг 1" и выполните шаги с 1 по 3.'

    @staticmethod
    def grid_height(inst):
        height = 0
        for child in inst.children:
            height += child.height
        return height + 25

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
            self.settings_widget.console.message = f'Имя файла "{file_name}" успешно сохранено в настройках.'
        else:
            input_obj.text = 'Введите имя файла (будет преобразованно к "имя_месяц_дата.xlsx").'
            self.settings_widget.console.message = 'Имя файла указано не верно.'

    def handle_path(self, name: str):
        if name == 'save_dir_path_button':
            if ex.check_folder_path(self.settings_widget.save_dir_path.input.text):
                self.store.put('save_dir_path', path=self.settings_widget.save_dir_path.input.text)
                self.settings_widget.console.message = 'Путь к папке успешно сохранен в настройках.'
            else:
                self.settings_widget.save_dir_path.input.text = 'Введите путь к папке для хранения файлов'
                self.settings_widget.console.message = 'Путь к папке указан не верно.'

        if name == 'file_name_button':
            self.save_file_name(self.settings_widget.file_name.input, 'file_name')

        if name == 'images_path_button':
            images_path = self.settings_widget.images_path.input.text
            if ex.check_folder_path(self.settings_widget.images_path.input.text):
                self.store.put('images_path', path=images_path)
                self.settings_widget.console.message = 'Путь к папке успешно сохранен в настройках.'
            else:
                self.settings_widget.images_path.input.text = 'Введите путь к папке с фото'
                self.settings_widget.console.message = 'Путь к папке указан не верно либо в ней фотографий'

        if name == 'update_file_name_button':
            self.save_file_name(self.settings_widget.update_file_name.input, 'update_file_name')

        if name == 'del_file_name_button':
            self.save_file_name(self.settings_widget.del_file_name.input, 'del_file_name')

    def check_cell_colors(self, instance, is_active):
        if instance.name == 'text_color':
            self.settings_widget.get_colors.button_text = 'Получить цвет шрифта ячеек'
        if instance.name == 'fill_color':
            self.settings_widget.get_colors.button_text = 'Получить цвет заливки ячеек'
        self.settings_widget.choose_color.items = []
        self.settings_widget.choose_color.set_height()
        self.settings_widget.grid_height = self.grid_height(self.settings_widget.grid)
        self.settings_widget.console.message = ''

    def save_cell_color(self):
        color = self.settings_widget.choose_color.color
        message = f'Выбран цвет [b][color=#{color}]{color}[/color][/b] '
        c_type = ''
        if self.settings_widget.checkbox_colors.text_color.active:
            c_type = 'text'
            message += f'текста выделенных ячеек'
        elif self.settings_widget.checkbox_colors.fill_color.active:
            c_type = 'fill'
            message += f'заливки выделенных ячеек'
        self.store['cell_color'] = {'type': c_type, 'value': color}
        self.settings_widget.console.message = message
        self.settings_widget.choose_color.items = [color]
        self.settings_widget.choose_color.remove_button()
        self.settings_widget.grid_height = self.grid_height(self.settings_widget.grid)
        self.handle_widget.step_button.text = 'Шаг 1'
        self.handle_widget.console.message = 'Консоль'

    def get_cell_colors(self, name):
        if 'table' in self.keeper.keys():
            colors = []
            if name == 'Получить цвет шрифта ячеек':
                colors = ex.search_cell_font_colors(self.keeper['table'])
                if colors:
                    self.settings_widget.console.message = f'Цвета шрифта выделенных ячеек:\n'
                else:
                    self.settings_widget.console.message = f'В файле отсутствуют ячейки выделенные цветом шрифта.\n'
            if name == 'Получить цвет заливки ячеек':
                colors = ex.search_cell_fill_colors(self.keeper['table'])
                if colors:
                    self.settings_widget.console.message = f'Цвета заливки выделенных ячеек:\n'
                else:
                    self.settings_widget.console.message = f'В файле отсутствуют ячейки выделенные цветом заливки.\n'
            if colors:
                self.settings_widget.console.message += ', '.join(f'[b][color=#{c}]{c}[/color][/b]' for c in colors)
                self.settings_widget.choose_color.items = colors
                self.settings_widget.choose_color.add_button()
                self.settings_widget.grid_height = self.grid_height(self.settings_widget.grid)
        else:
            self.settings_widget.console.message = 'Перейдите на вкладку "Обработка" и выполните "Шаг 1".'

    def load_press_step(self, text):
        missing = self.check_settings(['save_dir_path', 'file_name'])
        if missing:
            self.load_widget.console.message = self.settings_report(missing)
        else:
            if text == 'Шаг 1':
                self.keeper['columns'] = sql.get_table_columns()
                self.load_widget.console.message = 'В таблице определены следующие поля:\n'
                self.load_widget.console.message += '\n'.join([f'{i + 1}. {col}' for i, col in enumerate(self.keeper['columns'][1:])])
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
                        if num not in list(range(1, len(self.keeper['columns']))):
                            info += f'Номера "{num}" нет в списке колонок.\n'
                        else:
                            numbers.append(num)
                    except ValueError:
                        info += f'Значение "{num}" не является числом.\n'

                if len(numbers) == len(numbers_):
                    self.keeper['columns'] = [self.keeper['columns'][0]] + [self.keeper['columns'][num] for num in numbers]
                    self.load_widget.console.message = 'Определены следующие колонки:\n'
                    self.load_widget.console.message += '\n'.join([f'{i + 1}. {col}' for i, col in enumerate(self.keeper['columns'])])
                    self.load_widget.input.text = 'Введите представления имён выбранных колонок в файле через запятую.'
                    self.load_widget.step_button_1.text = 'Шаг 2'
                    self.load_widget.step_button_2.text = 'Шаг 3'
                else:
                    self.load_widget.console.message = info + 'Попробуйте ещё раз.'
                    self.load_widget.input.text = 'Введите номера выбранных колонок таблицы через запятую.'

            elif text == 'Шаг 3':
                names = self.load_widget.input.text.split(',')
                if len(names) == len(self.keeper['columns']):
                    self.keeper['columns'] = [(self.keeper['columns'][i], names[i].strip()) for i in range(len(names))]
                    self.load_widget.console.message = 'Определены следующие колонки:\n'
                    m1, m2 = [max(map(len, col)) for col in zip(*self.keeper['columns'])]
                    temp = f'{{}}. {{:>{m1 + 2}}} -- {{:<{m2 + 2}}}'
                    self.load_widget.console.message += '\n'.join([temp.format(i + 1, *col) for i, col in enumerate(self.keeper['columns'])])
                    self.load_widget.console.message += f'\nНажмите кнопку "Шаг 4" чтобы выгрузить данные в файл.' \
                                                        f'\nНажмите кнопку "Шаг 1" если хотите изменить выбранные колонки.'
                    self.load_widget.input.text = ''
                    self.store.put('columns', names=self.keeper['columns'])
                    self.load_widget.step_button_1.text = 'Шаг 1'
                    self.load_widget.step_button_2.text = 'Шаг 4'
                else:
                    self.load_widget.input.text = 'Количество выбранных имён не соответствует числу колонок. Попробуйте ещё раз.'

            elif text == 'Шаг 4':
                if self.store.get('columns')['names']:
                    self.keeper['columns'] = self.store.get('columns')['names']
                    save_dir_path = self.store.get('save_dir_path')['path']
                    file_name = self.store.get('file_name')['name']
                    info = sql.get_file_from_data(save_dir_path, file_name, self.keeper['columns'])
                    self.load_widget.console.message += f'\n{info}'
                else:
                    self.console.message = f'Нет наименований колонок таблицы для выгрузки.' \
                                        f'\nВыполните шаги с 1 по 3.'

    def handle_press_step(self, text: str):
        missing = self.check_settings(['save_dir_path', 'file_name', 'images_path'])
        if missing:
            self.handle_widget.console.message = self.settings_report(missing)
        else:
            if text == 'Шаг 1':
                file_name = self.store.get('file_name')['name']
                save_dir_path = self.store.get('save_dir_path')['path']
                file_path = os.path.join(save_dir_path, file_name)
                if ex.check_file_path(file_path):
                    self.handle_widget.console.message = 'Файл найден.\n'
                    self.handle_widget.console.message += f'Обрабатывается файл : {str(file_path)} \n'
                    self.keeper['table'], self.keeper['title'] = ex.get_worksheet(file_path)
                    self.handle_widget.step_button.text = 'Шаг 2'
                else:
                    self.handle_widget.console.message = f'Файл "{file_path}" не найден, либо имя указанно не верно.' \
                                                      f'\nПроверьте указанный путь и измените настройки.' \
                                                      f'\nПовторите операцию заново.'
            if text == 'Шаг 2':
                self.keeper['m_table'], m_row = ex.get_table(self.keeper['table'], 2, 10)
                self.handle_widget.console.message += f'Основная таблица содержит {len(self.keeper["m_table"])} строк.\n'
                self.keeper['update_table'], _ = ex.get_table(self.keeper['table'], m_row, 10)
                self.handle_widget.step_button.text = 'Шаг 3'

            if text == 'Шаг 3':
                if not self.check_settings(['cell_color']):
                    color = self.store.get('cell_color')['value']
                    c_type = self.store.get('cell_color')['type']
                    self.handle_widget.console.message += f'Выбран цвет [b][color=#{color}]{color}[/color][/b] '
                    if c_type == 'text':
                        self.handle_widget.console.message += f'текста выделенных ячеек'
                    if c_type == 'fill':
                        self.handle_widget.console.message += f'заливки выделенных ячеек'
                    self.handle_widget.console.message += f' для формирования файла удаления. \n'
                    self.handle_widget.step_button.text = 'Шаг 4'
                else:
                    self.handle_widget.console.message += f'Перейдите на вкладку настройки и выберете параметры \n' \
                                                          f'выделенных ячеек для формирования файла удаления. \n'

            if text == 'Шаг 4':
                self.handle_widget.console.message += f'Таблица для обновления содержит {len(self.keeper["update_table"])} строк.\n'
                if not self.keeper['update_table']:
                    self.handle_widget.console.message += f'Файл для обновления создан не будет.\n'
                    del self.keeper['update_table']
                else:
                    start_id = max(self.keeper['m_table'], key=lambda x: x[0].value)[0].value
                    self.keeper['update_table'] = ex.set_value(self.keeper['update_table'], 0, start_id, True)
                    self.keeper['update_table'] = ex.set_value(self.keeper['update_table'], 9, '#новые поступления#', False)

                color = self.store.get('cell_color')['value']
                c_type = self.store.get('cell_color')['type']
                del_table, table_norm, table_err = ex.separate_table(self.keeper['m_table'], color, c_type)
                self.handle_widget.console.message += f'Таблица для удаления содержит {len(del_table)} строк.\n'
                if not del_table:
                    self.handle_widget.console.message += f'Файл для удаления создан не будет.\n'
                else:
                    self.keeper['del_table'] = del_table

                self.handle_widget.step_button.text = 'Шаг 5'

            if text == 'Шаг 5':
                if 'update_table' in self.keeper.keys():
                    images_path = self.store.get('images_path')['path']
                    self.handle_widget.console.message += f'Выбран путь к папке с фотографиями: {images_path} \n'
                    response, flag = ex.check_images(images_path, self.keeper['update_table'])
                    self.handle_widget.console.message += response
                    if not flag:
                        self.handle_widget.step_button.text = 'Шаг 5'
                else:
                    self.handle_widget.console.message += f'Проверка фотографий не произведена из-за отсутствия \
                                                        файла обновления.\n'
                self.handle_widget.step_button.text = 'Шаг 6'

            if text == 'Шаг 6':
                folder_path = self.store.get('save_dir_path')['path']
                update_file_name = self.store.get('update_file_name')['name']
                del_file_name = self.store.get('del_file_name')['name']
                if 'update_table' in self.keeper.keys():
                    response = ex.get_file_from_table(folder_path, update_file_name, self.keeper['update_table'], self.keeper['title'])
                    self.handle_widget.console.message += response
                else:
                    self.handle_widget.console.message += f'Файл обновления не создан.\n'
                if 'del_table' in self.keeper.keys():
                    response = ex.get_file_from_table(folder_path, del_file_name, self.keeper['del_table'], self.keeper['title'])
                    self.handle_widget.console.message += response
                else:
                    self.handle_widget.console.message += f'Файл для удаления не создан.\n'
                self.handle_widget.console.message += f'Обработка файла успешно завершена.'
                self.handle_widget.step_button.text = 'Шаг 1'

    def upload_step(self):
        missing = self.check_settings(['save_dir_path', 'update_file_name', 'images_path', 'columns'])
        if missing:
            self.upload_widget.console.message = self.settings_report(missing)
        elif 'update_table' not in self.keeper.keys():
            self.upload_widget.console.message = f'Нет данных для загрузки.\n' \
                                              f'Перейдите к операции "Обработка"'
        else:
            images_path = self.store.get('images_path')['path']
            queries = ex.get_insert_queries(images_path, self.keeper['update_table'], self.store.get('columns')['names'])
            messages = sql.make_query(queries)
            if messages:
                self.upload_widget.console.message = 'Произошли следующие ошибки:'
                self.upload_widget.console.message += '\n'.join(messages)
            else:
                self.upload_widget.console.message = f'Было успешно добавлено {len(self.keeper["update_table"])} записей.'
                del self.keeper['update_table']

    def delete_step(self):
        missing = self.check_settings(['save_dir_path', 'del_file_name'])
        if missing:
            self.upload_widget.console.message = self.settings_report(missing)
        elif 'del_table' not in self.keeper.keys():
            self.upload_widget.console.message = f'Нет данных для удаления.\n' \
                                              f'Перейдите к операции "Обработка"'
        else:
            queries = ex.get_delete_query(self.keeper['del_table'])
            messages = sql.make_query(queries)
            if messages:
                self.upload_widget.console.message = 'Произошли следующие ошибки:'
                self.upload_widget.console.message += '\n'.join(messages)
            else:
                self.upload_widget.console.message = f'Было успешно удалено {len(self.keeper["del_table"])} записей.'
                del self.keeper['del_table']


class UploaderApp(App):

    def build(self):
        return Uploader()


if __name__ == '__main__':
    if hasattr(sys, '_MEIPASS'):
        resource_add_path(os.path.join(sys._MEIPASS))

    ex.check_version(version='1.0.0')
    Window.size = (700, 700)
    UploaderApp().run()