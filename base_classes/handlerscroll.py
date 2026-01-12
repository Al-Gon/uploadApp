from modules import parser_functions as pr
from kivy.properties import StringProperty, NumericProperty, ObjectProperty, ListProperty
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.scrollview import ScrollView
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.anchorlayout import AnchorLayout
from kivy.core.text.text_layout import layout_text


class TrButton(Button):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.data = []
    pass

class ClearLabel(Label):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.size_hint = (1, None)

    def on_texture_size(self, instance, size):
        # print(size)
        instance.height = size[1]

    @property
    def l_label(self):
        return self._label

class ChooseValueItem(GridLayout):
    label_text = StringProperty('')
    check_box = ObjectProperty()

class EditBlock(GridLayout):
    cols = 1
    size_hint = (1, None)
    input_field = ObjectProperty()
    translate_button = ObjectProperty()
    save_button = ObjectProperty()

    def set_height(self):
        height = 0
        for child in self.children:
            height += child.height
        self.height = height + 10

class HandlerScroll(GridLayout):
    cols = 1
    value = StringProperty()
    grid_height = NumericProperty()
    items = ListProperty([])
    edit_blocks = []
    keeper = None

    def set_height(self):
        height = 0
        for child in self.children:
            height += child.height
        self.height = height + 10

    def on_items(self, instance, items):
        self.clear_widgets()
        for item in self.items:
            new_item = ChooseValueItem()
            new_item.label_text = item
            if len(self.items) == 1:
                new_item.check_box.active = True
                self.value = item
            new_item.check_box.bind(active=self.choose_value)
            self.add_widget(new_item)
            self.set_height()

    def choose_value(self, instance, is_active):
        self.value = instance.parent.label_text

    def count_text_h(self, label):
        lines = []
        _, h, _ = layout_text(label.text, lines, (0, 0), (self.width, None),
                              label.l_label.options, label.l_label.get_cached_extents(), True, False)
        return h

    def translate(self, instance):
        value, index = instance.data[0], instance.data[1]
        text = ''
        if value:
            text = pr.get_translation(value)
        self.edit_blocks[index].input_field.text = text

    def save_cell_value(self, instance):
        _id, index = instance.data[0], instance.data[1]
        text = self.edit_blocks[index].input_field.text
        print(self.keeper)
        if text:
            self.keeper['temporary_column'][_id][1] = text
        print(self.keeper)

    def add_edit_block(self, column_name: str, _id: int, value: str):
        edit_block = EditBlock()
        self.edit_blocks.append(edit_block)
        self.add_widget(edit_block)

        label_title = ClearLabel(padding=(30, 10))
        edit_block.add_widget(label_title)
        label_title.text = f'[size=17sp]"Ряд [b]{_id}[/b], редактируемое поле [b]{column_name}[/b][/size]'
        ht = self.count_text_h(label_title)

        label_0 = ClearLabel(padding=(40, 10))
        edit_block.add_widget(label_0)
        label_0.text = '[size=15sp]Старое значение поля:[/size]'
        h0 = self.count_text_h(label_0)

        label_1 = ClearLabel(padding=(20, 10))
        edit_block.add_widget(label_1)
        label_1.text = value
        h1 = self.count_text_h(label_1)

        label_2 = ClearLabel(padding=(40, 10))
        edit_block.add_widget(label_2)
        label_2.text = '[size=15sp]Новое значение поля:[/size]'
        h2 = self.count_text_h(label_2)

        scroll_view = ScrollView(scroll_type=['bars', 'content'],
                                 do_scroll_x=False,
                                 do_scroll_y=True,
                                 size_hint=(1, None),
                                 height=100)
        # bar_width: 10
        # bar_color: utils.get_color_from_hex('#ffffff')
        # bar_inactive_color: utils.get_color_from_hex('#eeeeee'))

        text_input = TextInput(size_hint=(1, None),
                               padding=(20, 5),
                               multiline=True,
                               height=100,
                               background_normal='white_pixel.png',
                               background_active='white_pixel.png')
        scroll_view.add_widget(text_input)
        edit_block.add_widget(scroll_view)
        edit_block.input_field = text_input

        footer = AnchorLayout(size_hint=(1, None), height=60)
        box_layout = BoxLayout(orientation='horizontal',
                               size_hint=(.6, .6))
        button1 = TrButton(size_hint=(.5, 1), text='Перевести')
        button1.data = [value, self.edit_blocks.index(edit_block)]
        button2 = TrButton(size_hint=(.5, 1), text='Сохранить')
        button2.data = [_id, self.edit_blocks.index(edit_block)]
        box_layout.add_widget(button1)
        box_layout.add_widget(button2)
        footer.add_widget(box_layout)
        edit_block.add_widget(footer)
        edit_block.translate_button = button1
        edit_block.translate_button.bind(on_release=self.translate)
        edit_block.save_button = button2
        edit_block.save_button.bind(on_release=self.save_cell_value)

        edit_block.height = ht + h0 + h1 + h2 + text_input.height + footer.height +10
        self.height += edit_block.height

    def remove_edit_blocks(self):
        for block in self.edit_blocks[::-1]:
            self.remove_widget(block)
        self.edit_blocks = []
        self.set_height()
