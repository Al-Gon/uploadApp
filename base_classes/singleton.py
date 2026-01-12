from threading import Lock

class Singleton(object):
    _lock: Lock = Lock()

    def __new__(cls, *args, **kwargs):
        with cls._lock:
            if not hasattr(cls, 'instance'):
                cls.instance = super(Singleton, cls).__new__(cls)
        return cls.instance