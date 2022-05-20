from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException, NoSuchAttributeException
import requests
from selenium.webdriver.chrome.options import Options
from fake_useragent import UserAgent
import importlib.util
import os

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

# def get_categories(driver, site: str):
#     driver.get(site)
#     driver.implicitly_wait(10)
#     categories_list = driver.find_elements(By.CSS_SELECTOR, '.categories-list')
#     categories = []
#     for item in categories_list:
#         a = item.find_element(By.CSS_SELECTOR, '.categories-list__item')
#         href = a.get_attribute('href')
#         text = a.get_attribute('text')
#         categories.append([text, href])
#     return categories
#
# def get_categories_(driver, site: str):
#     driver.get(site)
#     driver.implicitly_wait(10)
#     categories_list = driver.find_elements(By.CSS_SELECTOR, '.categories-wrapper div')
#     categories = set()
#     for item in categories_list:
#         a = item.find_element(By.CSS_SELECTOR, 'div.categories-card-container h2.title a')
#         href = a.get_attribute('href')
#         text = a.get_attribute('text')
#         categories.add((text, href))
#     return list(categories)
#
# def get_products(driver, category_url: str):
#     driver.get(category_url)
#     prod_list = driver.find_element(By.CSS_SELECTOR, '.product-list ul')
#     prod_items = prod_list.find_elements(By.CSS_SELECTOR, 'li div.product-list-item')
#     items_href = []
#     if prod_items:
#         for item in prod_items:
#             item_divs = item.find_elements(By.TAG_NAME, 'div')
#             item_class_names = [div.get_attribute('class') for div in item_divs]
#             if 'awsm-personal-info' in item_class_names:
#                 info = item.find_element(By.CLASS_NAME, 'awsm-personal-info')
#                 text = info.text
#                 strong = info.find_element(By.TAG_NAME, 'strong').text
#                 code = text.replace('\n' + strong, '')
#                 webdriver.ActionChains(driver).move_to_element(info).perform()
#                 if item.find_element(By.CLASS_NAME, 'awsm-contact-info').is_displayed():
#                     a = item.find_element(By.TAG_NAME, 'a')
#                     href = a.get_attribute('href')
#                     items_href.append((code, href))
#     return items_href
#
# def get_products_(driver, category_url: str):
#     driver.get(category_url)
#     prod_list = driver.find_element(By.CSS_SELECTOR, 'div.listings-index')
#     prod_items = prod_list.find_elements(By.CSS_SELECTOR, 'div.listing .listing__title a')
#     items_href = []
#     if prod_items:
#         for item in prod_items:
#             code = item.text.split(' - ')[0].replace(' ', '')
#             items_href.append((code, item.get_attribute('href')))
#     return items_href
#
# def get_item_images(driver, item_url: str):
#     driver.get(item_url)
#     prod_block = driver.find_element(By.CSS_SELECTOR, 'div.product-block')
#     images = []
#     img_a = prod_block.find_element(By.CSS_SELECTOR, 'div.product__img a')
#     images.append(img_a.get_attribute('href'))
#     slider = prod_block.find_elements(By.CSS_SELECTOR, 'div.slick-track div')
#     if slider:
#         for item in slider:
#             a = item.find_element(By.TAG_NAME, 'a')
#             images.append(a.get_attribute('href'))
#     return images
#
# def get_item_images_(driver, item_url: str):
#     driver.get(item_url)
#     images_container = driver.find_elements(By.CSS_SELECTOR, 'ul #gallery__thumbnail-container li')
#     images = []
#     if images_container:
#         for item in images_container:
#             a = item.find_element(By.TAG_NAME, 'img')
#             images.append(a.get_attribute('src'))
#     return images
#
#
#
#
# def get_item_content(driver, item_url: str):
#     driver.get(item_url)
#     prod_code = driver.find_element(By.CSS_SELECTOR, 'div.product-code span')
#     prod_block = driver.find_element(By.CSS_SELECTOR, 'div.product-block')
#     prod_name = prod_block.find_element(By.CSS_SELECTOR, 'div.product-info .product__name')
#     prod_info = prod_block.find_elements(By.CSS_SELECTOR, 'div.product-info .product-info__text')
#     code = prod_code.text
#     name = prod_name.text
#     info = ' '.join([p.text for p in prod_info])
#     info_ = info.replace('\n', '').rsplit('Raumbedarf:', 1)
#     info__ = info_[0].rsplit('Hersteller:', 1)
#     return [code, name, info__[0], info__[1], info_[1]]
#
# def get_item_content_(driver, item_url: str):
#     driver.get(item_url)
#     info = ''
#     header = find_element(driver, By.CSS_SELECTOR, 'div.show-info__header .show-info__title')
#     divs = find_elements(driver, By.CSS_SELECTOR, 'div.show-info__section-text p')
#     if divs:
#         info += ', '.join([p.text for p in divs])
#     table = find_element(driver, By.CSS_SELECTOR, 'div.show-info__specifications table')
#     table_ = {}
#     for tr in table.find_elements(By.TAG_NAME, 'tr'):
#         td_1, td_2 = tr.find_elements(By.TAG_NAME, 'td')
#         table_[td_1.text] = td_2.text
#
#     code = table_['Stock Number'].replace(' ', '')
#     name = header.text.replace(table_['Stock Number'] + ' - ', '')
#     brand, dimensions = '', ''
#     if 'Manufacturer' in table_.keys():
#         brand = table_['Manufacturer']
#     if 'Floor space' in table_.keys():
#         dimensions = table_['Floor space']
#     excepted_keys = ['Manufacturer', 'Condition', 'Stock Number', 'Floor space']
#     info += ', '.join([f'{k}: {v}' for k, v in table_.items() if k not in excepted_keys])
#
#     return [code, name, info, brand, dimensions]



# def main():
#
#
#     l_b = ex.get_col_by_name(folder_path, 'pm.xlsx', 'артикул')
#     l_a = ex.get_col_by_name(folder_path, 'catalog_26_04.xlsx', 'Артикул')
#     print(l_a)
#     print(l_b)
#     print(ex.compare_list(l_a, l_b))
