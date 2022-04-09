import openpyxl
import datetime
import os
import re

def check_path(file_path: str):
    try:
        f = open(file_path, 'r')
        f.close()
    except IOError:
        return False
    return True

def search_cell_font_colors(table: list):
    font_colors = set()
    for raw in table:
        for cell in raw:
            try:
                ind = cell.font.color.index
                if isinstance(ind, str):
                    font_colors.add(ind)
            except AttributeError:
                print(cell)
    return list(font_colors)

def get_worksheet(file_path: str):
    wb_2 = openpyxl.load_workbook(file_path)
    sh_wb_2 = wb_2['Worksheet']
    title_row = list(sh_wb_2[1])
    return sh_wb_2, title_row


def separate_table(table: list, color: str):
    table_color, table_normal, table_error = [], [], []
    for j, raw in enumerate(table):
        try:
            ind = raw[0].font.color.index
            if isinstance(ind, str) and ind == color:       # print(f'color {ind} value {raw.value}')
                table_color.append(raw)
            else:
                table_normal.append(raw)
        except AttributeError:
            print(f'raw number =  {j}, value {raw.value}')
            table_error.append(raw)
    return table_color, table_normal, table_error

def get_table(w_sheet, min_row: int, max_col: int):
    main_table = []
    max_row = 0
    for i, row in enumerate(w_sheet.iter_rows(min_row=min_row, max_col=max_col)):
        new_row = []
        for cell in row:
            new_row.append(cell)
        if [el.value for el in new_row] == [None] * len(new_row):
            print(f'Loaded {i} rows')
            max_row = i + min_row + 1
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

def get_file_from_table(name_table: str, table: list, top_row: list):
    file_name = name_table.strip() + '_' + datetime.datetime.now().strftime('%m_%d') + '.xlsx'
    wb = openpyxl.Workbook()
    ws = wb.active
    for row in [top_row] + table:
        ws.append(list(map(lambda x: x.value, row)))
    wb.save(file_name)

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
        return f'Different files numbers: in table {len(articles)} in folder {len(images)}'
        # print(f'Different files numbers: in table {len(articles)} in folder {len(images)}')
    diff = articles.symmetric_difference(images)
    for el in diff:
        if el in articles and el not in images:
            return f'Article {el} in table have not images'
            # print(f'Article {el} in table have not images')
        if el in images and el not in articles:
            return f'Image {el} in folder have not rows in table'
            # print(f'Image {el} in folder have not rows in table')


# wb_2 = openpyxl.load_workbook('test.xlsx')
# sh_wb_2 = wb_2['Worksheet']
# #
# title_row = list(sh_wb_2[1])
# print(sh_wb_2)
# print(search_cell_font_colors(sh_wb_2))
# m_table, m_row = get_table(sh_wb_2, 2, 10)
# update_table, _ = get_table(sh_wb_2, m_row, 10)
# table_del, table_norm, table_err = separate_table(m_table, 'FFFF0000')
#
# start_id = max(m_table, key=lambda x: x[0].value)[0].value
#
# update_table = set_value(update_table, 0, start_id, True)
# update_table = set_value(update_table, 9, '#новые поступления#', False)
#
# check_images('C:\\Users\jenya\Desktop\\23.03\\23.03', update_table)
# get_file_from_table('update', update_table, title_row)
# get_file_from_table('del', table_del, title_row)
    #     print(f"coordinate: {cell.coordinate}\tvalue: {cell.value}\tcolor: {cell.fill.start_color.index}\ttext color: {cell.font.color.index}\t")
