from kivy.uix.floatlayout import FloatLayout
from base_classes.baseclasses import ScreenTemplate
from base_classes.settinglayout import SettingLayout
from base_classes.loadlayout import LoadLayout
from base_classes.handlerlayout import HandleLayout
from base_classes.parserlayout import ParserLayout
from base_classes.uploadlayout import UploadLayout
from kivy.lang import Builder
from base_classes.config import Config

Builder.load_file('base_classes/kv/uploader.kv')


class Uploader(FloatLayout):
    def __init__(self, **kwargs):
        super(Uploader, self).__init__(**kwargs)

        self.config = Config()
        self.config.update_content()

        layouts = [(SettingLayout(), 'Настройки'),
                   (LoadLayout(), 'Загрузка'),
                   (ParserLayout(), 'Парсинг'),
                   (HandleLayout(), 'Обработка'),
                   (UploadLayout(), 'Выгрузка')]
        widgets = []
        for i in range(len(layouts)):
            screen = ScreenTemplate(name=f'screen{i + 1}')
            screen.text_label.text = f'[size=18]{layouts[i][1]}[/size]'
            screen.main_screen.add_widget(layouts[i][0])
            self._screen_manager.add_widget(screen)
            widgets.append(screen.main_screen.children[0])

        self.settings_widget, self.load_widget, self.parser_widget, self.handle_widget, self.upload_widget = widgets

        self.settings_widget.update()
        self.handle_widget.update()
        self.load_widget.update()

    def set_current_screen(self, screen):
        """
        Used for switches screens buttons.
        Sets current screen.
        :param screen:
        """
        use_threads = [self.load_widget.use_thread, self.parser_widget.use_thread]
        if not any(use_threads):
            self._screen_manager.current = screen
