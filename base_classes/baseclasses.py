from kivy.uix.floatlayout import FloatLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.scrollview import ScrollView
from kivy.properties import StringProperty, NumericProperty
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.lang import Builder

Builder.load_file('base_classes/kv/base_widgets.kv')
Builder.load_file('base_classes/kv/setting_layout.kv')
Builder.load_file('base_classes/kv/load_layout.kv')
Builder.load_file('base_classes/kv/parser_layout.kv')
Builder.load_file('base_classes/kv/handle_layout.kv')
Builder.load_file('base_classes/kv/upload_layout.kv')


class ButtonGetColors(FloatLayout):
    button_text = StringProperty('')
    pass

class ButtonSaveColor(FloatLayout):
    pass

class ItemLabel(Label):
    message = StringProperty('')

class ScrollLabel(ScrollView):
    message = StringProperty('')

class InputBlock(FloatLayout):
    input_string = StringProperty('')

class ScreenTemplate(Screen):
    pass

class SettingLayout(BoxLayout):
    grid_height = NumericProperty()
    pass

class LoadLayout(BoxLayout):
    pass

class UploadLayout(BoxLayout):
    pass

class NewScreenManager(ScreenManager):
    pass