import json
from collections import UserDict
from base_classes.singleton import Singleton

class Config(Singleton, UserDict):
    content = {
        "f_path": "set.json",
        "version": "1.0.1",
        "save_dir_path": "",
        "db_file_name": "",
        "file_name": "",
        "images_folder_name": "",
        "title_fill_color": "",
        "title_font_color": "",
        "update_file_name": "",
        "del_file_name": "",
        "columns": [],
        "category_site_file_name": "",
        "data_site_file_name": "",
        "category_site_urls": [],
        "functions_names": ["get_categories",
                            "get_products",
                            "get_item_content",
                            "get_item_images"]
    }

    def __init__(self, **kwargs):
        super(Config, self).__init__(**kwargs)

    def update_content(self):
        if self.check_file_path(self.content['f_path']):
            content_ = self.load_file(self.content['f_path'])
            if content_['version'] == self.content['version']:
                for k, v in content_.items():
                    self[k] = v

        if not self.data:
            for k, v in self.content.items():
                self[k] = v
            self.save_data()

    def put(self, key, value):
        print(key)
        if key not in self.content.keys():
            raise ValueError(f'Не верный ключ словаря {key}.')
        elif not isinstance(value, type(self.content[key])):
            raise ValueError(f'Не верно задан тип значения словаря: ключ {key} значение {value}.')
        else:
            self.data[key] = value
            self.save_data()

    def save_data(self):
        with open(self['f_path'], 'w', encoding='utf-8') as f:
            f.write(json.dumps(self.data))

    @staticmethod
    def check_file_path(file_path: str):
        try:
            f = open(file_path, 'r')
            f.close()
        except IOError:
            return False
        return True

    @staticmethod
    def load_file(name):
        with open(name, 'r') as f:
            store = json.loads(f.readline())
        return store