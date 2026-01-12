import os
import time
from kivy.uix.boxlayout import BoxLayout
from kivy.properties import ListProperty
from kivy.lang import Builder
from base_classes.config import Config
from base_classes.db import DB
from modules import excel_functions as ex, sql_functions as sql, request_functions as rq, thread_functions as th
from kivy.clock import mainthread

Builder.load_file('base_classes/kv/load_layout.kv')

class LoadLayout(BoxLayout):
    config = Config()
    keeper = {}
    use_thread = False
    results = ListProperty([])
    msg_template = ('При загрузке данных в базу данных произошла ошибка.\n',
                    'Загрузка данных в базу данных прошла успешно.\n',
                    'Файл {2} сохранен в папке {3}.',
                    'Ошибка : {0}')


    def update(self):
        if self.config['columns']:
            self.keeper['columns'] = self.config['columns']
            self.console.message = f'Колонки таблицы "{self.config["table_name"]}" ' \
                                   f'и представления для выгрузки в файл:\n'
            self.console.message += '\n'.join(
                [f'{i + 1}. {col[0]}  -  "{col[1]}"' for i, col in enumerate(self.keeper['columns'])])
            self.console.message += f'\nЕсли нужно выгрузить данные из данных колонок в файл нажмите "Шаг 4".' \
                                    f'\nЕсли нужно изменить колонки нажмите "Шаг 1" и выполните шаги с 1 по 3.\n'

    def on_results(self, instance, value):
        """A callback to track changes to property."""
        if self.results:
            result = self.results[-1]
            template_index = int(result[0])
            self.console.message += self.msg_template[template_index]

    @mainthread
    def set_message(self, message):
        """A callback for output new message in console."""
        self.input.text = message

    def output_procedure_result(self):
        errors = [res[1] for res in self.results if not res[0]]
        if not errors:
            result = self.results[0]
            self.console.message += self.msg_template[2].format(*result)
        else:
            message = ''.join([self.msg_template[3].format(err) for err in errors])
            self.console.message += message + 'Исправьте ошибки.'
        self.results = []

    def load_press_step(self, text):
        """
        Step 1 - selecting column numbers for main table in database.
        Step 2 - selecting columns names for main table in database.
        Step 3 - setting users columns names.
        Step 4 - create a main table in database and save it in file.
        :param text: step button name
        """
        missing = ex.check_values(self.config, ['save_dir_path',
                                                'db_file_name',
                                                'file_name',
                                                'title_fill_color',
                                                'title_font_color'])
        if missing:
            self.console.message = ex.get_report(missing)
        else:
            save_dir_path = self.config['save_dir_path']
            db_file_name = self.config['db_file_name']
            file_name = self.config['file_name']
            php_file_path = self.config['php_file_path']
            title_fill_color = self.config['title_fill_color']
            title_font_color = self.config['title_font_color']
            styles = [title_fill_color, title_font_color]
            table_name = self.config['table_name']
            inner_id = self.config['inner_id']
            outer_id = self.config['outer_id']
            db = DB(os.path.join(save_dir_path, db_file_name))
            if text == 'Шаг 1':
                data_ = {'table_name': table_name,
                         'get_columns': 'Field'}
                response = rq.do_request(url=php_file_path, userdata=data_)
                if response is not None and response.ok:
                    columns = response.json()
                    self.keeper['columns'] = columns[1:]
                    self.console.message = f'В таблице "{table_name}" определены следующие поля:\n'
                    self.console.message += '\n'.join(
                        [f'{i + 1}. {col}' for i, col in enumerate(self.keeper['columns'])])
                    self.input.text = f'Введите номера выбранных полей таблицы через запятую.'
                    self.step_button_2.text = 'Шаг 2'
                else:
                    self.console.message = 'Ошибка запроса к базе данных сайта.'

            elif text == 'Шаг 2':
                numbers_ = self.input.text.split(',')
                numbers = []
                info = ''
                for num in numbers_:
                    num = num.strip()
                    try:
                        num_ = int(num) - 1
                        if num_ not in list(range(len(self.keeper['columns']))):
                            info += f'Номера "{num}" нет в списке колонок.\n'
                        else:
                            numbers.append(num_)
                    except ValueError:
                        info += f'Значение "{num}" не является числом.\n'
                if len(numbers) == len(numbers_):
                    self.keeper['columns'] = [self.keeper['columns'][num] for num in numbers]
                    self.console.message = 'Определены следующие колонки:\n'
                    self.console.message += '\n'.join(
                        [f'{i + 1}. {col}' for i, col in enumerate(self.keeper['columns'])])
                    self.input.text = 'Введите представления имён выбранных колонок в файле через запятую.'
                    self.step_button_1.text = 'Шаг 2'
                    self.step_button_2.text = 'Шаг 3'
                else:
                    self.console.message = info + 'Попробуйте ещё раз.'
                    self.input.text = 'Введите номера выбранных колонок таблицы через запятую.'

            elif text == 'Шаг 3':
                names = self.input.text.replace(' ', '').split(',')
                if len(names) == len(self.keeper['columns']):
                    self.keeper['columns'] = list(zip(self.keeper['columns'], names))
                    self.console.message = 'Определены следующие колонки:\n'
                    m1, m2 = [max(map(len, col)) for col in zip(*self.keeper['columns'])]
                    temp = f'{{}}. {{:>{m1 + 2}}} -- {{:<{m2 + 2}}}'
                    self.console.message += '\n'.join(
                        [temp.format(i + 1, *col) for i, col in enumerate(self.keeper['columns'])])
                    self.console.message += f'\nНажмите кнопку "Шаг 4" чтобы выгрузить данные в файл.' \
                                            f'\nНажмите кнопку "Шаг 1" если хотите изменить выбранные колонки.'
                    self.input.text = ''
                    self.config.put('columns', self.keeper['columns'])
                    self.step_button_1.text = 'Шаг 1'
                    self.step_button_2.text = 'Шаг 4'
                else:
                    self.input.text = 'Количество выбранных имён не соответствует числу колонок. Попробуйте ещё раз.'

            elif text == 'Шаг 4':
                if self.config['columns']:
                    self.keeper['columns'] = [self.config['outer_id']] + self.keeper['columns']
                    catalog_columns_names, columns_names = zip(*self.keeper['columns'])
                    data_ = {'table_name': table_name,
                             'get_catalog': ','.join(catalog_columns_names)}
                    params = {'save_dir_path': save_dir_path,
                              'file_name': file_name,
                              'styles': styles,
                              'inner_id': inner_id,
                              'columns_names': columns_names,
                              'php_file_path': php_file_path,
                              'data_': data_,
                              'db': db}
                    messages = ('Начало загрузки данных.\n', 'Конец загрузки данных.\n')
                    th.threads_operation(self, rq.load_data_procedure, self.set_message, params, messages)
                else:
                    self.console.message = 'Нет наименований колонок таблицы для выгрузки.\nВыполните шаги с 1 по 3.'