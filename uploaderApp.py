import os
import sys
import threading
import time
import excel_functions as ex
import sql_functions as sql
import parser_functions as pr
import validate_function as vl
from handlerscroll import HandlerScroll
from colorspanel import ColorsPanel
from kivy.resources import resource_add_path
from kivy.uix.gridlayout import GridLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.scrollview import ScrollView
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.properties import StringProperty, ListProperty, NumericProperty
from kivy.storage.jsonstore import JsonStore
from kivy.clock import mainthread
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

class ItemLabel(Label):
    message = StringProperty('')

class ScrollLabel(ScrollView):
    message = StringProperty('')

class InputBlock(FloatLayout):
    input_string = StringProperty('')

class ChooseColorBlock(GridLayout):
    choose_color = StringProperty('')
    panels = ListProperty([])
    panel = None

    def on_panels(self, instance, panels):
        if panels:
            instance.add_widget(self.panels[0])
            instance.panel = self.panels[0]
        else:
            instance.remove_widget(self.panel)
            self.panel = None
        height = 0
        for child in self.children:
            height += child.height
        self.height = height + 10

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

class ParserLayout(BoxLayout):
    message = StringProperty('')
    grid_height = NumericProperty()
    use_thread = False
    results = ListProperty([])
    msg_templates = {'check_procedure': ('Проверка функции {2} модуля {3}.py ошибка: {4}.\n',
                                         'Проверка функции {2} модуля {3}.py прошла успешно.\n',
                                         'Шаг 3',
                                         'Проверка закончена. Нажмите кнопку "Шаг 3".',
                                         'Модуль {err[3]} метод "{err[2]}" результат: {err[4]}.\n'
                                         ),
                     'parsing_category_procedure': ('При работе над файлом {3} произошла ошибка: {2}.\n',
                                                    'Файл {3} успешно сохранен в папке {4}.\n',
                                                    'Шаг 4',
                                                    'Обработка закончена. Нажмите кнопку "Шаг 4".',
                                                    'При работе над файлом {3} произошла ошибка: {2}.\n'),
                     'parsing_item_procedure': ('При работе над файлом {3} произошла ошибка: {2}.\n',
                                                'Файл {3} успешно сохранен в папке {4}.\n',
                                                'Шаг 1',
                                                'Обработка закончена.',
                                                'При работе над файлом {3} произошла ошибка: {2}.\n')
                     }

    def threads_operation(self, procedure, params: dict, messages: tuple):
        """
        Starts two new threads. First one for graphics, second one for validation parsing functions process.
        :param procedure - name of method
        :param params - a dictionary of elements of the following type
        [url](name_operation, module_name, operation, validator)
        :param messages - start and end messages for threads.
        """
        if not self.use_thread:
            self.use_thread = True
            t1 = threading.Thread(target=self.get_message, args=(messages, ), daemon=True)
            t2 = threading.Thread(target=procedure,
                                  args=(params, self.transfer, self.set_use_thread))
            t1.start()
            t2.start()

    def on_results(self, instance, value):
        """A callback to track changes to property."""
        if self.results:
            result = self.results[-1]
            msg_template = self.msg_templates[result[0]]
            self.console.message = msg_template[int(result[1])].format(*result)

    @mainthread
    def transfer(self, result: tuple):
        """A callback for transfer result."""
        self.results.append(result)

    @mainthread
    def set_use_thread(self, *args):
        """A callback for catching the finishing of validation process."""
        self.use_thread = False
        time.sleep(.5)
        msg_template = self.msg_templates[self.results[-1][0]]
        errors = [res for res in self.results if not res[1]]
        if not errors:
            self.step_button.text = msg_template[2]
            self.console.message = msg_template[3]
            if args:
                app = App.get_running_app()
                app.root.update_handle_widget()
        else:
            message = '\n'.join([msg_template[4].format(*err) for err in errors])
            self.console.message = message + '\nИсправьте ошибки.'
        self.results = []

    def get_message(self, messages: tuple):
        """
        This function use for graphics representation of validation process.
        :param messages - start and end messages for threads.
        """
        counter = 0
        strip = ["     "] * 10
        use_thread = True
        self.set_message(messages[0])
        while use_thread:
            time.sleep(.5)
            index = counter % 10
            strip[index] = " *** "
            self.set_message(''.join(strip))
            strip[index] = "     "
            counter += 1
            use_thread = self.use_thread
        self.set_message(messages[1])

    @mainthread
    def set_message(self, message):
        """A callback for output new message."""
        self.message = message


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
                        if hasattr(obj, 'input'):
                            obj.input.text = value
                        elif hasattr(obj, 'choose_color'):
                            obj.choose_color = value
                    if isinstance(value, list):
                        obj.input.text = ', '.join(value)

        self.settings_widget.grid_height = self.grid_height(self.settings_widget.grid)

        if len(self.store.get('columns')['names']):
            self.keeper['columns'] = self.store.get('columns')['names']
            self.load_widget.console.message = 'Колонки и представления для выгрузки в файл:\n'
            self.load_widget.console.message += '\n'.join([f'{i}. {col[0]} "{col[1]}"' for i, col in enumerate(self.keeper['columns'])])
            self.load_widget.console.message += f'\nЕсли нужно выгрузить данные из данных колонок в файл нажмите "Шаг 4".'\
                                                f'\nЕсли нужно изменить колонки нажмите "Шаг 1" и выполните шаги с 1 по 3.'

        self.update_handle_widget()

    def update_handle_widget(self):
        save_dir_path = self.store.get('save_dir_path')['path']
        db_file_name = self.store.get('db_file_name')['name']
        if save_dir_path and db_file_name:
            if sql.make_response_query(save_dir_path, db_file_name, sql.check_table('update_table')):
                query = sql.get_table_info('update_table')
                data = sql.make_response_query(save_dir_path, db_file_name, query)
                columns_names = list(map(lambda x: x[1], data))
                self.handle_widget.message = 'Выберите колонку для редактирования и нажмите кнопку "Шаг 1":'
                self.handle_widget.handler_scroll.items = columns_names[1:]

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

    def set_color(self, obj, name):
        if not obj.panels:
            panel = ColorsPanel()
            obj.panels.append(panel)
        else:
            self.store.put(name, color=obj.choose_color)
            obj.panels = []
        self.settings_widget.grid_height = self.grid_height(self.settings_widget.grid)

    def get_color(self, name):
        if name == 'title_fill_color':
            self.set_color(self.settings_widget.title_fill_color, name)
        if name == 'title_font_color':
            self.set_color(self.settings_widget.title_font_color, name)

    def load_press_step(self, text):
        """
        Step 1 - selecting column numbers for main table in database.
        Step 2 - selecting columns names for main table in database.
        Step 3 - setting users columns names.
        Step 4 - create a main table in database and save it in file.
        :param text: step button name
        """
        missing = self.check_settings(['save_dir_path',
                                       'db_file_name',
                                       'file_name',
                                       'title_fill_color',
                                       'title_font_color'])
        if missing:
            self.load_widget.console.message = self.settings_report(missing)
        else:
            save_dir_path = self.store.get('save_dir_path')['path']
            db_file_name = self.store.get('db_file_name')['name']
            file_name = self.store.get('file_name')['name']
            title_fill_color = self.store.get('title_fill_color')['color']
            title_font_color = self.store.get('title_font_color')['color']
            styles = [title_fill_color, title_font_color]

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
                    _, columns_names = zip(*self.keeper['columns'])
                    if sql.make_response_query(save_dir_path, db_file_name, sql.check_table(new_table_name)):
                        query, _ = sql.get_delete_query(new_table_name)
                        msg = sql.make_query_script(save_dir_path, db_file_name, query)
                    else:
                        query = sql.create_table(new_table_name, columns_names)
                        msg = sql.make_query(save_dir_path, db_file_name, query)
                    if not msg:
                        query, data = sql.get_insert_query(new_table_name, columns_names, data)
                        msg = sql.make_many_query(save_dir_path, db_file_name, query, data)
                    if not msg:
                        msg = ex.get_file_from_data(save_dir_path, file_name, data, columns_names, styles)
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
        Step 2 - validate useful functions in modules
        Step 3 - creating tables for product categories, parsing categories and writing to tables
            (if the table is already created, the old data will be deleted)
        Step 4 - creating a table to store the values of certain fields, which will be searched
            rows and removing them from the main table
        Step 5 - create a table for updating, create a folder with products images
        At each step each table is saved in file.
        :param text: step button name
        """
        missing = self.check_settings(['save_dir_path',
                                       'db_file_name',
                                       'update_file_name',
                                       'del_file_name',
                                       'title_fill_color',
                                       'title_font_color',
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
            columns_names = ['categories',
                             'categories_alias',
                             'article',
                             'article_alias']
            title_fill_color = self.store.get('title_fill_color')['color']
            title_font_color = self.store.get('title_font_color')['color']
            styles = [title_fill_color, title_font_color]
            if text == 'Шаг 1':
                function_names = self.store.get('functions_names')['names']
                message = ''
                for m_name in module_names:
                    file_name = f'{m_name}.py'
                    # if text:
                    #     with open(os.path.join(save_dir_path, file_name), 'w') as f:
                    #         f.write(text)
                    #     self.parser_widget.console.message = f'Функции записаны в файл {file_name}.'

                    module = vl.import_source(os.path.join(save_dir_path, file_name), m_name)
                    if module is None:
                        message += f'Модуль из файла {file_name} не обнаружен.'
                        break
                    else:
                        missed_function = vl.missed_function(module, function_names)
                        message += f'Модуль из файла {file_name} загружен успешно.\n'
                        if missed_function:
                            message += f'\nДанные функции отсутствуют в модуле: {", ".join(missed_function)}'
                        else:
                            self.keeper[m_name] = module
                            self.parser_widget.step_button.text = 'Шаг 4'
                self.parser_widget.console.message = message

            if text == 'Шаг 2':
                if not self.parser_widget.use_thread:
                    self.parser_widget.console.message = 'Производиться проверка.\n'
                    params = {}
                    for url in urls:
                        params[url] = []
                        m_name = pr.get_site_name(url)
                        params[url].append(
                            ('get_categories', m_name, self.keeper[m_name].get_categories, vl.check_get_prod_cat))
                        params[url].append(
                            ('get_products', m_name, self.keeper[m_name].get_products, vl.check_get_prod_cat))
                        params[url].append(
                            ('get_item_images', m_name, self.keeper[m_name].get_item_images, vl.check_get_images))
                        params[url].append(
                            ('get_item_content', m_name, self.keeper[m_name].get_item_content, vl.check_get_item))
                    messages = ['Начало проверки.\n', 'Конец проверки.\n']
                    self.parser_widget.threads_operation(pr.check_procedure, params, messages)

            if text == 'Шаг 3':
                if not self.parser_widget.use_thread:
                    self.parser_widget.console.message = 'Производиться парсинг.\n'
                    params = {'save_dir_path': save_dir_path,
                              'db_file_name': db_file_name,
                              'columns_names': columns_names,
                              'styles': styles,
                              'urls': {}
                              }
                    for i, m_name in enumerate(module_names):
                        table_name = f'{m_name}'
                        file_name = self.store.get('category_site_file_name')['name'].replace('{site}', m_name)
                        params['urls'][urls[i]] = (table_name,
                                                   file_name,
                                                   self.keeper[m_name].get_categories,
                                                   self.keeper[m_name].accept_cookie,
                                                   self.keeper[m_name].get_products)
                    messages = ['Начало парсинга.\n', 'Конец парсинга.\n']
                    self.parser_widget.threads_operation(pr.parsing_category_procedure, params, messages)

            if text == 'Шаг 4':
                if not sql.make_response_query(save_dir_path, db_file_name, sql.check_table('del_table')):
                    query = sql.create_table('del_table', ['id', 'article'])
                    msg = sql.make_query(save_dir_path, db_file_name, query)
                else:
                    query, _ = sql.get_delete_query('del_table')
                    msg = sql.make_query_script(save_dir_path, db_file_name, query)
                if not msg:
                    deleted_query = sql.deleted_data_query(tables_names)
                    deleted_data = sql.make_response_query(save_dir_path, db_file_name, deleted_query)
                    deleted_data = list(map(lambda x: [x[0]], deleted_data))
                    if deleted_data:
                        query, deleted_data = sql.get_insert_query('del_table', ['article'], deleted_data)
                        msg = sql.make_many_query(save_dir_path, db_file_name, query, deleted_data)
                        if not msg:
                            msg = ex.get_file_from_data(save_dir_path, del_file_name,
                                                        deleted_data, ['article'], styles)
                if not msg:
                    self.parser_widget.console.message = f'Файл {del_file_name} сохранен в папке {save_dir_path}.\n'
                    self.parser_widget.step_button.text = 'Шаг 5'
                else:
                    self.parser_widget.console.message = msg

            if text == 'Шаг 5':
                if not self.parser_widget.use_thread:
                    self.parser_widget.console.message = 'Производиться парсинг.\n'
                    query = sql.update_data_query(tables_names)
                    update_data = sql.make_response_query(save_dir_path, db_file_name, query)
                    if not update_data:
                        self.parser_widget.console.message = 'Нет данных для обновления.'
                    else:
                        images_dir_path = os.path.join(save_dir_path, images_folder_name)
                        _, cols_names = zip(*self.store.get('columns')['names'])
                        columns_names = list(cols_names) + ['image'] + [f'image_{str(i)}' for i in range(1, 13)]
                        params = {'save_dir_path': save_dir_path,
                                  'db_file_name': db_file_name,
                                  'styles': styles,
                                  'update_file_name': update_file_name,
                                  'images_dir_path': images_dir_path,
                                  'columns_names': columns_names,
                                  'urls': urls,
                                  'update_data': update_data}
                        for module in module_names:
                            params[module] = self.keeper[module]
                        messages = ['Начало парсинга.\n', 'Конец парсинга.\n']
                        self.parser_widget.threads_operation(pr.parsing_items_procedure, params, messages)

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