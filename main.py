import os
import sys
from kivy.resources import resource_add_path, resource_find
import excel_functions as ex
from kivy.uix.gridlayout import GridLayout
from kivy.app import App
from kivy.properties import ObjectProperty, StringProperty


class Container(GridLayout):
    def __init__(self, **kwargs):
        super(Container, self).__init__(**kwargs)
        self.table = None
        self.title = None
        self.del_table = None
        self.update_table = None

    def handle_press(self):
        if self.step_button.text == 'Шаг 1':
            if ex.check_path(str(self.file_path.text).strip()):
                self.massage.text = 'Файл найден.'
                self.step_info.text = f'Обрабатывается файл : {str(self.file_path.text).strip()} \n'
                self.table, self.title = ex.get_worksheet(str(self.file_path.text).strip())
                if self.table is not None:
                    self.file_path.text = 'Выберите цвет шрифта выделенных ячеек: \n'
                    self.file_path.text += ' '.join([color for color in ex.search_cell_font_colors(self.table)])
                else:
                    self.file_path.text = 'Что-то пошло не так'
                self.step_button.text = 'Шаг 2'
            else:
                self.massage.text = 'Не верен путь или имя файла.'
        elif self.step_button.text == 'Шаг 2':
            color = str(self.file_path.text).strip()
            self.massage.text = 'Выбран цвет выделенных ячеек.'
            self.step_info.text += f'Выбран цвет выделенных ячеек: {color} \n'
            m_table, m_row = ex.get_table(self.table, 2, 10)
            update_table, _ = ex.get_table(self.table, m_row, 10)
            self.del_table, table_norm, table_err = ex.separate_table(m_table, color)
            start_id = max(m_table, key=lambda x: x[0].value)[0].value
            update_table = ex.set_value(update_table, 0, start_id, True)
            self.update_table = ex.set_value(update_table, 9, '#новые поступления#', False)
            self.file_path.text = 'Ведите путь к папке с фотографиями.'
            self.step_button.text = 'Шаг 3'
        elif self.step_button.text == 'Шаг 3':
            path = str(self.file_path.text).strip()
            self.step_info.text += f'Выбран путь к папке с фотографиями: {path} \n'
            ex.check_images(path, self.update_table)
            self.step_button.text = 'Шаг 4'


class ContainerApp(App):

    def build(self):
        return Container()


if __name__ == '__main__':
    if hasattr(sys, '_MEIPASS'):
        resource_add_path(os.path.join(sys._MEIPASS))
    ContainerApp().run()
