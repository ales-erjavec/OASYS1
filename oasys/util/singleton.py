import threading

def synchronized_method(method):

    outer_lock = threading.Lock()
    lock_name = "__"+method.__name__+"_lock"+"__"

    def sync_method(self, *args, **kws):
        with outer_lock:
            if not hasattr(self, lock_name): setattr(self, lock_name, threading.Lock())
            lock = getattr(self, lock_name)
            with lock:
                return method(self, *args, **kws)

    return sync_method

class Singleton:
    def __init__(self, decorated):
        self.__decorated = decorated

    @synchronized_method
    def Instance(self, **args):
        try:
            return self.__instance
        except AttributeError:
            self.__instance = self.__decorated(**args)
            return self.__instance

    def __call__(self):
        raise TypeError('Singletons must be accessed through `Instance()`.')

    def __instancecheck__(self, inst):
        return isinstance(inst, self.__decorated)

