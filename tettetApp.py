from kivy.uix.boxlayout import BoxLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.properties import StringProperty, ListProperty, ObjectProperty
from kivy.clock import mainthread
from kivy.app import App
import time
import threading
from modules import parser_functions as pr


# def procedure1(urls, f):
#     driver = get_driver()
#     count = 0
#     for url in urls:
#         driver.get(url)
#         count += 1
#     driver.close()
#     f(count)

class InputBlock(FloatLayout):
    input_string = StringProperty('')
    # transfer_name = StringProperty('')
    #
    # def handle_path(self, name):
    #     self.transfer_name = name

class Tettet(BoxLayout):
    message = StringProperty('Not yet.')
    result = ListProperty([])

    def __init__(self, **kwargs):
        super(Tettet, self).__init__(**kwargs)
        # self.save_dir_path = ObjectProperty()
        self.save_dir_path.button_.bind(on_release=self.handle)

    def handle(self):
        print(self.save_dir_path.button_.name)



    # use_thread = False


    # def play(self, name):
    #     if name == 'Шаг 1':
    #         if not self.use_thread:
    #             self.use_thread = True
    #             t1 = threading.Thread(target=self.get_message, daemon=True)
    #             t2 = threading.Thread(target=pr.procedure1,
    #                                   args=(['https://www.mail.ru', 'https://www.ya.ru'] * 10, self.set_use_thread))
    #             t1.start()
    #             t2.start()
    #     if name == 'Шаг 2':
    #         print('I am here.')
    #         self.message = f'Your result is: {str(self.result[0])}'
    #
    # def on_result(self, instance, value):
    #     # print(self.result)
    #     self.my_button.name = 'Шаг 2'
    #
    # @mainthread
    # def set_use_thread(self, count):
    #     self.use_thread = False
    #     self.result.append(count)
    #
    # def get_message(self):
    #     counter = 0
    #     message = ["     "] * 5
    #     use_thread = True
    #     self.set_message("Начало проверки.")
    #     while use_thread:
    #         time.sleep(1)
    #         index = counter % 5
    #         message[index] = " *** "
    #         self.set_message(''.join(message))
    #         message[index] = "     "
    #         counter += 1
    #         use_thread = self.use_thread
    #     self.set_message("Конец проверки.")
    #
    # @mainthread
    # def set_message(self, message):
    #     self.message = message




class TettetApp(App):

    def build(self):
        return Tettet()


if __name__ == '__main__':
    TettetApp().run()