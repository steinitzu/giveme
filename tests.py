import pytest
from functools import wraps

from giveme import register, inject, manager


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

    
        
    

    
