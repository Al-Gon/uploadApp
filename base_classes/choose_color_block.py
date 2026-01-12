from kivy.uix.gridlayout import GridLayout
from kivy.properties import StringProperty, ListProperty
from base_classes.config import Config
from base_classes.colorspanel import ColorsPanel

class ChooseColorBlock(GridLayout):
    choose_color = StringProperty('FFFFFF')
    panels = ListProperty([])
    panel = None
    config = Config()

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

    def handle_color(self, name):
        if not self.panels:
            panel = ColorsPanel()
            self.panels.append(panel)
        else:
            self.config.put(name, self.choose_color)
            self.panels = []