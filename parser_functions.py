from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException, NoSuchAttributeException
import requests
from selenium.webdriver.chrome.options import Options
from fake_useragent import UserAgent
import importlib.util
import os
import json

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

def import_source(module_file_path, module_name):
    module_spec = importlib.util.spec_from_file_location(
        module_name, module_file_path
    )
    if module_spec is None:
        return None
    else:
        print('Module: {} can be imported!'.format(module_name))
        module = importlib.util.module_from_spec(module_spec)
        module_spec.loader.exec_module(module)
        return module

def missed_function(module, function_names: list) -> list:
    """Returns missed functions which have to be in module"""
    return [name for name in function_names if name not in module.__dict__.keys()]

def check_url(url: str):
    try:
        response = requests.get(url)
        return response.ok
    except(requests.RequestException, ValueError):
        return False

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
    driver = webdriver.Chrome(chrome_options=options)
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
