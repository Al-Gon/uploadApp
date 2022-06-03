import sqlite3

def create_table(table_name: str, columns_names: list) -> str:
    """
    Returns a string of query
    :param table_name: str
    :param columns_names: list of columns names
    """
    columns = ', '.join(f'{col} INTEGER PRIMARY KEY AUTOINCREMENT' if col == 'id' else f'{col} text'
                        for col in columns_names)
    query = f"""CREATE TABLE IF NOT EXISTS {table_name}({columns})"""
    return query

def get_delete_query(table_name: str, columns_names=None, data=None) -> tuple:
    """
    Returns a tuple: query string and list of data rows.
    :param table_name: str
    :param columns_names: list
    :param data: list of tuples, each of them must be the same length as list of columns names.
    :return: tuple
    """
    columns_names = columns_names or []
    data = data or []
    condition = ''
    if columns_names and len(columns_names) == len(max(data, key=len, default=[])):
        condition = ' WHERE ' + ' AND '.join([f'{col}=?' for col in columns_names])
    return f"""DELETE FROM {table_name}{condition}""", data

def check_table(table_name: str) -> str:
    return f"""SELECT name FROM sqlite_master WHERE type='table' AND name='{table_name}'"""

def make_response_query(querystring: str):
    """
    Executes a query throw executemany
    :param: querystring
    """
    db_file = 'site.db'
    con = None
    error_msg = []
    response = None
    try:
        con = sqlite3.connect(db_file)
        cursor = con.cursor()
        cursor.execute(querystring)
        response = cursor.fetchall()
        con.commit()
    except sqlite3.DatabaseError as err:
        if con:
            con.rollback()
        error_msg.append(f'Error: {err}')
    finally:
        if con:
            con.close()
    return response

def make_many_query(querystring: str, params: list):
    """
    Executes a query throw executemany
    :param: querystring
    :param: params list of values
    """
    db_file = 'site.db'
    con = None
    error_msg = []
    try:
        con = sqlite3.connect(db_file)
        cursor = con.cursor()
        cursor.executemany(querystring, params)
        con.commit()
    except sqlite3.DatabaseError as err:
        if con:
            con.rollback()
        error_msg.append(f'Error: {err}')
    finally:
        if con:
            con.close()
    return error_msg

def make_query(querystring: str):
    """
    Executes a query throw execute
    :param: querystring
    """
    db_file = 'site.db'
    con = None
    error_msg = []
    try:
        con = sqlite3.connect(db_file)
        cursor = con.cursor()
        cursor.execute(querystring)
        con.commit()
    except sqlite3.DatabaseError as err:
        if con:
            con.rollback()
        error_msg.append(f'Error: {err}')
    finally:
        if con:
            con.close()
    return error_msg

def get_insert_query(table_name: str, columns_names: list, data: list) -> tuple:
    """
    Returns a tuple: query string and list of data rows.
    :param table_name: str
    :param columns_names: list
    :param data: list of tuples, each of them must be the same length as list of columns names.
    :return: tuple
    """
    part_1 = ", ".join(columns_names)
    part_2 = ", ".join(['?'] * len(columns_names))
    query = f"""INSERT INTO {table_name}({part_1}) VALUES ({part_2})"""
    return query, data

def get_data_from_table(table_name: str, columns: list):
    """
    Returns list of data from table.
    :param table_name:
    :param columns: list of columns names or list of tuples (column name, representation)
    :return: list
    """
    part = ''
    if isinstance(columns[0], str):
        part = ', '.join(columns)
    else:
        part = ', '.join(f'{elem[0]} AS {elem[1]}' for elem in columns)
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

def get_set_values_query(table_name: str, column_name: str, data: list):
    """
    Returns query string for set columns values using the 'id' field
    :param: table_name: name of the table
    :param: column_name: name of the column
    :param: values: list of tuples: value, id
    """
    if len(max(data, key=len)) != 2:
        data = []
    return f"""UPDATE {table_name} SET {column_name}=? WHERE id=?""", data

def get_table_columns(table_name: str):
    """
    Returns names of tables columns
    :param: table_name
    """
    query = f"""PRAGMA table_info({table_name})"""
    data = make_response_query(query)
    return list(map(lambda x: x[1], data))
