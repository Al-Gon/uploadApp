from kivy.uix.boxlayout import BoxLayout
from kivy.lang import Builder
from base_classes.config import Config
from base_classes.db import DB
from modules import excel_functions as ex, sql_functions as sql
import os

Builder.load_file('base_classes/kv/upload_layout.kv')

class UploadLayout(BoxLayout):
    config = Config()

    def upload_step(self):
        missing = ex.check_values(self.config, ['columns', 'save_dir_path', 'db_file_name'])
        if missing:
            self.parser_widget.console.message = ex.get_report(missing)
        else:
            save_dir_path = self.config['save_dir_path']
            db_file_name = self.config['db_file_name']
            db = DB(os.path.join(save_dir_path, db_file_name))
            data = []
            img_fields_names = ['image'] + [f'image_{str(i)}' for i in range(1, 13)]
            columns = self.store.get('columns')['names']
            img_columns = [list(el) for el in zip(img_fields_names, img_fields_names)]
            columns += img_columns
            if 'update_table' in db.tables.keys():
                query = sql.get_data_query('update_table', [el[::-1] for el in columns])
                data = sql.make_response_query(db, query)
            msg = db.error_msg
            if msg is None:
                if not data:
                    self.upload_widget.console.message = f'Нет данных для загрузки.\n' \
                                                         f'Перейдите к операции "Обработка"'
                else:
                    catalog_columns, _ = zip(*columns)
                    query, data = sql.get_insert_query('catalog', catalog_columns, data)
                    sql.make_many_query(db, query, data)
            if msg is None:
                self.upload_widget.console.message = f'Было успешно добавленно {len(data)} записей.'
            else:
                self.upload_widget.console.message = f'Произошли следующие ошибки:\n{msg}'


    def delete_step(self):
        missing = ex.check_values(self.config, ['save_dir_path', 'db_file_name'])
        if missing:
            self.console.message = ex.get_report(missing)
        else:
            save_dir_path = self.config['save_dir_path']
            db_file_name = self.config['db_file_name']
            db = DB(os.path.join(save_dir_path, db_file_name))
            data = []
            if 'del_table' in db.tables.keys():
                query = sql.get_data_query('del_table', ['article'])
                data = sql.make_response_query(db, query)
            msg = db.error_msg
            if msg is None:
                if not data:
                    self.console.message = f'Нет данных для удаления.\n' \
                                                         f'Перейдите к операции "Парсинг"'
                else:
                    query, data = sql.get_delete_query('catalog', ['article'], data)
                    sql.make_many_query(db, query, data)
            if not msg:
                self.console.message = f'Было успешно удалено {len(data)} записей.'
            else:
                self.console.message = 'Произошли следующие ошибки:'
                self.console.message += '\n'.join(msg)