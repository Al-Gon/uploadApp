import requests
import time
from modules import sql_functions as sql, excel_functions as ex
from fake_useragent import UserAgent


def do_request(url, attempt=3, userdata=None):
    resp = None
    ua = UserAgent()
    user_agent = ua.random
    headers = {'user-agent': user_agent}
    try:
        if userdata is None:
            resp = requests.get(url, headers=headers,)
        else:
            resp = requests.post(url, json=userdata, headers=headers,)
    except requests.RequestException:
        if attempt:
            time.sleep(5)
            return do_request(url, attempt - 1, userdata)
    finally:
        return resp

def load_data_procedure(obj, params, transfer, set_use_thread):
    save_dir_path = params['save_dir_path']
    file_name = params['file_name']
    styles = params['styles']
    inner_id = params['inner_id']
    columns_names = params['columns_names']
    php_file_path = params['php_file_path']
    data_ = params['data_']
    db = params['db']

    msg = db.error_msg
    response = do_request(url=php_file_path, userdata=data_)
    if response is not None and response.ok:
        try:
            data = response.json()
            new_table_name = 'new_catalog'
            columns_names_ = [inner_id[1]] + list(columns_names)
            if new_table_name in db.tables.keys():
                query = sql.delete_table(new_table_name)
                sql.make_query(db, query)
            db.create_table(new_table_name, columns_names_)
        except Exception as e:
             msg = f'Ошибка в ответе: {e}.\n'    
        if msg is None:
            query, data = sql.get_insert_query(new_table_name, columns_names, data)
            sql.make_many_query(db, query, data)
        if msg is None:
            msg = ex.get_file_from_data(save_dir_path, file_name, data, columns_names, styles)
    else:
        msg = 'Ошибка запроса к базе данных на сайте.\n'

    result = (not bool(msg), msg, file_name, save_dir_path)

    transfer(obj, result)
    set_use_thread(obj)