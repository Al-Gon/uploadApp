import os
import sys

from kivy.uix.anchorlayout import AnchorLayout
import excel_functions as ex
import sql_functions as sql
import parser_functions as pr
from handlerscroll import HandlerScroll
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
Builder.load_file('load_layout.kv')
Builder.load_file('parser_layout.kv')
Builder.load_file('handle_layout.kv')
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
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.settings_widget = NumericProperty()
        self.handler_scroll = HandlerScroll(size_hint=(1, None))
        self.scroll.add_widget(self.handler_scroll)
    pass

class ParserLayout(BoxLayout):
    grid_height = NumericProperty()
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
                   (ParserLayout(), 'Парсинг'),
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
        self.parser_widget = widgets[2]
        self.handle_widget = widgets[3]
        self.upload_widget = widgets[4]
        self.store = JsonStore('settings.json')
        self.keeper = {}
        self.handle_widget.handler_scroll.keeper = self.keeper

        for key, obj in self.settings_widget.ids.items():
            if key in self.store.keys():
                value = self.store.get(key)[key.rsplit('_', 1)[-1]]
                if value:
                    if isinstance(value, str):
                        obj.input.text = value
                    if isinstance(value, list):
                        obj.input.text = ', '.join(value)

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

        save_dir_path = self.store.get('save_dir_path')['path']
        db_file_name = self.store.get('db_file_name')['name']
        if save_dir_path and db_file_name:
            if sql.make_response_query(save_dir_path, db_file_name, sql.check_table('update_table')):
                query = sql.get_table_info('update_table')
                data = sql.make_response_query(save_dir_path, db_file_name, query)
                columns_names = list(map(lambda x: x[1], data))
                self.handle_widget.message = 'Выберите колонку для редактирования и нажмите кнопку "Шаг 1":'
                self.handle_widget.handler_scroll.items = columns_names[1:]

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

    # @staticmethod
    # def output_msg(msg):
    #     return ',\n'.join(msg) if not isinstance(msg, str) else msg

    def save_file_name(self, input_obj: object, field: str, extension: str):
        file_name = input_obj.text.strip()
        substr = bool(field.count('site'))
        massage = f'Введите имя файла (будет преобразованно к "имя_месяц_дата{extension}").'
        if substr:
            massage = f'Введите имя файла (будет преобразованно к "имя_сайт_месяц_дата{extension}").'
        if not ex.check_file_name(file_name):
            file_name = ex.make_file_name(file_name, extension, substr)
        if len(file_name):
            self.store.put(field, name=file_name)
            input_obj.text = file_name
            self.settings_widget.console.message = f'Имя файла "{file_name}" успешно сохранено в настройках.'
        else:
            input_obj.text = massage
            self.settings_widget.console.message = 'Имя файла указано не верно.'

    def handle_path(self, name: str):
        if name == 'save_dir_path_button':
            if ex.check_folder_path(self.settings_widget.save_dir_path.input.text):
                self.store.put('save_dir_path', path=self.settings_widget.save_dir_path.input.text)
                self.settings_widget.console.message = 'Путь к папке успешно сохранен в настройках.'
            else:
                self.settings_widget.save_dir_path.input.text = 'Введите путь к папке для хранения файлов'
                self.settings_widget.console.message = 'Путь к папке указан не верно.'

        if name == 'db_file_name_button':
            self.save_file_name(self.settings_widget.db_file_name.input, 'db_file_name', '.db')

        if name == 'file_name_button':
            self.save_file_name(self.settings_widget.file_name.input, 'file_name', '.xlsx')

        if name == 'images_folder_name_button':
            images_folder_name = self.settings_widget.images_folder_name.input.text.strip()
            save_dir_path = self.store.get('save_dir_path')['path']
            folder_path = os.path.join(save_dir_path, images_folder_name)
            if ex.check_folder_path(folder_path):
                self.store.put('images_folder_name', name=images_folder_name)
                self.settings_widget.console.message = 'Имя папки успешно сохранено в настройках.'
            else:
                self.settings_widget.images_path.input.text = 'Введите путь к папке с фото'
                self.settings_widget.console.message = 'Путь к папке указан не верно либо в ней фотографий'

        if name == 'update_file_name_button':
            self.save_file_name(self.settings_widget.update_file_name.input, 'update_file_name', '.xlsx')

        if name == 'del_file_name_button':
            self.save_file_name(self.settings_widget.del_file_name.input, 'del_file_name', '.xlsx')

        if name == 'category_site_file_name_button':
            self.save_file_name(self.settings_widget.category_site_file_name.input, 'category_site_file_name', '.xlsx')

        if name == 'data_site_file_name_button':
            self.save_file_name(self.settings_widget.data_site_file_name.input, 'data_site_file_name', '.xlsx')

        if name == 'category_site_urls_button':
            urls_ = self.settings_widget.category_site_urls.input.text.split(',')
            urls = [url.strip() for url in urls_ if pr.check_url(url.strip())]
            if urls:
                self.store.put('category_site_urls', urls=urls)
                message = ' ,\n'.join(urls)
                self.settings_widget.console.message = f'Данные url: "{message}" сохранены в настройках.'
                self.parser_widget.choose_url.items = urls
            else:
                self.settings_widget.console.message = 'Ни одного url не было сохранено.'
                self.settings_widget.category_site_urls.input.text = 'Введите url адреса страниц категорий сайтов (через запятую).'

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
        """
        Step 1 - selecting column numbers for main table in database.
        Step 2 - selecting columns names for main table in database.
        Step 3 - setting users columns names.
        Step 4 - create a main table in database and save it in file.
        :param text: step button name
        """
        missing = self.check_settings(['save_dir_path', 'db_file_name', 'file_name'])
        if missing:
            self.load_widget.console.message = self.settings_report(missing)
        else:
            save_dir_path = self.store.get('save_dir_path')['path']
            db_file_name = self.store.get('db_file_name')['name']
            file_name = self.store.get('file_name')['name']

            if text == 'Шаг 1':
                query = sql.get_table_info('catalog')
                data = sql.make_response_query(save_dir_path, db_file_name, query)
                self.keeper['columns'] = list(map(lambda x: x[1], data))
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
                    self.load_widget.console.message += '\n'.join([f'{i + 1}. {col}' for i, col in enumerate(self.keeper['columns'][1:])])
                    self.load_widget.input.text = 'Введите представления имён выбранных колонок в файле через запятую.'
                    self.load_widget.step_button_1.text = 'Шаг 2'
                    self.load_widget.step_button_2.text = 'Шаг 3'
                else:
                    self.load_widget.console.message = info + 'Попробуйте ещё раз.'
                    self.load_widget.input.text = 'Введите номера выбранных колонок таблицы через запятую.'

            elif text == 'Шаг 3':
                names = self.load_widget.input.text.replace(' ', '').split(',')
                if len(names) + 1 == len(self.keeper['columns']):
                    self.keeper['columns'] = list(zip(self.keeper['columns'], ['id'] + names))
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
                    table_name = 'Catalog'
                    query = sql.get_data_query(table_name, self.keeper['columns'])
                    data = sql.make_response_query(save_dir_path, db_file_name, query)
                    new_table_name = 'new_catalog'
                    msg = ''
                    _, columns_names = zip(*self.keeper['columns'])
                    if sql.make_response_query(save_dir_path, db_file_name, sql.check_table(new_table_name)):
                        query, _ = sql.get_delete_query(new_table_name)
                        msg = sql.make_query(save_dir_path, db_file_name, query)
                    else:
                        query = sql.create_table(new_table_name, columns_names)
                        msg = sql.make_query(save_dir_path, db_file_name, query)
                    if not msg:
                        query, data = sql.get_insert_query(new_table_name, columns_names, data)
                        msg = sql.make_many_query(save_dir_path, db_file_name, query, data)
                    if not msg:
                        msg = ex.get_file_from_data(save_dir_path, file_name, data, columns_names)
                    if not msg:
                        msg = f'Файл {file_name} сохранен в папке {save_dir_path}.'
                    msg = msg
                    self.load_widget.console.message += f'\n{msg}'
                else:
                    self.console.message = f'Нет наименований колонок таблицы для выгрузки.' \
                                        f'\nВыполните шаги с 1 по 3.'

    def parser_press_step(self, text: str):
        """
        Step 1 - connecting modules, checking for useful functions in modules
        Step 2 - creating tables for product categories, parsing categories and writing to tables
            (if the table is already created, the old data will be deleted)
        Step 3 - creating a table to store the values of certain fields, which will be searched
            rows and removing them from the main table
        Step 4 - create a table for updating, create a folder with products images
        At each step each table is saved in file.
        :param text: step button name
        """
        missing = self.check_settings(['save_dir_path',
                                       'db_file_name',
                                       'update_file_name',
                                       'del_file_name',
                                       'columns',
                                       'functions_names',
                                       'category_site_file_name',
                                       'category_site_urls',
                                       'images_folder_name'])
        if missing:
            self.parser_widget.console.message = self.settings_report(missing)
        else:
            urls = self.store.get('category_site_urls')['urls']
            save_dir_path = self.store.get('save_dir_path')['path']
            db_file_name = self.store.get('db_file_name')['name']
            module_names = [pr.get_site_name(url) for url in urls]
            tables_names = ['new_catalog'] + module_names
            update_file_name = self.store.get('update_file_name')['name']
            del_file_name = self.store.get('del_file_name')['name']
            images_folder_name = self.store.get('images_folder_name')['name']
            columns_names= ['categories',
                            'categories_alias',
                            'article',
                            'article_alias']
            if text == 'Шаг 1':
                function_names = self.store.get('functions_names')['names']
                message = ''
                for m_name in module_names:
                    file_name = f'{m_name}.py'
                    # if text:
                    #     with open(os.path.join(save_dir_path, file_name), 'w') as f:
                    #         f.write(text)
                    #     self.parser_widget.console.message = f'Функции записаны в файл {file_name}.'

                    module = pr.import_source(os.path.join(save_dir_path, file_name), m_name)
                    if module is None:
                        message += f'Модуль из файла {file_name} не обнаружен.'
                        break
                    else:
                        missed_function = pr.missed_function(module, function_names)
                        message += f'Модуль из файла {file_name} загружен успешно.\n'
                        if missed_function:
                            message += f'\nДанные функции отсутствуют в модуле: {", ".join(missed_function)}'
                        else:
                            self.keeper[m_name] = module
                            self.parser_widget.step_button.text = 'Шаг 2'
                self.parser_widget.console.message = message

            if text == 'Шаг 2':
                msg = ''
                self.parser_widget.console.message = ''
                for i, m_name in enumerate(module_names):
                    table_name = f'{m_name}'
                    file_name = self.store.get('category_site_file_name')['name'].replace('{site}', m_name)
                    query = sql.create_table(table_name, columns_names)
                    msg = sql.make_query(save_dir_path, db_file_name, query)
                    if not msg:
                        query, _ = sql.get_delete_query(table_name)
                        msg = sql.make_query(save_dir_path, db_file_name, query)
                    if not msg:
                        driver = pr.get_driver()
                        categories = self.keeper[m_name].get_categories(driver, urls[i])
                        data = []
                        for name, href in categories:
                            start = [name, href]
                            rows = self.keeper[m_name].get_products(driver, href)
                            data += [start + list(row) for row in rows]
                        driver.close()
                        query, data = sql.get_insert_query(table_name, columns_names, data)
                        msg = sql.make_many_query(save_dir_path, db_file_name, query, data)
                    if not msg:
                        columns = list(zip(columns_names, columns_names))
                        query = sql.get_data_query(table_name, columns)
                        data = sql.make_response_query(save_dir_path, db_file_name, query)
                        msg = ex.get_file_from_data(save_dir_path, file_name, data, columns_names)
                    if not msg:
                        self.parser_widget.console.message += f'Файл {file_name} сохранен в папке {save_dir_path}.\n'
                    if msg:
                        self.parser_widget.console.message += msg
                        break
                if not msg:
                    self.parser_widget.step_button.text = 'Шаг 3'

            if text == 'Шаг 3':
                msg = ''
                if not sql.make_response_query(save_dir_path, db_file_name, sql.check_table('del_table')):
                    query = sql.create_table('del_table', ['id', 'article'])
                    msg = sql.make_query(save_dir_path, db_file_name, query)
                else:
                    query, _ = sql.get_delete_query('del_table')
                    msg = sql.make_query(save_dir_path, db_file_name, query)
                if not msg:
                    deleted_query = sql.deleted_data_query(tables_names)
                    deleted_data = sql.make_response_query(save_dir_path, db_file_name, deleted_query)
                    deleted_data = list(map(lambda x: [x[0]], deleted_data))
                    if deleted_data:
                        query, deleted_data = sql.get_insert_query('del_table', ['article'], deleted_data)
                        msg = sql.make_many_query(save_dir_path, db_file_name, query, deleted_data)
                        if not msg:
                            msg = ex.get_file_from_data(save_dir_path, del_file_name, deleted_data, ['article'])
                if not msg:
                    self.parser_widget.console.message = f'Файл {del_file_name} сохранен в папке {save_dir_path}.\n'
                    self.parser_widget.step_button.text = 'Шаг 4'
                else:
                    self.parser_widget.console.message = msg

            if text == 'Шаг 4':
                query = sql.update_data_query(tables_names)
                update_data = sql.make_response_query(save_dir_path, db_file_name, query)
                if not update_data:
                    self.parser_widget.console.message = 'Нет данных для обновления.'
                else:
                    images_dir_path = os.path.join(save_dir_path, images_folder_name)
                    _, cols_names = zip(*self.store.get('columns')['names'])
                    columns_names = list(cols_names) + ['image'] + [f'image_{str(i)}' for i in range(1, 13)]
                    if sql.make_response_query(save_dir_path, db_file_name, sql.check_table('update_table')):
                        query, _ = sql.get_delete_query('update_table')
                        msg = sql.make_query(save_dir_path, db_file_name, query)
                    else:
                        query = sql.create_table('update_table', columns_names)
                        msg = sql.make_query(save_dir_path, db_file_name, query)
                    update_table = []
                    if not msg:
                        update_dict = {pr.get_site_name(url): [] for url in urls}
                        for row in update_data:
                            update_dict[pr.get_site_name(row[1])].append(row)
                        driver = pr.get_driver()

                        if ex.del_dir_files(images_dir_path):
                            for k, v in update_dict.items():
                                for row in v:
                                    item_url = row[3]
                                    item_row = [row[0]]
                                    item_row += self.keeper[k].get_item_content(driver, item_url)
                                    item_images = self.keeper[k].get_item_images(driver, item_url)
                                    images_paths, file_names, values, fields_names = ex.get_image_fields(row[2], item_images)
                                    pr.get_images(images_dir_path, images_paths, file_names)
                                    item_row += values
                                    if len(columns_names) - 1 == len(item_row):
                                        update_table.append(item_row)

                        driver.close()
                    query, data = sql.get_insert_query('update_table', columns_names[1:], update_table)
                    msg = sql.make_many_query(save_dir_path, db_file_name, query, data)
                    if not msg:
                        msg = ex.get_file_from_data(save_dir_path, update_file_name, update_table, columns_names[1:])
                    if not msg:
                        self.parser_widget.console.message = f'Файл {update_file_name} сохранен в папке {save_dir_path}.'
                        self.parser_widget.step_button.text = 'Шаг 1'
                        query = sql.get_table_info('update_table')
                        data = sql.make_response_query(save_dir_path, db_file_name, query)
                        columns_names = list(map(lambda x: x[1], data))
                        self.handle_widget.message = 'Выберите колонку для редактирования и нажмите кнопку "Шаг 1":'
                        self.handle_widget.handler_scroll.items = columns_names[1:]
                    else:
                        self.parser_widget.console.message = msg

    def handle_press_step(self, text):
        missing = self.check_settings(['save_dir_path', 'db_file_name'])
        if missing:
            self.parser_widget.console.message = self.settings_report(missing)
        else:
            save_dir_path = self.store.get('save_dir_path')['path']
            db_file_name = self.store.get('db_file_name')['name']
            if text == 'Шаг 1':
                column_name = self.handle_widget.handler_scroll.value
                if column_name:
                    self.keeper['temporary_column_name'] = column_name
                    self.handle_widget.handler_scroll.items = [column_name]
                    self.handle_widget.message = f'Выбрана колонка "{column_name}".\n' \
                                                 f'Нажмите кнопку "Шаг 2" чтобы получить значения.'
                    self.handle_widget.step_button.text = 'Шаг 2'

            if text == 'Шаг 2':
                self.handle_widget.handler_scroll.items = []
                column_name = self.keeper['temporary_column_name']
                query = sql.get_data_query('update_table', ['ID', column_name])
                columns_values = sql.make_response_query(save_dir_path, db_file_name, query)
                self.handle_widget.message = f'В колонке {column_name} содержится {len(columns_values)} значений.\n' \
                                             f'После редактирования ячейки сохраните её значения.\n' \
                                             f'Для сохранения колонки в таблицу нажмите кнопку "Шаг 3"'
                self.keeper['temporary_column'] = {}
                for _id, value in columns_values:
                    self.keeper['temporary_column'][_id] = ([value, ''])
                    self.handle_widget.handler_scroll.add_edit_block(_id, value)
                    # print("   ", self.handle_widget.choose_value.height)

                self.handle_widget.step_button.text = 'Шаг 3'

            if text == 'Шаг 3':
                column_name = self.keeper['temporary_column_name']
                column = self.keeper['temporary_column']
                values = list(map(lambda item: (item[1][0] if not item[1][1] else item[1][1], item[0]), column.items()))
                query, data = sql.get_set_values_query('update_table', column_name, values)
                msg = sql.make_many_query(save_dir_path, db_file_name, query, data)
                if not msg:
                    self.handle_widget.handler_scroll.remove_edit_blocks()
                    query = sql.get_table_info('update_table')
                    data = sql.make_response_query(save_dir_path, db_file_name, query)
                    columns_names = list(map(lambda x: x[1], data))
                    self.handle_widget.message = 'Данные сохранены.\n' \
                                                 'Выберите колонку для редактирования и нажмите "Получить значения".'
                    self.handle_widget.handler_scroll.items = columns_names
                    self.handle_widget.step_button.text = 'Шаг 1'
                else:
                    print(msg)

    def upload_step(self):
        missing = self.check_settings(['columns', 'save_dir_path', 'db_file_name'])
        if missing:
            self.parser_widget.console.message = self.settings_report(missing)
        else:
            save_dir_path = self.store.get('save_dir_path')['path']
            db_file_name = self.store.get('db_file_name')['name']
            data = []
            img_fields_names = ['image'] + [f'image_{str(i)}' for i in range(1, 13)]
            columns = self.store.get('columns')['names']
            img_columns = [list(el) for el in zip(img_fields_names, img_fields_names)]
            columns += img_columns
            if sql.make_response_query(save_dir_path, db_file_name, sql.check_table('update_table')):
                query = sql.get_data_query('update_table', [el[::-1] for el in columns])
                data = sql.make_response_query(save_dir_path, db_file_name, query)
            if not data:
                self.upload_widget.console.message = f'Нет данных для загрузки.\n' \
                                                     f'Перейдите к операции "Обработка"'
            else:
                catalog_columns, _ = zip(*columns)
                query, data = sql.get_insert_query('catalog', catalog_columns, data)
                msg = sql.make_many_query(save_dir_path, db_file_name, query, data)
                if not msg:
                    self.upload_widget.console.message = f'Было успешно добавленно {len(data)} записей.'
                else:
                    self.upload_widget.console.message = f'Произошли следующие ошибки:\n{msg}'

    def delete_step(self):
        missing = self.check_settings(['save_dir_path', 'db_file_name'])
        if missing:
            self.parser_widget.console.message = self.settings_report(missing)
        else:
            save_dir_path = self.store.get('save_dir_path')['path']
            db_file_name = self.store.get('db_file_name')['name']
            data = []
            if sql.make_response_query(save_dir_path, db_file_name, sql.check_table('del_table')):
                query = sql.get_data_query('del_table', ['article'])
                data = sql.make_response_query(save_dir_path, db_file_name, query)
            if not data:
                self.upload_widget.console.message = f'Нет данных для удаления.\n' \
                                                  f'Перейдите к операции "Парсинг"'
            else:
                query, data = sql.get_delete_query('catalog', ['article'], data)
                msg = sql.make_many_query(save_dir_path, db_file_name, query, data)
                if not msg:
                    self.upload_widget.console.message = f'Было успешно удалено {len(data)} записей.'
                else:
                    self.upload_widget.console.message = 'Произошли следующие ошибки:'
                    self.upload_widget.console.message += '\n'.join(msg)


class UploaderApp(App):

    def build(self):
        return Uploader()


if __name__ == '__main__':
    if hasattr(sys, '_MEIPASS'):
        resource_add_path(os.path.join(sys._MEIPASS))

    ex.check_version(version='1.0.0')
    Window.size = (700, 700)
    UploaderApp().run()