from collections import OrderedDict
def make_SafeOrderedDict(_eletype):
    class _SafeOrderedDict(SafeOrderedDict):
        eletype = _eletype
    return _SafeOrderedDict
class SafeOrderedDict(OrderedDict):
    'Dictionary that remembers insertion order'
    # An inherited dict maps keys to values.
    # The inherited dict provides __getitem__, __len__, __contains__, and get.
    # The remaining methods are order-aware.
    # Big-O running times for all methods are the same as regular dictionaries.

    # The internal self.__map dict maps keys to links in a doubly linked list.
    # The circular doubly linked list starts and ends with a sentinel element.
    # The sentinel element never gets deleted (this simplifies the algorithm).
    # The sentinel is in self.__hardroot with a weakref proxy in self.__root.
    # The prev links are weakref proxies (to prevent circular references).
    # Individual links are kept alive by the hard reference in self.__map.
    # Those hard references disappear when a key is deleted from an OrderedDict.
    eletype = None

    def __setitem__(self, key, value):
        if not isinstance(value, self.eletype):
            raise TypeError(
            f'Setting key {key}, value must be of {self.eletype}'
            f' but found {value.__class__}')
        super().__setitem__( key, value)


import sys
import time
import threading

class Spinner:
    '''
    Source: https://stackoverflow.com/a/39504463/8083313
    '''
    busy = False
    delay = 0.1

    # @staticmethod
    def spinning_cursor(self):
        while 1: 
            dt = time.time() - self.t0
            for cursor in '|/-\\': yield cursor+'[Elapsed]%s %.1fs'%(cursor,dt)

    def __init__(self, delay=None):
        self.t0 = time.time()
        self.spinner_generator = self.spinning_cursor()
        if delay and float(delay): self.delay = delay

    def spinner_task(self):
        while self.busy:
            v = next(self.spinner_generator)
            sys.stdout.write(v)
            sys.stdout.flush()
            time.sleep(self.delay)
            sys.stdout.write('\b'*len(v))
            sys.stdout.flush()

    def __enter__(self):
        self.busy = True
        threading.Thread(target=self.spinner_task).start()

    def __exit__(self, exception, value, tb):
        self.busy = False
        time.sleep(self.delay)
        print(next(self.spinner_generator)+'[task_finised!]')
        # print(self.spinning_cursor())
        if exception is not None:
            return False
