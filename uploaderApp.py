import os
import sys
from base_classes.uploader import Uploader
from kivy.resources import resource_add_path
from kivy.core.window import Window
from kivy.app import App

# https://stackoverflow.com/questions/74923685/how-do-i-install-kivy-and-kivymd-in-python-3-11-0
# python3.11 -m pip install kivy --pre --no-deps --index-url  https://kivy.org/downloads/simple/
# python3.11 -m pip install "kivy[base]" --pre --extra-index-url https://kivy.org/downloads/simple/
# python3.11 -m pip install https://github.com/kivymd/KivyMD/archive/master.zip


class UploaderApp(App):
    def build(self):
        return Uploader()


if __name__ == '__main__':
    if hasattr(sys, '_MEIPASS'):
        resource_add_path(os.path.join(sys._MEIPASS))

    Window.size = (700, 700)
    UploaderApp().run()
