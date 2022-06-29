import requests
import os
import json
import sql_functions as sql
import excel_functions as ex
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
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

def check_url(url: str):
    try:
        response = requests.get(url)
    except(requests.RequestException, ValueError):
        return False
    else:
        return response.ok

def get_images(folder_path: str, images_paths: list, file_names: list):
    ua = UserAgent()
    for i, path in enumerate(images_paths):
        user_agent = ua.random
        headers = {'user-agent': user_agent}
        if path:
            try:
                response = requests.get(path, headers=headers)
                with open(os.path.join(folder_path, file_names[i]), 'wb') as f:
                    f.write(response.content)
            except(requests.RequestException, ValueError):
                print('ValueError')

def get_site_name(url: str) -> str:
    """Returns the name of the site from url without points"""
    return f'{url.lstrip("https://").split("/")[0].replace(".", "_").replace("-", "_")}'

def get_driver():
    options = Options()
    ua = UserAgent()
    user_agent = ua.random
    options.add_argument(f'user-agent={user_agent}')
    driver = Driver(chrome_options=options)
    return driver

def find_element(driver, by, way: str):
    try:
        element = driver.find_element(by, way)
        return element
    except NoSuchElementException:
        print(f'Element {way.split(" ")[-1]} not found')

def find_elements(driver, by, way: str):
    try:
        elements = driver.find_elements(by, way)
        return elements
    except NoSuchElementException:
        print(f'Elements {way.split(" ")[-1]} not found')

def check_procedure(params, transfer, set_use_thread):
    driver = get_driver()
    for key, value in params.items():
        hrefs = [key]
        for item in value:
            name_operation, m_name, operation, validator = item
            res = operation(driver, hrefs[0])
            flag, href = validator(res)
            if href:
                hrefs[0] = href
            transfer(('check_procedure', flag, name_operation, m_name, hrefs[0]))
            if not flag:
                break
    driver.close()
    set_use_thread()

def parsing_category_procedure(params, transfer, set_use_thread):
    save_dir_path = params['save_dir_path']
    db_file_name = params['db_file_name']
    columns_names = params['columns_names']
    styles = params['styles']

    for url, value in params['urls'].items():
        table_name, file_name, get_categories, accept_cookie, get_products = value
        query = sql.create_table(table_name, columns_names)
        msg = sql.make_query(save_dir_path, db_file_name, query)
        if not msg:
            query, _ = sql.get_delete_query(table_name)
            msg = sql.make_query_script(save_dir_path, db_file_name, query)
        if not msg:
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
            msg = sql.make_many_query(save_dir_path, db_file_name, query, data)
        if not msg:
            columns = list(zip(columns_names, columns_names))
            query = sql.get_data_query(table_name, columns)
            data = sql.make_response_query(save_dir_path, db_file_name, query)
            msg = ex.get_file_from_data(save_dir_path, file_name, data, columns_names, styles)
        if msg:
            break
        transfer(('parsing_category_procedure', not bool(msg), msg, file_name, save_dir_path))
    set_use_thread()