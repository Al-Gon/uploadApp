import re

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException


def accept_cookie(driver, url):
    driver.get(url)
    try:
        btn = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, 'div.cc_banner-wrapper a.cc_btn')))
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
    driver.implicitly_wait(10)
    categories_list = find_elements(driver, By.CSS_SELECTOR, '.categories-list')
    categories = []
    if categories_list:
        for item in categories_list:
            el = find_element(item, By.CSS_SELECTOR, '.categories-list__item')
            if el is not None:
                href = el.get_attribute('href')
                text = el.get_attribute('text')
                if 'new arrivals' not in text.lower():
                    pattern = r'\(\d+\)'
                    text = re.sub(pattern, '', text).strip()
                    categories.append((text, href))
            else:
                break
    return categories


def get_products(driver, category_url: str):
    driver.get(category_url)
    items_href = []
    prod_list = find_element(driver, By.CSS_SELECTOR, '.product-list ul')
    if prod_list is not None:
        prod_items = find_elements(prod_list, By.CSS_SELECTOR, 'li div.product-list-item')
        if prod_items:
            for item in prod_items:
                item_href = ('', '')
                item_divs = find_elements(item, By.TAG_NAME, 'div')
                if item_divs:
                    item_class_names = [div.get_attribute('class') for div in item_divs]
                    if 'awsm-personal-info' in item_class_names:
                        info = find_element(item, By.CLASS_NAME, 'awsm-personal-info')
                        if info is not None:
                            text = info.text
                            strong = find_element(info, By.TAG_NAME, 'strong').text
                            article = text.replace('\n' + strong, '')
                            # webdriver.ActionChains(driver).move_to_element(info).perform()
                            contact = item.find_element(By.CLASS_NAME, 'awsm-contact-info')
                            if contact.is_enabled():
                                btn_detail = contact.find_element(By.CLASS_NAME, 'product__btn-detail')
                                href = btn_detail.get_attribute('href')
                                item_href = (article, href)
                if item_href == ('', ''):
                    break
                else:
                    items_href.append(item_href)
    return items_href


def get_item_images(driver, item_url: str):
    driver.get(item_url)
    prod_block = driver.find_element(By.CSS_SELECTOR, 'div.product-block')
    images = []
    img_a = prod_block.find_element(By.CSS_SELECTOR, 'div.product__img a')
    images.append(img_a.get_attribute('href'))
    slider = prod_block.find_elements(By.CSS_SELECTOR, 'div.slick-track div')
    if slider:
        for item in slider:
            a = item.find_element(By.TAG_NAME, 'a')
            images.append(a.get_attribute('href'))
    return images


def get_item_content(driver, item_url: str):
    driver.get(item_url)
    article, page_title, intro_text, brand, dimensions = '', '', '', '', ''
    prod_code = find_element(driver, By.CSS_SELECTOR, 'div.product-code span')
    if prod_code is not None:
        article = prod_code.text
    prod_block = find_element(driver, By.CSS_SELECTOR, 'div.product-block')
    if prod_block is not None:
        prod_name = find_element(prod_block, By.CSS_SELECTOR, 'div.product-info .product__name')
        prod_info = find_elements(prod_block, By.CSS_SELECTOR, 'div.product-info .product-info__text *')
        page_title = prod_name.text.replace("'", '`')
        text_info = [el.text for el in prod_info if el.tag_name in ['p', 'li', 'div'] and el.text.strip()]
        for el in text_info:
            if el.count('Floor Space:'):
                brand, dimensions = el.split('Floor Space:')
                dimensions = dimensions.strip().replace("'", '`')
                brand = brand.replace('Manufacturer:', '').strip().replace("'", '`')
            else:
                intro_text += f'{el} '
        intro_text = intro_text.strip().replace("'", '`')

    return [article, page_title, intro_text, article, brand, dimensions, '#новые поступления#']

# from modules.parser_functions import *
#
# site = 'https://www.pharma-maschinen.com/categories_engl.php'
# driver = get_driver()
# cat = get_categories(driver=driver, site=site)
#
# a = 1
