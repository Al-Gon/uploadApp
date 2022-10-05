import os
from kivy.uix.boxlayout import BoxLayout
from kivy.lang import Builder
from base_classes.config import Config
from base_classes.db import DB
from modules import excel_functions as ex, sql_functions as sql, request_functions as rq


Builder.load_file('base_classes/kv/upload_layout.kv')

class UploadLayout(BoxLayout):
    config = Config()

    def upload_step(self):
        missing = ex.check_values(self.config, ['columns',
                                                'save_dir_path',
                                                'db_file_name',
                                                'php_file_path'])
        if missing:
            self.console.message = ex.get_report(missing)
        else:
            save_dir_path = self.config['save_dir_path']
            db_file_name = self.config['db_file_name']
            php_file_path = self.config['php_file_path']
            table_name = self.config['table_name']
            db = DB(os.path.join(save_dir_path, db_file_name))
            data = []
            resp = ''
            img_fields_names = ['image'] + [f'image_{str(i)}' for i in range(1, 13)]
            columns = self.config['columns']
            img_columns = [list(el) for el in zip(img_fields_names, img_fields_names)]
            columns += [col for col in img_columns if col not in columns]
            if 'update_table_1' in db.tables.keys():
                query = sql.get_data_query('update_table_1', [el[::-1] for el in columns])
                data = sql.make_response_query(db, query)
            msg = db.error_msg
            if msg is None:
                if not data:
                    self.upload_widget.console.message = f'Нет данных для загрузки.\n' \
                                                         f'Перейдите к операции "Обработка"'
                else:
                    columns_, _ = zip(*columns)
                    columns_ = ','.join(columns_)
                    data_ = {'table_name': table_name,
                             'insert_data': {'columns': columns_,
                                             'rows': {}
                                             }
                             }
                    for i, row in enumerate(data):
                        data_['insert_data']['rows']['row ' + str(i)] = ','.join([f"'{el}'" for el in row])
                    resp = rq.get_response(php_file_path, data_)
                    if not resp:
                        msg = 'ошибка добавления данных на сайте.'
            if msg is None:
                self.console.message = f'Было успешно добавленно {resp} записей.'
            else:
                self.console.message = f'Произошли следующие ошибки:\n{msg}'


    def delete_step(self):
        missing = ex.check_values(self.config, ['save_dir_path',
                                                'db_file_name',
                                                'php_file_path'])
        if missing:
            self.console.message = ex.get_report(missing)
        else:
            save_dir_path = self.config['save_dir_path']
            db_file_name = self.config['db_file_name']
            php_file_path = self.config['php_file_path']
            table_name = self.config['table_name']
            db = DB(os.path.join(save_dir_path, db_file_name))
            data = []
            resp = ''
            if 'del_table' in db.tables.keys():
                query = sql.get_data_query('del_table', ['migxID', 'article'])
                data = sql.make_response_query(db, query)
            msg = db.error_msg
            if msg is None:
                if not data:
                    self.console.message = f'Нет данных для удаления.\n' \
                                           f'Перейдите к операции "Парсинг"'
                else:
                    ids, articles = zip(*data)
                    ids = ','.join(ids)
                    articles = ','.join(articles)
                    data_ = {'table_name': table_name,
                             'delete_data': {'ids': ids,
                                             'articles': articles
                                             }
                             }
                    resp = rq.get_response(php_file_path, data_)
                    if not resp:
                        msg = 'ошибка удаления данных на сайте.'
            if not msg:
                self.console.message = f'Было успешно удалено {resp} записей.'
            else:
                self.console.message = 'Произошли следующие ошибки:\n'
                self.console.message += msg