import sqlite3
import excel_functions as ex

def get_data_from_table(query: str):
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

def insert_query(table_: list, table_n: dict, title: list):
    db_file = 'site.db'
    queries = ex.get_insert_queries(table_, ex.get_query_dict(table_n, title))
    with sqlite3.connect(db_file, timeout=5) as conn:
        cursor = conn.cursor()
        for query in queries:
            try:
                cursor.execute(query)
            except sqlite3.DatabaseError as err:
                print("Error: ", err)
            else:
                conn.commit()

def get_file_from_data(folder_path: str, file_name: str, columns: list):
    part = ", ".join(f'{elem[0]} AS {elem[1]}' for elem in columns)
    data = get_data_from_table(f"""SELECT {part} FROM catalog""")
    return ex.get_file_from_table(folder_path, file_name, data, [elem[1] for elem in columns])

def get_table_columns():
    query = """PRAGMA table_info(Catalog);"""
    data = get_data_from_table(query)
    return list(map(lambda x: x[1], data))











