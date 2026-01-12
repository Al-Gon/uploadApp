from kivy.uix.label import Label
from kivy.uix.checkbox import CheckBox
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.anchorlayout import AnchorLayout
from kivy.uix.gridlayout import GridLayout
from kivy.utils import get_color_from_hex
from kivy.graphics import Color, Rectangle

class ColorLabel(Label):
    def __init__(self, color_, **kwargs):
        super(ColorLabel, self).__init__(**kwargs)
        self.color_ = color_
        # self.height = 30
        # self.padding = [5, 5]
        with self.canvas.before:
            Color(*get_color_from_hex(self.color_))
            self.rect = Rectangle(pos=self.pos, size=self.size)
        self.bind(pos=self.update_rect)
        self.bind(size=self.update_rect)

    def update_rect(self, *args):
        self.rect.pos = self.pos
        self.rect.size = self.size

class ColorItem(BoxLayout):
    def __init__(self, item_color, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'vertical'
        self.item_color = item_color
        check_box = AnchorLayout(size_hint=(1, .5), anchor_x='center', anchor_y='center')
        self.check_box = CheckBox(group='colors', active=False,
                                  color=get_color_from_hex('000000'))
        check_box.add_widget(self.check_box)
        self.add_widget(check_box)
        self.add_widget(ColorLabel(item_color, size_hint=(1, .5)))


class ColorsPanel(GridLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        colors = ['000000', 'FFFFFF', 'FF0000', '00FF00', '0000FF',
                  'FFFF00', 'FF00FF', '00FFFF', '800000', '008000',
                  '000080', '808000', '800080', '008080', 'C0C0C0',
                  '808080', '9999FF', '993366', 'FFFFCC', 'CCFFFF',
                  '660066', 'FF8080', '0066CC', 'CCCCFF', '00CCFF',
                  'CCFFCC', 'FFFF99', '99CCFF', 'FF99CC', 'CC99FF',
                  'FFCC99', '3366FF', '33CCCC', '99CC00', 'FFCC00',
                  'FF9900', 'FF6600', '666699', '969696', '003366',
                  '339966', '003300', '333300', '993300', '333399']
        self.cols = 5
        self.rows = len(colors) // 5
        self.height = self.rows * 60
        self.padding = [10, 10]
        for color in colors:
            color_item = ColorItem(color)
            color_item.check_box.bind(active=self.get_color)
            self.add_widget(color_item)

    def get_color(self, instance, is_active):
        if self.parent:
            self.parent.choose_color = instance.parent.parent.item_color
