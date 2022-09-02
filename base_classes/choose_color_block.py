from kivy.uix.gridlayout import GridLayout
from kivy.properties import StringProperty, ListProperty
from kivy.lang import Builder

# Builder.load_file('base_classes/kv/base_widgets.kv')

class ChooseColorBlock(GridLayout):
    choose_color = StringProperty('')
    panels = ListProperty([])
    panel = None

    def on_panels(self, instance, panels):
        if panels:
            instance.add_widget(self.panels[0])
            instance.panel = self.panels[0]
        else:
            instance.remove_widget(self.panel)
            self.panel = None
        height = 0
        for child in self.children:
            height += child.height
        self.height = height + 10