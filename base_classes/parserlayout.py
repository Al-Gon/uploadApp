import os
from kivy.uix.boxlayout import BoxLayout
from kivy.properties import StringProperty, NumericProperty, ListProperty
from kivy.clock import mainthread
from kivy.lang import Builder
from kivy.app import App
from base_classes.db import DB
from base_classes.config import Config
from modules import excel_functions as ex, parser_functions as pr, \
    validate_function as vl, sql_functions as sql, thread_functions as th

Builder.load_file('base_classes/kv/parser_layout.kv')


class ParserLayout(BoxLayout):
    config = Config()
    keeper = {}
    message = StringProperty('')
    grid_height = NumericProperty()
    use_thread = False
    results = ListProperty([])
    msg_templates = {'check_driver_procedure': ('При проверке драйвера произошла ошибка.\n',
                                                'Проверка драйвера прошла успешно.\n',
                                                'Шаг 3',
                                                'Проверка закончена. Нажмите кнопку "Шаг 3".',
                                                'Ошибка: {2}.'),

                     'check_procedure': ('Проверка функции {2} модуля {3}.py ошибка: {4}.\n',
                                         'Проверка функции {2} модуля {3}.py прошла успешно.\n',
                                         'Шаг 4',
                                         'Проверка закончена. Нажмите кнопку "Шаг 4".',
                                         'Модуль {3} метод "{2}" результат: {4}.\n'
                                         ),
                     'parsing_category_procedure': ('При работе над файлом {3} произошла ошибка: {2}.\n',
                                                    'Файл {3} успешно сохранен в папке {4}.\n',
                                                    'Шаг 5',
                                                    'Обработка закончена. Нажмите кнопку "Шаг 5".',
                                                    'При работе над файлом {3} произошла ошибка: {2}.\n'),
                     'parsing_item_procedure': ('При работе над файлом {3} произошла ошибка: {2}.\n',
                                                'Файл {3} успешно сохранен в папке {4}.\n',
                                                'Шаг 1',
                                                'Файл {3} успешно сохранен в папке {4}.\nОбработка закончена.',
                                                'При работе над файлом {3} произошла ошибка: {2}.\n')
                     }

    def on_results(self, instance, value):
        """A callback to track changes to property."""
        if self.results:
            result = self.results[-1]
            msg_template = self.msg_templates[result[0]]
            self.console.message = msg_template[int(result[1])].format(*result)

    def output_procedure_result(self, *args):
        msg_template = self.msg_templates[self.results[-1][0]]
        errors = [res for res in self.results if not res[1]]
        if not errors:
            result = self.results[0]
            self.step_button.text = msg_template[2]

            self.console.message += msg_template[3].format(*result)
            if args:
                app = App.get_running_app()
                app.root.handle_widget.update()
        else:
            message = '\n'.join([msg_template[4].format(*err) for err in errors])
            self.console.message = message + '\nИсправьте ошибки.'
        self.results = []

    @mainthread
    def set_message(self, message):
        """A callback for output new message."""
        self.message = message

    def parser_press_step(self, text: str):
        """
        Step 1 - connecting modules, checking for useful functions in modules
        Step 2 - validate webdriver
        Step 3 - validate useful functions in modules
        Step 4 - creating tables for product categories, parsing categories and writing to tables
            (if the table is already created, the old data will be deleted)
        Step 5 - creating a table to store the values of certain fields, which will be searched
            rows and removing them from the main table
        Step 6 - create a table for updating, create a folder with products images
        At each step each table is saved in file.
        :param text: step button name
        """
        missing = ex.check_values(self.config, ['save_dir_path',
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
            self.console.message = ex.get_report(missing)
        else:
            urls = self.config['category_site_urls']
            save_dir_path = self.config['save_dir_path']
            db_file_name = self.config['db_file_name']
            module_names = [pr.get_site_name(url) for url in urls]
            tables_names = ['new_catalog'] + module_names
            update_file_name = self.config['update_file_name']
            del_file_name = self.config['del_file_name']
            images_folder_name = self.config['images_folder_name']
            columns_names = ['categories',
                             'categories_alias',
                             'article',
                             'article_alias']
            title_fill_color = self.config['title_fill_color']
            title_font_color = self.config['title_font_color']

            styles = [title_fill_color, title_font_color]
            db = DB(os.path.join(save_dir_path, db_file_name))
            if text == 'Шаг 1':
                function_names = self.config['functions_names']
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
                            self.step_button.text = 'Шаг 2'
                self.console.message = message

            if text == 'Шаг 2':
                if not self.use_thread:
                    params = {}
                    self.console.message = 'Производиться проверка драйвера.\n'
                    messages = ('Начало проверки.\n', 'Конец проверки.\n')
                    th.threads_operation(self, pr.check_driver_procedure, self.set_message, params, messages)

            if text == 'Шаг 3':
                if not self.use_thread:
                    self.console.message = 'Производиться проверка.\n'
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
                    messages = ('Начало парсинга.\n', 'Конец парсинга.\n')
                    th.threads_operation(self, pr.check_procedure, self.set_message, params, messages)

            if text == 'Шаг 4':
                if not self.use_thread:
                    self.console.message = 'Производиться парсинг.\n'
                    params = {'save_dir_path': save_dir_path,
                              'columns_names': columns_names,
                              'styles': styles,
                              'urls': {},
                              'db': db
                              }
                    for i, m_name in enumerate(module_names):
                        table_name = f'{m_name}'
                        file_name = self.config['category_site_file_name'].replace('{site}', m_name)
                        params['urls'][urls[i]] = (table_name,
                                                   file_name,
                                                   self.keeper[m_name].get_categories,
                                                   self.keeper[m_name].accept_cookie,
                                                   self.keeper[m_name].get_products)
                    messages = ('Начало парсинга.\n', 'Конец парсинга.\n')
                    th.threads_operation(self, pr.parsing_category_procedure, self.set_message, params, messages)

            if text == 'Шаг 5':
                msg = db.error_msg
                if 'del_table' not in db.tables.keys():
                    db.create_table('del_table', ['id', 'migxID', 'article'])
                else:
                    query, _ = sql.get_delete_query('del_table')
                    sql.make_query_script(db, query)
                if msg is None:
                    deleted_query = sql.deleted_data_query(tables_names)
                    deleted_data = sql.make_response_query(db, deleted_query)
                    if deleted_data:
                        query, deleted_data = sql.get_insert_query('del_table', ['migxID', 'article'], deleted_data)
                        sql.make_many_query(db, query, deleted_data)
                    if msg is None:
                        msg = ex.get_file_from_data(save_dir_path, del_file_name,
                                                    deleted_data, ['migxID', 'article'], styles)
                if not msg:
                    self.console.message = f'Файл {del_file_name} сохранен в папке {save_dir_path}.\n'
                    self.step_button.text = 'Шаг 6'
                else:
                    self.console.message = msg

            if text == 'Шаг 6':
                if not self.use_thread:
                    self.console.message = 'Производиться парсинг.\n'
                    query = sql.update_data_query(tables_names)
                    update_data = sql.make_response_query(db, query)
                    if not update_data:
                        self.console.message = 'Нет данных для обновления.'
                    else:
                        images_dir_path = os.path.join(save_dir_path, images_folder_name)
                        _, columns_names_ = zip(*self.config['columns'])
                        images_fields = ['image'] + [f'image_{str(i)}' for i in range(1, 13)]
                        columns_names = list(columns_names_) + [field for field in images_fields
                                                                if field not in columns_names_]
                        params = {'save_dir_path': save_dir_path,
                                  'styles': styles,
                                  'update_file_name': update_file_name,
                                  'images_dir_path': images_dir_path,
                                  'columns_names': columns_names,
                                  'urls': urls,
                                  'update_data': update_data,
                                  'db': db}
                        for module in module_names:
                            params[module] = self.keeper[module]
                        # params['www_pharma_machines_com'] = self.keeper['www_pharma_machines_com']

                        messages = ('Начало парсинга.\n', 'Конец парсинга.\n')
                        th.threads_operation(self, pr.parsing_items_procedure, self.set_message, params, messages)
