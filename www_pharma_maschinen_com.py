from selenium import webdriver
from selenium.webdriver.common.by import By

def get_categories(driver, site: str):
    driver.get(site)
    driver.implicitly_wait(10)
    categories_list = driver.find_elements(By.CSS_SELECTOR, '.categories-list')
    categories = []
    for item in categories_list:
        a = item.find_element(By.CSS_SELECTOR, '.categories-list__item')
        href = a.get_attribute('href')
        text = a.get_attribute('text')
        if text != 'New Arrivals':
            categories.append([text, href])
    return categories

def get_products(driver, category_url: str):
    driver.get(category_url)
    prod_list = driver.find_element(By.CSS_SELECTOR, '.product-list ul')
    prod_items = prod_list.find_elements(By.CSS_SELECTOR, 'li div.product-list-item')
    items_href = []
    if prod_items:
        for item in prod_items:
            item_divs = item.find_elements(By.TAG_NAME, 'div')
            item_class_names = [div.get_attribute('class') for div in item_divs]
            if 'awsm-personal-info' in item_class_names:
                info = item.find_element(By.CLASS_NAME, 'awsm-personal-info')
                text = info.text
                strong = info.find_element(By.TAG_NAME, 'strong').text
                code = text.replace('\n' + strong, '')
                webdriver.ActionChains(driver).move_to_element(info).perform()
                if item.find_element(By.CLASS_NAME, 'awsm-contact-info').is_displayed():
                    a = item.find_element(By.TAG_NAME, 'a')
                    href = a.get_attribute('href')
                    items_href.append((code, href))
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
    prod_code = driver.find_element(By.CSS_SELECTOR, 'div.product-code span')
    prod_block = driver.find_element(By.CSS_SELECTOR, 'div.product-block')
    prod_name = prod_block.find_element(By.CSS_SELECTOR, 'div.product-info .product__name')
    prod_info = prod_block.find_elements(By.CSS_SELECTOR, 'div.product-info .product-info__text *')
    article = prod_code.text
    pagetitle = prod_name.text
    brand, dimensions, introtext = '', '', ''
    text_info = [el.text for el in prod_info if el in ['p', 'li'] and el.text]
    for el in text_info:
        if el.count('Manufacturer:'):
            brand = el.rsplit('Manufacturer:', 1).strip()
        elif el.count('Floor Space:'):
            dimensions = el.rsplit('Floor Space:', 1).strip()
        else:
            introtext += f', {el}'            
    return [article, pagetitle, introtext, '', dimensions, article, brand, '#новые поступления#']
