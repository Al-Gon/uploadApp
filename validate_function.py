import requests
import random
import importlib.util

def import_source(module_file_path, module_name):
    module_spec = importlib.util.spec_from_file_location(
        module_name, module_file_path
    )
    if module_spec is None:
        return None
    else:
        # print('Module: {} can be imported!'.format(module_name))
        module = importlib.util.module_from_spec(module_spec)
        module_spec.loader.exec_module(module)
        return module

def missed_function(module, function_names: list) -> list:
    """Returns missed functions which have to be in module"""
    return [name for name in function_names if name not in module.__dict__.keys()]

def is_list_of_tuples(list_: list):
    for el in list_:
        if not (isinstance(el, tuple) and len(el) == 2):
            return False
    return True

def is_tuple_of_str(list_: list):
    for el in list_:
        if not (isinstance(el[0], str) and isinstance(el[1], str)):
            return False
    return True

def is_list_of_str(list_: list):
    for el in list_:
        if not isinstance(el, str):
            return False
    return True

def is_href(list_: list):
    _, hrefs = zip(*list_)
    href = random.choice(list(hrefs))
    if href.startswith('http://') or href.startswith('https://'):
        if 199 < requests.get(href).status_code < 400:
            return True
    return False

def is_src(list_: list):
    src = random.choice(list(list_))
    if (src.startswith('http://') or src.startswith('https://')) and src.rsplit('.')[-1] in ['jpg', 'png']:
        if 199 < requests.get(src).status_code < 400:
            return True
    return False

def check_get_prod_cat(list_: list):
    try:
        if not isinstance(list_, list):
            raise ValueError('возвращаемый результат не является списоком')
        elif not list_:
            raise ValueError('возвращаемый список пуст')
        elif not is_list_of_tuples(list_):
            raise ValueError('элемент списка не является кортежем из двух элементов')
        elif not is_tuple_of_str(list_):
            raise ValueError('элементы кортежа не являются строками')
        elif not is_href(list_):
            raise ValueError('второй элемент кортежа не ссылка')
        else:
            return True, list_[0][1]
    except ValueError as e:
        return False, e

def check_get_item(list_: list):
    try:
        if not isinstance(list_, list):
            raise ValueError('возвращаемый результат не является списоком')
        elif not list_:
            raise ValueError('возвращаемый список пуст')
        elif not len(list_) == 7:
            raise ValueError('количество элементов возвращаемого списока не равно 7')
        elif not is_list_of_str(list_):
            raise ValueError('элементы списка не являются строками')
        else:
            return True, '", "'.join(list_)
    except ValueError as e:
        return False, e

def check_get_images(list_: list):
    try:
        if not isinstance(list_, list):
            raise ValueError('возвращаемый результат не является списоком')
        elif not list_:
            raise ValueError('возвращаемый список пуст')
        elif not is_list_of_str(list_):
            raise ValueError('элементы списка не являются строками')
        elif not is_src(list_):
            raise ValueError('элементы списка не являются ссылками на файлы jpg или png')
        else:
            return True, ''
    except ValueError as e:
        return False, e