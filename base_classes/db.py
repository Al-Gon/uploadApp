import sqlite3
import modules.sql_functions as sql
from base_classes.singleton import Singleton

class DB(Singleton):
    def __init__(self, db_path: str):
        self.db_path = db_path
        self.con = None
        self.tables = self._check_tables()
        self.error_msg = None

    def get_con(self):
        if self.con is None:
            return sqlite3.connect(self.db_path)
        else:
            self.error_msg = 'Не возможно установить связь с БД.'

    def close_con(self):
        if self.con is not None:
            self.con.close()
            self.con = None

    def _check_tables(self):
        querystring = sql.check_tables()
        response = sql.make_response_query(self, querystring)
        tables = {}
        if response:
            names = [res[0] for res in response]
            for name in names:
                querystring = sql.get_columns_names(name)
                res_ = sql.make_response_query(self, querystring)
                if res_:
                    columns_names = [res[0] for res in res_]
                    tables[name] = columns_names
        return tables

    def get_error_msg(self):
        msg, self.error_msg = self.error_msg, None
        return msg

    def create_table(self, table_name, columns_names):
        querystring = sql.create_table(table_name, columns_names)
        sql.make_query(self, querystring)
        if self.error_msg is None:
            self.tables[table_name] = columns_names