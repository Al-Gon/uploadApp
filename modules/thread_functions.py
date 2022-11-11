import threading
import time
from kivy.clock import mainthread

def threads_operation(obj, procedure, set_message, params: dict, messages: tuple):
    """
    Starts two new threads. First one for graphics, second one for validation parsing functions process.
    :param obj: object
    :param set_message: object callback function for the output message during execution of the t2 thread.
    :param procedure - name of method
    :param params - a dictionary of elements of the following type
    [url](name_operation, module_name, operation, validator)
    :param messages - start and end messages for threads.
    """
    if not obj.use_thread:
        obj.use_thread = True
        t1 = threading.Thread(target=get_message, args=(obj, set_message, messages), daemon=True)
        t2 = threading.Thread(target=procedure,
                              args=(obj, params, transfer, set_use_thread))
        t1.start()
        t2.start()


@mainthread
def transfer(obj, result: tuple):
    """A callback for adding result to the object property."""
    obj.results.append(result)


@mainthread
def set_use_thread(obj, *args):
    """A callback for catching the finishing of validation process."""
    obj.use_thread = False
    time.sleep(.5)
    obj.output_procedure_result(*args)


def get_message(obj, set_message, messages: tuple):
    """
    This function use for graphics representation of validation process.
    :param obj: object
    :param set_message: object callback function for the output message.
    :param messages - start and end messages for threads.
    """
    counter = 0
    strip = ["     "] * 10
    set_message(messages[0])
    while obj.use_thread:
        time.sleep(.5)
        index = counter % 10
        strip[index] = " *** "
        set_message(''.join(strip))
        strip[index] = "     "
        counter += 1
    set_message(messages[1])