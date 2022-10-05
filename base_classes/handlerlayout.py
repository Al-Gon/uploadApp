import os
from kivy.uix.boxlayout import BoxLayout
from kivy.properties import NumericProperty, StringProperty
from kivy.lang import Builder
from base_classes.handlerscroll import HandlerScroll
from base_classes.config import Config
from base_classes.db import DB
from modules import excel_functions as ex, sql_functions as sql

Builder.load_file('base_classes/kv/handle_layout.kv')

class HandleLayout(BoxLayout):
    config = Config()
    keeper = {}
    message = StringProperty("Консоль")

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.settings_widget = NumericProperty()
        self.handler_scroll = HandlerScroll(size_hint=(1, None))
        self.scroll.add_widget(self.handler_scroll)
        self.handler_scroll.keeper = self.keeper

    def update(self):
        save_dir_path = self.config['save_dir_path']
        db_file_name = self.config['db_file_name']

        if save_dir_path and db_file_name:
            db = DB(os.path.join(save_dir_path, db_file_name))
            if 'update_table' in db.tables.keys():
                self.message = 'Выберите колонку для редактирования и нажмите кнопку "Шаг 1":'
                self.handler_scroll.items = db.tables['update_table'][1:]

    def handle_press_step(self, text):
        missing = ex.check_values(self.config, ['save_dir_path', 'db_file_name'])
        if missing:
            self.console.message = ex.get_report(missing)
        else:
            save_dir_path = self.config['save_dir_path']
            db_file_name = self.config['db_file_name']

            db = DB(os.path.join(save_dir_path, db_file_name))
            if text == 'Шаг 1':
                column_name = self.handler_scroll.value
                if column_name:
                    self.keeper['temporary_column_name'] = column_name
                    self.handler_scroll.items = [column_name]
                    self.message = f'Выбрана колонка "{column_name}".\n' \
                                   f'Нажмите кнопку "Шаг 2" чтобы получить значения.'
                    self.step_button.text = 'Шаг 2'

            if text == 'Шаг 2':
                self.handler_scroll.items = []
                column_name = self.keeper['temporary_column_name']
                query = sql.get_data_query('update_table', ['ID', column_name])
                columns_values = sql.make_response_query(db, query)
                self.message = f'В колонке {column_name} содержится {len(columns_values)} значений.\n' \
                               f'После редактирования ячейки сохраните её значения.\n' \
                               f'Для сохранения колонки в таблицу нажмите кнопку "Шаг 3"'
                self.keeper['temporary_column'] = {}
                for _id, value in columns_values:
                    self.keeper['temporary_column'][_id] = ([value, ''])
                    self.handler_scroll.add_edit_block(column_name, _id, value)
                    # print("   ", self.handle_widget.choose_value.height)
                print(self.keeper['temporary_column'])
                self.step_button.text = 'Шаг 3'

            if text == 'Шаг 3':
                column_name = self.keeper['temporary_column_name']
                column = self.keeper['temporary_column']
                values = list(map(lambda item: (item[1][0] if not item[1][1] else item[1][1], item[0]), column.items()))
                query, data = sql.get_set_values_query('update_table', column_name, values)
                sql.make_many_query(db, query, data)
                msg = db.error_msg
                if msg is None:
                    self.handler_scroll.remove_edit_blocks()
                    query = sql.get_table_info('update_table')
                    data = sql.make_response_query(db, query)
                    columns_names = list(map(lambda x: x[1], data))
                    self.message = 'Данные сохранены.\n' \
                                   'Выберите колонку для редактирования и нажмите "Получить значения".'
                    self.handler_scroll.items = columns_names[1:]
                    self.step_button.text = 'Шаг 1'
                else:
                    print(msg)