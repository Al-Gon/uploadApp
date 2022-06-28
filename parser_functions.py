from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
import requests
from selenium.webdriver.chrome.options import Options
from fake_useragent import UserAgent
import os
import json

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

def check_procedure(operations, transfer, set_use_thread):
    driver = get_driver()
    for key, value in operations.items():
        hrefs = [key]
        for item in value:
            name_operation, m_name, operation, validator = item
            res = operation(driver, hrefs[0])
            flag, href = validator(res)
            if href:
                hrefs[0] = href
            transfer((name_operation, m_name, flag, hrefs[0]))
            if not flag:
                break
    driver.close()
    set_use_thread()