from giveme import register, inject
from giveme.core import manager

# Basic


@register
def something():
    return 'I am a dependency'


@inject
def use_dependency(something):
    return something


print(use_dependency())
# I am a dependency

assert use_dependency() == something()

# Singleton


class DependencyClass(object):
    def __init__(self):
        self.size = 21

        
@register(singleton=True)
def something():
    return DependencyClass()


@inject
def use_dependency(something):
    print(something.size)
    something.size = 42


@inject
def use_it_again(something):
    print(something.size)


use_dependency()
# 22
use_dependency()
# 42

# Nested

manager.clear()


@register
def something():
    return 'I am a dependency'


@register
@inject
def another_thing(something):
    return (something, 'So am I')


@inject
def use_dependency(another_thing):
    return another_thing


print(use_dependency())
# ('I am a dependency', 'So am i')

assert use_dependency() == ('I am a dependency', 'So am I')
