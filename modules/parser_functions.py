import requests
import os
import json
import chromedriver_autoinstaller
from modules import sql_functions as sql
from modules import excel_functions as ex
from modules import request_functions as rq
from selenium import webdriver
from selenium.common.exceptions import SessionNotCreatedException
from selenium.common.exceptions import WebDriverException
from selenium.webdriver.chrome.options import Options
from fake_useragent import UserAgent


class Driver(webdriver.Chrome):
    cookie = False
    pass

def get_translation(text: str):
    url = "https://translated-mymemory---translation-memory.p.rapidapi.com/api/get"
    querystring = {"q": text, "langpair": "en|ru", "de": "a@b.c", "onlyprivate": "0", "mt": "1"}
    headers = {
        "X-RapidAPI-Host": "translated-mymemory---translation-memory.p.rapidapi.com",
        "X-RapidAPI-Key": "5bf8090618msheed2f30fd311833p146a35jsn5a89ecd1d58f"
    }
    response = requests.request("GET", url, headers=headers, params=querystring)
    data = json.loads(response.text)
    return data['responseData']['translatedText']

def get_images(folder_path: str, images_paths: list, file_names: list):
    for i, path in enumerate(images_paths):
        response = rq.do_request(url=path)
        if response is not None and response.ok:
            with open(os.path.join(folder_path, file_names[i]), 'wb') as f:
                f.write(response.content)

def get_site_name(url: str) -> str:
    """Returns the name of the site from url without points"""
    return f'{url.lstrip("https://").split("/")[0].replace(".", "_").replace("-", "_")}'

def get_driver():
    options = Options()
    ua = UserAgent()
    user_agent = ua.random
    options.add_argument("--start-maximized")
    options.add_argument(f'user-agent={user_agent}')
    options.add_experimental_option("useAutomationExtension", False)
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    chromedriver_autoinstaller.install(path='webdriver/')
    version = chromedriver_autoinstaller.get_chrome_version().split('.', 1)[0]
    path = f'webdriver/{version}/chromedriver.exe'
    
    driver = Driver(executable_path=path, 
                    chrome_options=options)
    return driver

def check_driver_procedure(obj, params, transfer, set_use_thread):
    msg = None
    try:
        driver = get_driver()
        driver.close()
    except (SessionNotCreatedException, WebDriverException) as e:
        msg = e.msg
    transfer(obj, ('check_driver_procedure', not bool(msg), msg, '', ''))
    set_use_thread(obj)

def check_procedure(obj, params, transfer, set_use_thread):
    driver = get_driver()
    for key, value in params.items():
        hrefs = [key]
        for item in value:
            name_operation, m_name, operation, validator = item
            res = operation(driver, hrefs[0])
            flag, href = validator(res)
            if href:
                hrefs[0] = href
            transfer(obj, ('check_procedure', flag, name_operation, m_name, hrefs[0]))
            if not flag:
                break
    driver.close()
    set_use_thread(obj)

def parsing_category_procedure(obj, params, transfer, set_use_thread):
    save_dir_path = params['save_dir_path']
    columns_names = params['columns_names']
    styles = params['styles']
    db = params['db']

    for url, value in params['urls'].items():
        msg = db.error_msg
        table_name, file_name, get_categories, accept_cookie, get_products = value
        db.create_table(table_name, columns_names)
        if msg is None:
            query, _ = sql.get_delete_query(table_name)
            sql.make_query_script(db, query)
        if msg is None:
            driver = get_driver()
            categories = get_categories(driver, url)
            data = []
            for name, href in categories:
                if not driver.cookie:
                    accept_cookie(driver, href)
                start = [name, href]
                rows = get_products(driver, href)
                data += [start + list(row) for row in rows]
            driver.close()
            query, data = sql.get_insert_query(table_name, columns_names, data)
            sql.make_many_query(db, query, data)
        if msg is None:
            columns = list(zip(columns_names, columns_names))
            query = sql.get_data_query(table_name, columns)
            data = sql.make_response_query(db, query)
            msg = ex.get_file_from_data(save_dir_path, file_name, data, columns_names, styles)
        else:
            break
        transfer(obj, ('parsing_category_procedure', not bool(msg), msg, file_name, save_dir_path))
    set_use_thread(obj)

def parsing_items_procedure(obj, params, transfer, set_use_thread):
    save_dir_path = params['save_dir_path']
    styles = params['styles']
    update_file_name = params['update_file_name']
    images_dir_path = params['images_dir_path']
    columns_names = params['columns_names']
    urls = params['urls']
    update_data = params['update_data']
    db = params['db']

    msg = db.error_msg
    if 'update_table' in db.tables.keys():
        query, _ = sql.get_delete_query('update_table')
        sql.make_query_script(db, query)
    else:
        db.create_table('update_table', columns_names)

    update_table = []
    if msg is None:
        update_dict = {get_site_name(url): [] for url in urls}
        for row in update_data:
            update_dict[get_site_name(row[1])].append(row)

        if ex.del_dir_files(images_dir_path):
            for k, v in update_dict.items():
                driver = get_driver()
                for row in v:
                    item_url = row[3]
                    item_row = [row[0]]
                    if not driver.cookie:
                        params[k].accept_cookie(driver, item_url)
                    item_row += params[k].get_item_content(driver, item_url)
                    item_images = params[k].get_item_images(driver, item_url)
                    images_paths, file_names, values, fields_names = ex.get_image_fields(row[2], item_images)
                    get_images(images_dir_path, images_paths, file_names)
                    item_row += values
                    if len(columns_names) == len(item_row):
                        update_table.append(item_row)
                driver.close()
    query, data = sql.get_insert_query('update_table', columns_names, update_table)
    msg = sql.make_many_query(db, query, data)
    if msg is None:
        msg = ex.get_file_from_data(save_dir_path, update_file_name,
                                    update_table, columns_names, styles)

    transfer(obj, ('parsing_item_procedure', not bool(msg), msg, update_file_name, save_dir_path))
    set_use_thread(obj, True)
    # if not msg:
    #     self.parser_widget.console.message = f'Файл {update_file_name} сохранен в папке {save_dir_path}.'
    #     self.parser_widget.step_button.text = 'Шаг 1'
    #     query = sql.get_table_info('update_table')
    #     data = sql.make_response_query(save_dir_path, db_file_name, query)
    #     columns_names = list(map(lambda x: x[1], data))
    #     self.handle_widget.message = 'Выберите колонку для редактирования и нажмите кнопку "Шаг 1":'
    #     self.handle_widget.handler_scroll.items = columns_names[1:]
    # else:
    #     self.parser_widget.console.message = msg