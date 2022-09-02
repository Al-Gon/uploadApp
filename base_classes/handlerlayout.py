from kivy.uix.boxlayout import BoxLayout
from kivy.properties import NumericProperty
from base_classes.handlerscroll import HandlerScroll

class HandleLayout(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.settings_widget = NumericProperty()
        self.handler_scroll = HandlerScroll(size_hint=(1, None))
        self.scroll.add_widget(self.handler_scroll)