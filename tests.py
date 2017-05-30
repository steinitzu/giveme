import pytest
import time
from functools import wraps
from multiprocessing.pool import ThreadPool

from giveme import register, inject


def test_inject():
    @register
    def something():
        return 124

    @inject
    def do_some(something):
        return something

    assert do_some() == 124


def test_with_other_params():
    @register
    def something():
        return 124

    @inject
    def do_some(a, something, b):
        return a, something, b

    assert do_some(2, 4) == (2, 124, 4)


def test_with_kwargs():
    @register
    def something():
        return 124

    @inject
    def do_some(a, something, b, c=7):
        return a, something, b, c

    assert do_some(2, 4) == (2, 124, 4, 7)
    assert do_some(2, 4, c=12) == (2, 124, 4, 12)
    assert do_some(2, 4, 12) == (2, 124, 4, 12)


def test_manual_override():
    @register
    def something():
        return 5

    @inject
    def do_some(something, n):
        return something, n

    assert do_some(something=2, n=3) == (2, 3)

    
def test_manual_overrideb():
    @register
    def something():
        return 5

    @inject
    def do_some(n, something, k=3):
        return n, something, k

    assert do_some(1, 2, 3) == (1, 2, 3)
    assert do_some(n=1, something=2, k=3) == (1, 2, 3)


def test_nested():
    @register
    def something():
        return 128

    @register
    @inject
    def something_else(something):
        return something*2

    @inject
    def do_some(something_else):
        return something_else

    assert do_some() == 128*2


def test_with_outside_decorator():
    @register
    def something():
        return 128

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            kwargs['c'] = 'changed'
            return func(*args, **kwargs)
        return wrapper

    @inject
    @decorator
    def do_some(a, something, c='original'):
        return a, something, c

    @decorator
    @inject
    def do_some_flipped(a, something, c='original'):
        return a, something, c

    assert do_some(12) == (12, 128, 'changed')
    assert do_some_flipped(12) == (12, 128, 'changed')


def test_instance_method():
    @register
    def something():
        return 128

    class SomeClass(object):

        @inject
        def do_some(self, something):
            return something

    s = SomeClass()
    assert s.do_some() == 128


def test_not_singleton():
    class Something(object):
        def __init__(self):
            self.size = 22

    @register
    def something():
        return Something()

    @inject
    def do_some(something):
        something.size = 42
        return something

    @inject
    def do_some_again(something):
        return something

    assert do_some() is not do_some_again()
    assert do_some().size == 42 and do_some_again().size == 22


def test_singleton():
    class Something(object):
        def __init__(self):
            self.size = 22

    @register(singleton=True)
    def something():
        return Something()

    @inject
    def do_some(something):
        something.size = 42
        return something

    @inject
    def do_some_again(something):
        return something

    assert do_some() is do_some_again()
    assert do_some().size == 42 and do_some_again().size == 42


def test_threadlocal():
    @register(threadlocal=True)
    def something():
        return [1, 2, 3]

    @inject
    def do_some(something, add):
        time.sleep(0.5)  # Make sure they run in separate threads
        something.append(add)
        return something

    tp = ThreadPool()

    t1 = tp.apply_async(do_some, args=(4, ))
    t2 = tp.apply_async(do_some, args=(5, ))

    r1 = t1.get()
    r2 = t2.get()

    assert r1 == [1, 2, 3, 4]
    assert r2 == [1, 2, 3, 5]


def test_no_decorator():
    def something():
        return [1, 2, 3]

    def do_some(something):
        something.append(4)
        return something

    register(something)
    do_some = inject(do_some)

    assert do_some() == [1, 2, 3, 4]
