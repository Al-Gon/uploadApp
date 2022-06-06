from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException

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

def get_categories(driver, site: str):
    driver.get(site)
    driver.implicitly_wait(10)
    categories_list = driver.find_elements(By.CSS_SELECTOR, '.categories-wrapper div')
    categories = set()
    for item in categories_list:
        a = item.find_element(By.CSS_SELECTOR, 'div.categories-card-container h2.title a')
        href = a.get_attribute('href')
        text = a.get_attribute('text')
        categories.add((text, href))
    return list(categories)

def get_products(driver, category_url: str):
    driver.get(category_url)
    prod_list = driver.find_element(By.CSS_SELECTOR, 'div.listings-index')
    prod_items = prod_list.find_elements(By.CSS_SELECTOR, 'div.listing .listing__title a')
    items_href = []
    if prod_items:
        for item in prod_items:
            code = item.text.split(' - ')[0].replace(' ', '')
            items_href.append((code, item.get_attribute('href')))
    return items_href
    
def get_item_images(driver, item_url: str):
    driver.get(item_url)
    images_container = driver.find_elements(By.CSS_SELECTOR, '#gallery__thumbnail-container li')
    images = []
    if images_container:
        for item in images_container:
            img = item.find_element(By.TAG_NAME, 'img')
            images.append(img.get_attribute('src'))
    return images

def get_item_content(driver, item_url: str):
    driver.get(item_url)
    introtext = ''
    header = find_element(driver, By.CSS_SELECTOR, 'div.show-info__header .show-info__title')
    description = find_elements(driver, By.CSS_SELECTOR, 'div.show-info__description *')
    if description:
        introtext += ', '.join([el.text for el in description if el.text]) + ' '
    table = find_element(driver, By.CSS_SELECTOR, 'div.show-info__specifications table')
    table_ = {}
    for tr in table.find_elements(By.TAG_NAME, 'tr'):
        td_1, td_2 = tr.find_elements(By.TAG_NAME, 'td')
        table_[td_1.text] = td_2.text

    article = table_['Stock Number'].replace(' ', '')
    pagetitle = header.text.replace(table_['Stock Number'] + ' - ', '').replace("'", '`')
    brand, dimensions = '', ''
    if 'Manufacturer' in table_.keys():
        brand = table_['Manufacturer'].replace("'", '`')
    if 'Floor space' in table_.keys():
        dimensions = table_['Floor space'].replace("'", '`')
    excepted_keys = ['Manufacturer', 'Condition', 'Stock Number', 'Floor space']
    introtext += ', '.join([f'{k}: {v}' for k, v in table_.items() if k not in excepted_keys])
    introtext = introtext.replace("'", '`')

    return [article, pagetitle, introtext, article, brand, dimensions, '#новые поступления#']