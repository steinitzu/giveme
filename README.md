# Giveme 
A python dependency injection framework

[![Build Status](https://travis-ci.org/steinitzu/giveme.svg?branch=master)](https://travis-ci.org/steinitzu/giveme)

# Quickstart

## Basic dependency factories

```python
from giveme import register, inject

@register
def something():
    return 'I am a dependency'
nnnn

@inject
def use_dependency(something):
    return something


print(use_dependency())
# I am a dependency
```

## Singleton factories

Sometimes you want a dependency instantiated only once.  
By using `@register` with the optional `singleton` argument, the factory function is only called on first use, any subsequent injectees will get the previous return value.  
Example:  

```python
from giveme import register, inject

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
```

## Nested dependencies

```python
@register
def something():n
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
```	



