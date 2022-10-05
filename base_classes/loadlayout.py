from kivy.uix.boxlayout import BoxLayout
from kivy.lang import Builder
from base_classes.config import Config
from base_classes.db import DB
from modules import excel_functions as ex, sql_functions as sql, request_functions as rq
import os

Builder.load_file('base_classes/kv/load_layout.kv')

class LoadLayout(BoxLayout):
    config = Config()
    keeper = {}

    def update(self):
        if self.config['columns']:
            self.keeper['columns'] = [self.config['outer_id']] + self.config['columns']
            self.console.message = f'Колонки таблицы "{self.config["table_name"]}" ' \
                                   f'и представления для выгрузки в файл:\n'
            self.console.message += '\n'.join(
                [f'{i + 1}. {col[0]}  -  "{col[1]}"' for i, col in enumerate(self.keeper['columns'])])
            self.console.message += f'\nЕсли нужно выгрузить данные из данных колонок в файл нажмите "Шаг 4".' \
                                    f'\nЕсли нужно изменить колонки нажмите "Шаг 1" и выполните шаги с 1 по 3.'

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
                self.keeper['columns'] = rq.get_response(php_file_path, data_, 'json')
                self.console.message = f'В таблице "{table_name}" определены следующие поля:\n'
                self.console.message += '\n'.join(
                    [f'{i + 1}. {col}' for i, col in enumerate(self.keeper['columns'][1:])])
                self.input.text = f'Введите номера выбранных полей таблицы через запятую.'
                self.step_button_2.text = 'Шаг 2'

            elif text == 'Шаг 2':
                numbers_ = self.input.text.split(',')
                numbers = []
                info = ''
                for num in numbers_:
                    num = num.strip()
                    try:
                        num = int(num)
                        if num not in list(range(len(self.keeper['columns']))):
                            info += f'Номера "{num + 1}" нет в списке колонок.\n'
                        else:
                            numbers.append(num)
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
                    columns = [tuple(outer_id)] + self.keeper['columns']
                    self.console.message = 'Определены следующие колонки:\n'
                    m1, m2 = [max(map(len, col)) for col in zip(*columns)]
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
                msg = db.error_msg
                if self.config['columns']:
                    catalog_columns_names, columns_names = zip(*self.keeper['columns'])
                    data_ = {'table_name': table_name,
                             'get_catalog': ','.join(catalog_columns_names)}
                    data = rq.get_response(php_file_path, data_, 'json')
                    new_table_name = 'new_catalog'
                    columns_names_ = [inner_id[1]] + list(columns_names)
                    if new_table_name in db.tables.keys():
                        query = sql.delete_table(new_table_name)
                        sql.make_query(db, query)
                    db.create_table(new_table_name, columns_names_)
                    if msg is None:
                        query, data = sql.get_insert_query(new_table_name, columns_names, data)
                        sql.make_many_query(db, query, data)
                    if msg is None:
                        msg = ex.get_file_from_data(save_dir_path, file_name, data, columns_names, styles)
                    if not msg:
                        msg = f'Файл {file_name} сохранен в папке {save_dir_path}.'
                    self.console.message += f'\n{msg}'
                else:
                    self.console.message = f'Нет наименований колонок таблицы для выгрузки.\nВыполните шаги с 1 по 3.'