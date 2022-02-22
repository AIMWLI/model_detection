from functools import wraps
from threading import Thread
def convert_to_thread(thread=None):
    if thread is None:
        thread = Thread
    def _convert_to_thread(cls):
        base = cls.__base__
        # base += (thread, )
        return type(cls.__name__, (base,), cls.__attributes__)
    return _convert_to_thread

class BaseTest(object):pass
class BaseTest_(object):pass

@convert_to_thread()
class Test(BaseTest, BaseTest_):
    def __init__(self):
        pass

if __name__ == '__main__':
    t = Test()
    t.start()


