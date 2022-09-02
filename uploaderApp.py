import os
import sys
from modules import excel_functions as ex
from base_classes.uploader import Uploader
from kivy.resources import resource_add_path
from kivy.core.window import Window
from kivy.app import App


class UploaderApp(App):
    def build(self):
        return Uploader()

if __name__ == '__main__':
    if hasattr(sys, '_MEIPASS'):
        resource_add_path(os.path.join(sys._MEIPASS))

    ex.check_version(version='1.0.0')
    Window.size = (700, 700)
    UploaderApp().run()