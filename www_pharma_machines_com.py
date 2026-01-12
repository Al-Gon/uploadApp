import re
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


def accept_cookie(driver, url):
    driver.get(url)
    try:
        btn = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.CSS_SELECTOR, '#cookies_notice_btn')))
        btn.click()
    except TimeoutException:
        pass
    finally:
        driver.cookie = True


def find_element(obj, by, way: str):
    try:
        return obj.find_element(by, way)
    except NoSuchElementException:
        print(f'Element {way.split(" ")[-1]} not found')
        return None


def find_elements(obj, by, way: str):
    try:
        return obj.find_elements(by, way)
    except NoSuchElementException:
        print(f'Elements {way.split(" ")[-1]} not found')
        return []


def get_categories(driver, site: str):
    driver.get(site)
    driver.implicitly_wait(5)
    categories_list = find_elements(driver, By.CSS_SELECTOR, '.categories-wrapper div')
    categories = set()
    if categories_list:
        for item in categories_list:
            el = find_element(item, By.CSS_SELECTOR, 'div.categories-card-container h2.title a')
            if el is not None:
                href = el.get_attribute('href')
                if '/en/' not in href:
                    href_ = href.rsplit('/', 1)
                    href = href_[0] + '/en/' + href_[1]
                text = el.get_attribute('text')
                categories.add((text, href))
            else:
                break
    return list(categories)


def get_products(driver, category_url: str):
    driver.get(category_url)
    prod_list = find_element(driver, By.CSS_SELECTOR, 'div.listings-index')
    items_href = []
    if prod_list is not None:
        prod_items = find_elements(prod_list, By.CSS_SELECTOR, 'div.listing .listing__title a')
        if prod_items:
            for item in prod_items:
                article = item.text.split(' - ')[0].replace(' ', '')
                items_href.append((article, item.get_attribute('href')))
    return items_href


def get_item_content(driver, item_url: str):
    driver.get(item_url)
    article, page_title, intro_text, brand, dimensions = '', '', '', '', ''
    header = find_element(driver, By.CSS_SELECTOR, 'div.show-info__header .show-info__title')
    if header is not None:
        template = r'^([A-Z]+\s*\d{1,5}(?:\s*-\s*|\s*[A-Z]|\s*[A-Z]\s*-\s*))'
        article = re.findall(template, header.text)[0]
        page_title = header.text.replace(article, '')
        article = article.replace(' ', '').rstrip('-')
        page_title = page_title.replace("'", '`')

    description = find_element(driver, By.CSS_SELECTOR, 'div.show-info__description')
    if description is not None:
        if hasattr(description, 'text'):
            description = re.sub('\s+', ' ', description.text).strip()
            intro_text = description.lstrip('Description ')
    table = find_element(driver, By.CSS_SELECTOR, 'div.show-info__specifications table')
    table_ = {}
    if table is not None:
        tr_list = find_elements(table, By.TAG_NAME, 'tr')
        if tr_list:
            for tr in tr_list:
                td_list = find_elements(tr, By.TAG_NAME, 'td')
                if td_list:
                    table_[td_list[0].text] = td_list[1].text
    if 'Manufacturer' in table_.keys():
        brand = table_['Manufacturer'].replace("'", '`')
    if 'Floor space' in table_.keys():
        dimensions = table_['Floor space'].replace("'", '`')
    excepted_keys = ['Manufacturer', 'Condition', 'Stock Number', 'Floor space']
    intro_text += ', '.join([f'{k}: {v}' for k, v in table_.items() if k not in excepted_keys])
    intro_text = intro_text.replace("'", '`')

    return [article, page_title, intro_text, article, brand, dimensions, '#новые поступления#']


def get_item_images(driver, item_url: str):
    driver.get(item_url)
    images_container = driver.find_elements(By.CSS_SELECTOR, '#gallery__thumbnail-container li')
    images = []
    if images_container:
        for item in images_container:
            img = item.find_element(By.TAG_NAME, 'img')
            images.append(img.get_attribute('src'))
    else:
        img = driver.find_element(By.CSS_SELECTOR, '#gallery img.gallery-image')
        images.append(img.get_attribute('src'))
    return images
