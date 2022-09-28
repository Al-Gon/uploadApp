from kivy.uix.boxlayout import BoxLayout
from kivy.lang import Builder
from base_classes.config import Config
from base_classes.db import DB
from modules import excel_functions as ex, sql_functions as sql
import os

Builder.load_file('base_classes/kv/load_layout.kv')

class LoadLayout(BoxLayout):
    config = Config()
    keeper = {}

    def update(self):
        if self.config['columns']:
            self.keeper['columns'] = self.config['columns']
            self.console.message = 'Колонки и представления для выгрузки в файл:\n'
            self.console.message += '\n'.join(
                [f'{i}. {col[0]} "{col[1]}"' for i, col in enumerate(self.keeper['columns'])])
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
            title_fill_color = self.config['title_fill_color']
            title_font_color = self.config['title_font_color']
            styles = [title_fill_color, title_font_color]
            db = DB(os.path.join(save_dir_path, db_file_name))
            if text == 'Шаг 1':
                self.keeper['columns'] = db.tables['Catalog']
                self.console.message = 'В таблице определены следующие поля:\n'
                self.console.message += '\n'.join(
                    [f'{i + 1}. {col}' for i, col in enumerate(self.keeper['columns'][1:])])
                self.input.text = f'Введите номера выбранных полей таблицы через запятую.' \
                                  f'\nКолонка "id" будет добавлена по умолчанию.'
                self.step_button_2.text = 'Шаг 2'

            elif text == 'Шаг 2':
                numbers_ = self.input.text.split(',')
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
                    self.keeper['columns'] = [self.keeper['columns'][0]] + [self.keeper['columns'][num] for num in
                                                                            numbers]
                    self.console.message = 'Определены следующие колонки:\n'
                    self.console.message += '\n'.join(
                        [f'{i + 1}. {col}' for i, col in enumerate(self.keeper['columns'][1:])])
                    self.input.text = 'Введите представления имён выбранных колонок в файле через запятую.'
                    self.step_button_1.text = 'Шаг 2'
                    self.step_button_2.text = 'Шаг 3'
                else:
                    self.console.message = info + 'Попробуйте ещё раз.'
                    self.input.text = 'Введите номера выбранных колонок таблицы через запятую.'

            elif text == 'Шаг 3':
                names = self.input.text.replace(' ', '').split(',')
                if len(names) + 1 == len(self.keeper['columns']):
                    self.keeper['columns'] = list(zip(self.keeper['columns'], ['id'] + names))
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
                msg = db.error_msg
                if self.config['columns']:
                    self.keeper['columns'] = self.config['columns']
                    table_name = 'Catalog'
                    query = sql.get_data_query(table_name, self.keeper['columns'])
                    data = sql.make_response_query(db, query)
                    new_table_name = 'new_catalog'
                    _, columns_names = zip(*self.keeper['columns'])
                    if new_table_name in db.tables.keys():
                        query, _ = sql.get_delete_query(new_table_name)
                        sql.make_query_script(db, query)
                    else:
                        db.create_table(new_table_name, columns_names)
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