import threading
import time
from kivy.uix.boxlayout import BoxLayout
from kivy.properties import StringProperty, NumericProperty, ListProperty
from kivy.clock import mainthread
from kivy.app import App

class ParserLayout(BoxLayout):
    message = StringProperty('')
    grid_height = NumericProperty()
    use_thread = False
    results = ListProperty([])
    msg_templates = {'check_procedure': ('Проверка функции {2} модуля {3}.py ошибка: {4}.\n',
                                         'Проверка функции {2} модуля {3}.py прошла успешно.\n',
                                         'Шаг 3',
                                         'Проверка закончена. Нажмите кнопку "Шаг 3".',
                                         'Модуль {err[3]} метод "{err[2]}" результат: {err[4]}.\n'
                                         ),
                     'parsing_category_procedure': ('При работе над файлом {3} произошла ошибка: {2}.\n',
                                                    'Файл {3} успешно сохранен в папке {4}.\n',
                                                    'Шаг 4',
                                                    'Обработка закончена. Нажмите кнопку "Шаг 4".',
                                                    'При работе над файлом {3} произошла ошибка: {2}.\n'),
                     'parsing_item_procedure': ('При работе над файлом {3} произошла ошибка: {2}.\n',
                                                'Файл {3} успешно сохранен в папке {4}.\n',
                                                'Шаг 1',
                                                'Файл {3} успешно сохранен в папке {4}.\nОбработка закончена.',
                                                'При работе над файлом {3} произошла ошибка: {2}.\n')
                     }

    def threads_operation(self, procedure, params: dict, messages: tuple):
        """
        Starts two new threads. First one for graphics, second one for validation parsing functions process.
        :param procedure - name of method
        :param params - a dictionary of elements of the following type
        [url](name_operation, module_name, operation, validator)
        :param messages - start and end messages for threads.
        """
        if not self.use_thread:
            self.use_thread = True
            t1 = threading.Thread(target=self.get_message, args=(messages, ), daemon=True)
            t2 = threading.Thread(target=procedure,
                                  args=(params, self.transfer, self.set_use_thread))
            t1.start()
            t2.start()

    def on_results(self, instance, value):
        """A callback to track changes to property."""
        if self.results:
            result = self.results[-1]
            msg_template = self.msg_templates[result[0]]
            self.console.message = msg_template[int(result[1])].format(*result)

    @mainthread
    def transfer(self, result: tuple):
        """A callback for transfer result."""
        self.results.append(result)

    @mainthread
    def set_use_thread(self, *args):
        """A callback for catching the finishing of validation process."""
        self.use_thread = False
        time.sleep(.5)
        msg_template = self.msg_templates[self.results[-1][0]]
        errors = [res for res in self.results if not res[1]]
        if not errors:
            result = self.results[0]
            self.step_button.text = msg_template[2]
            self.console.message = msg_template[3].format(*result)
            if args:
                app = App.get_running_app()
                app.root.update_handle_widget()
        else:
            message = '\n'.join([msg_template[4].format(*err) for err in errors])
            self.console.message = message + '\nИсправьте ошибки.'
        self.results = []

    def get_message(self, messages: tuple):
        """
        This function use for graphics representation of validation process.
        :param messages - start and end messages for threads.
        """
        counter = 0
        strip = ["     "] * 10
        use_thread = True
        self.set_message(messages[0])
        while use_thread:
            time.sleep(.5)
            index = counter % 10
            strip[index] = " *** "
            self.set_message(''.join(strip))
            strip[index] = "     "
            counter += 1
            use_thread = self.use_thread
        self.set_message(messages[1])

    @mainthread
    def set_message(self, message):
        """A callback for output new message."""
        self.message = message