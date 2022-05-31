import openpyxl
import datetime
import os
import re
import json
import parser_functions as pr

def check_file_path(file_path: str):
    try:
        f = open(file_path, 'r')
        f.close()
    except IOError:
        return False
    return True

def check_folder_path(folder_path: str) -> bool:
    """Creates folder if it not exists."""
    if os.path.exists(folder_path) and os.path.isdir(folder_path):
        return True
    else:
        try:
            os.mkdir(folder_path)
            return check_folder_path(folder_path)
        except WindowsError:
            return False


def check_file_name(name: str):
    pattern = r'.*_\d{2}_\d{2}.{1}xlsx'
    return True if not name or re.findall(pattern, name) else False

def make_file_name(name: str, substr: bool = False):
    """Returns the file name with xlsx extension as a string """
    date = f'_{datetime.datetime.now().strftime("%d_%m")}'
    site = ''
    if name.endswith('.xlsx'):
        name = name.strip().rsplit('.xlsx', 1)[0]
    if substr:
        site = '_{site}'
        # url = f'_{url.lstrip("https://").split("/")[0].replace(".", "_")}'
    return f'{name}{site}{date}.xlsx'

def del_dir_files(dir_path: str) -> bool:
    """Returns True if dir is empty."""
    for file in os.listdir(dir_path):
        os.remove(os.path.join(dir_path, file))
    if os.listdir(dir_path):
        return del_dir_files(dir_path)
    else:
        return True

def search_cell_font_colors(table: list):
    font_colors = set()
    for row in table:
        for cell in row:
            try:
                color = cell.font.color.rgb
                if isinstance(color, str):
                    font_colors.add(color[2:])
            except AttributeError:
                print(cell)
    return list(font_colors)

def search_cell_fill_colors(table: list):
    fill_colors = set()
    for row in table:
        for cell in row:
            if cell.fill.fill_type is not None:
                try:
                    color = cell.fill.fgColor.rgb
                    if isinstance(color, str):
                        fill_colors.add(color[2:])
                except AttributeError:
                    print(cell)
    return list(fill_colors)

def get_worksheet(file_path: str):
    wb = openpyxl.load_workbook(file_path)
    sh = wb.active
    title_row = list(sh[1])
    return sh, title_row

def separate_table(table: list, color: str, c_type: str):
    table_color, table_normal, table_error = [], [], []
    for j, row in enumerate(table):
        try:
            color_ = None
            if c_type == 'text':
                color_ = row[0].font.color.rgb
            if c_type == 'fill':
                color_ = row[0].fill.fgColor.rgb
            if isinstance(color_, str) and color_ == 'FF' + color:
                table_color.append(row)
            else:
                table_normal.append(row)
        except AttributeError:
            print(f'raw number =  {j}, value {row.value}')
            table_error.append(row)
    return table_color, table_normal, table_error


def get_table(w_sheet, min_row: int, max_col: int):

    main_table = []
    max_row = 0
    for i, row in enumerate(w_sheet.iter_rows(min_row=min_row, max_col=max_col)):
        new_row = []
        for cell in row:
            if cell.value is not None:
                new_row.append(cell.value)
            else:
                new_row.append('')
        max_row = i + min_row + 1
        if new_row == [''] * len(new_row):
            break
        main_table.append(new_row)

    return main_table, max_row

def set_value(table: list, pos: int, val, incr: bool):
    for row in table:
        if incr:
            try:
                val += 1
            except TypeError:
                print('TypeError param val in set_value :(')
                break
        row[pos].value = val
    return table

def get_file_from_table(folder_path: str, file_name: str, table: list, top_row: list):
    full_path = os.path.join(folder_path, file_name)
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = 'Main'
    error_msg = []
    for row in [top_row] + table:
        if isinstance(row[0], str) or isinstance(row[0], int):
            ws.append(row)
        else:
            ws.append(row)
    try:
        wb.save(full_path)
    except PermissionError:
        error_msg = f'Ошибка доступа к файлу {full_path}. Закройте файл.\n'
    return error_msg

def check_images(path: str, table: list):
    template = r'[A-Z]+\d+[A-Z]+.+'
    images = set()
    if os.path.exists(path):
        for f_name in os.listdir(path):
            re_part = re.findall(template, f_name)
            if re_part and f_name != re_part[0]:
                if os.path.isfile(os.path.join(path, f_name)):
                    os.rename(os.path.join(path, f_name), os.path.join(path, re_part[0]))
                    print(f'File {f_name} was renamed to {re_part[0]}')

            if f_name.endswith('.jpg'):
                images.add(f_name.split('.')[0].split('_')[0])
    articles = set(map(lambda x: x[2].value, table))

    if len(articles) != len(images):
        return f'Количество записей: в файле {len(articles)} в папке с фотографиями {len(images)}.\n', False
    diff = articles.symmetric_difference(images)
    for el in diff:
        if el in articles and el not in images:
            return f'Записи с артикулом {el} в таблице не соответствует ни одной фотографии.\n', False
        if el in images and el not in articles:
            return f'Фотографии {el} в папке нет соответствующей записи в таблице.\n', False
    return f'Фотографии успешно проверены.\n', True

def get_image_fields(alias: str, images_paths: list) -> tuple:
    """
    Returns list of tuples, if length of paths smaller than 12 list will be added elements like empty string
    :param alias:
    :param images_paths:
    :return:
    """
    num = 13
    if len(images_paths) > num:
        images_paths = images_paths[: num - 1]
    site_path = "assets/images/product_images/"
    file_names = [f'{alias}.jpg'] + [f'{alias}_{str(i)}.jpg' for i in range(1, len(images_paths))]
    values = [site_path + f_name for f_name in file_names]
    if len(values) < num:
        values += [''] * (num - len(values))
    fields_names = ['image'] + [f'image_{str(i)}' for i in range(1, num)]
    return images_paths, file_names, values, fields_names

def check_version(version: str):
    json_str = {
                "uploader": {"version": version},
                "save_dir_path": {"path": ""},
                "file_name": {"name": ""},
                "images_folder_name": {"name": ""},
                "cell_color": {"type": "",
                               "value": ""},
                "update_file_name": {"name": ""},
                "del_file_name": {"name": ""},
                "columns": {"names": []},
                "category_site_file_name": {"name": ""},
                "data_site_file_name": {"name": ""},
                "category_site_urls": {"urls": {}},
                "functions_names": {"names": ["get_categories",
                                              "get_products",
                                              "get_item_content",
                                              "get_item_images"]}
                }

    version_ = ''
    if check_file_path('settings.json'):
        with open('settings.json') as json_file:
            data = json.load(json_file)
            if 'uploader' in data.keys():
                version_ = data['uploader']['version']

    if not check_file_path('settings.json') or version_ != version:
        with open('settings.json', 'w', encoding='utf-8',) as file:
            file.write(json.dumps(json_str))
