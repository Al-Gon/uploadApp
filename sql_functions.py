import sqlite3
import excel_functions as ex

def create_table(table_name: str, columns_: list) -> str:
    """
    Returns a string of query
    :param table_name: str
    :param columns_: list of tuples: field name, representation
    """
    columns = ', '.join([f'{col[0]} {col[1]}'for col in columns_])
    query = f"""CREATE TABLE IF NOT EXISTS {table_name}({columns})"""
    return query

def delete_data_from_table(table_name: str, del_data: list) -> list:
    """
    Returns a list of delete queries.
    :param table_name: string
    :param del_data: list of tuples: field, value
    """
    if not del_data:
        return [f"""DELETE FROM {table_name}"""]
    else:
        queries = []
        for data in del_data:
            f"""DELETE FROM {table_name} WHERE {del_data[0]}='{del_data[1]}'"""
        return queries


def check_table(table_name: str) -> str:
    return f"""SELECT name FROM sqlite_master WHERE type='table' AND name='{table_name}'"""

def make_response_query(query: str):
    db_file = 'site.db'
    response = []
    with sqlite3.connect(db_file, timeout=5) as conn:
        cursor = conn.cursor()
        try:
            cursor.execute(query)
            response = cursor.fetchall()
        except sqlite3.DatabaseError as err:
            print("Error: ", err)
        else:
            conn.commit()
    return response

def make_query(queries: list):
    db_file = 'site.db'
    error_msg = []
    with sqlite3.connect(db_file, timeout=5) as conn:
        cursor = conn.cursor()
        for query in queries:
            try:
                cursor.execute(query)
            except sqlite3.DatabaseError as err:
                error_msg.append(f'Error: {err}')
            else:
                conn.commit()
    return error_msg

def get_insert_queries(table_name: str, data: list, columns_names: list) -> list:
    """
    Creates a list of insert queries
    :param table_name: str
    :param data: list of raws
    :param columns_names: list
    :return: list
    """
    queries = []
    for raw in data:
        part_1 = ", ".join(columns_names)
        part_2 = "', '".join([str(el) for el in raw])
        queries.append(f"""INSERT INTO {table_name}({part_1}) VALUES ('{part_2}')""")

    return queries

def get_data_from_table(table_name: str, columns: list):
    """
    Returns list of data from table.
    :param table_name:
    :param columns: list of tuples (column name, representation)
    :return: list
    """
    part = ', '.join(f'{elem[0]} AS {elem[1]}' for elem in columns)
    print(f"""SELECT {part} FROM {table_name}""")
    data = make_response_query(f"""SELECT {part} FROM {table_name}""")
    return data

def update_data_query(tables: list) -> str:
    """
    Returns query string for getting data for update by field 'article'
    :param tables: list from two tables names
    :return: string
    """
    field = 'article'
    part_1 = f'SELECT * FROM {tables[1]} UNION SELECT * FROM {tables[2]}'
    part_2 = f'SELECT {field} FROM {tables[0]}'
    query = f"""SELECT * FROM ({part_1}) WHERE {field} NOT IN ({part_2})"""
    return query

def deleted_data_query(tables: list) -> str:
    """
    Returns query string for getting data for deleted by field 'article'
    :param tables: list from two tables names
    :return: string
    """
    # SELECT article FROM new_catalog WHERE article NOT IN (SELECT article FROM www_pharma_machines_com UNION SELECT article FROM www_pharma_maschinen_com)
    field = 'article'
    part_1 = f'SELECT {field} FROM {tables[1]} UNION SELECT {field} FROM {tables[2]}'
    query = f"""SELECT {field} FROM ({tables[0]}) WHERE {field} NOT IN ({part_1})"""
    return query

def get_table_columns():
    query = """PRAGMA table_info(Catalog)"""
    data = make_response_query(query)
    return list(map(lambda x: x[1], data))
