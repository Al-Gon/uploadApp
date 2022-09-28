from kivy.uix.boxlayout import BoxLayout
from kivy.properties import NumericProperty
from kivy.lang import Builder
from base_classes.config import Config

Builder.load_file('base_classes/kv/setting_layout.kv')

class SettingLayout(BoxLayout):
    config = Config()
    grid_height = NumericProperty()

    def repr_console_massage(self, massage):
        self.console.message = massage

    def set_height(self):
        height = 0
        for child in self.grid.children:
            height += child.height
        self.grid_height = height + 25

    def update(self):
        for key, obj in self.ids.items():
            if key in self.config.keys():
                value = self.config[key]
                if value:
                    if isinstance(value, str):
                        if hasattr(obj, 'input'):
                            obj.input.text = value
                        elif hasattr(obj, 'choose_color'):
                            obj.choose_color = value
                    if isinstance(value, list):
                        obj.input.text = ', '.join(value)
        self.set_height()