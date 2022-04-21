import openpyxl
import datetime
import os
import re
import json

def check_file_path(file_path: str):
    try:
        f = open(file_path, 'r')
        f.close()
    except IOError:
        return False
    return True

def check_folder_path(folder_path: str):
    return True if os.path.exists(folder_path) and os.path.isdir(folder_path) else False

def check_file_name(name: str):
    pattern = r'.+_\d{2}_\d{2}.{1}xlsx'
    return True if re.findall(pattern, name) else False

def make_file_name(name: str):
    if name.endswith('.xlsx'):
        name = name.strip().rsplit('.xlsx', 1)[0]
    return f'{name}_{datetime.datetime.now().strftime("%d_%m")}.xlsx'

def search_cell_font_colors(table: list):
    font_colors = set()
    for row in table:
        for cell in row:
            try:
                ind = cell.font.color.index
                if isinstance(ind, str):
                    font_colors.add(ind)
            except AttributeError:
                print(cell)
    return list(font_colors)

def get_worksheet(file_path: str):
    wb = openpyxl.load_workbook(file_path)
    sh = wb.active
    title_row = list(sh[1])
    return sh, title_row

def separate_table(table: list, color: str):
    table_color, table_normal, table_error = [], [], []
    for j, row in enumerate(table):
        try:
            ind = row[0].font.color.index
            if isinstance(ind, str) and ind == color:
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
            new_row.append(cell)
        max_row = i + min_row + 1
        if [el.value for el in new_row] == [None] * len(new_row):
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
    for row in [top_row] + table:
        if isinstance(row[0], str) or isinstance(row[0], int):
            ws.append(row)
        else:
            ws.append(list(map(lambda x: x.value, row)))
    try:
        wb.save(full_path)
    except PermissionError:
        return f'Ошибка доступа к файлу {full_path}. Закройте файл.\n'

    return f'Файл {file_name} успешно сохранён в папке {folder_path}.\n'

def read_table(t):
    for row in t:
        print(list(map(lambda x: x.value, row)))

def check_images(path: str, table: list):
    template = r'[A-Z]+\d+[A-Z]+.+'
    images = set()
    if os.path.exists(path):
        for f_name in os.listdir(path):
            re_part = re.findall(template, f_name)[0]
            if f_name != re_part:
                if os.path.isfile(os.path.join(path, f_name)):
                    os.rename(os.path.join(path, f_name), os.path.join(path, re_part))
                    print(f'File {f_name} was renamed to {re_part}')

            if f_name.endswith('.jpg'):
                images.add(f_name.split('.')[0].split('_')[0])
    articles = set(map(lambda x: x[2].value, table))

    if len(articles) != len(images):
        return f'Количество записей: в файле {len(articles)} в папке {len(images)}', False
        # print(f'Different files numbers: in table {len(articles)} in folder {len(images)}')
    diff = articles.symmetric_difference(images)
    for el in diff:
        if el in articles and el not in images:
            return f'Записи с артикулом {el} в таблице не соответствует ни одной фотографии.\n', False
            # print(f'Article {el} in table have not images')
        if el in images and el not in articles:
            return f'Фотографии {el} в папке нет соответствующей записи в таблице.\n', False
            # print(f'Image {el} in folder have not rows in table')
    return f'Фотографии успешно проверены.\n', True

def get_image_fields(alias: str, images_path: str):
    site_path = "assets/images/product_images/"
    im_names = [f'{alias}.jpg'] + [f'{alias}_{str(i)}.jpg' for i in range(1, 13)]
    f_names = ['image'] + [f'image_{str(i)}' for i in range(1, 13)]
    fields = []
    for i in range(len(im_names)):
        if os.path.exists(os.path.join(images_path, im_names[i])):
            fields.append((f_names[i], f'{site_path}/{im_names[i]}'))
    return fields

def get_insert_queries(images_path: str, table: list, columns_names: list):
    queries = []
    columns = [el[0] for el in columns_names]
    for raw in table:
        alias = str(raw[columns.index('alias')].value)
        fields = get_image_fields(alias, images_path)
        part_1 = ", ".join(col for col in columns[1:])
        part_1_1 = ", ".join(elem[0] for elem in fields)
        part_2 = "', '".join('' if cell.value is None else str(cell.value) for cell in raw[1:])
        part_2_2 = "', '".join(elem[1] for elem in fields)
        queries.append(f"""INSERT INTO catalog({part_1}, {part_1_1}) VALUES ('{part_2}', '{part_2_2}');""")
    return queries

def get_delete_query(table: list):
    part = ', '.join(str(raw[0].value) for raw in table)
    return [f"""DELETE FROM catalog WHERE id IN ({part});"""]

def check_version(version: str):
    json_str = {
                "uploader": {"version": version},
                "save_dir_path": {"path": ""},
                "file_name": {"name": ""},
                "images_path": {"path": ""},
                "cell_color": {"value": ""},
                "update_file_name": {"name": ""},
                "del_file_name": {"name": ""},
                "columns": {"names": []}
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


