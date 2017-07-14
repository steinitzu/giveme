# Giveme 
An easy to use python dependency injection framework.  

The API contains two functions decorators: `@register` to register a dependency factory function and `@inject` to inject a dependency into a function.  
giveme only requires that your injectee accepts and argument named after your dependency. Injected dependencies can also be seamleassly overriden for testing and mocking.  

[![Build Status](https://travis-ci.org/steinitzu/giveme.svg?branch=master)](https://travis-ci.org/steinitzu/giveme)

# Quickstart

## Install

Tested on python 3.4 and up

`pip install giveme`


## Basic dependency factories

```python
from giveme import register, inject

@register
def duck():
    return duck'


@inject
def return_duck(duck=None):  # use a named keyword argument for best results
    return duck


result = return_dependency()  # notice we don't pass any arguments here
print(result)
# duck
```

We can also override the duck dependency manually.  

```python
print(return_duck(duck='goose'))
# goose

```


## Singleton factories

Sometimes you want a dependency instantiated only once.  
By using `@register` with the optional `singleton` argument, the factory function is only called on first use, any subsequent injectees will get the previous return value.  
You can also use `threadlocal=True` instead of singleton so the dependency is a singleton only for the thread that created, this is good for example for things that should be unique in a request context in a web framework like Flask.  
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
def use_dependency(something=None):
    print(something.size)
    something.size = 42


@inject
def use_it_again(something=None):
    print(something.size)


use_dependency()
# 22
use_dependency()
# 42
```

## Nested dependencies

```python
@register
def something():
    return 'I am a dependency'


@register
@inject
def another_thing(something=None):
    return (something, 'So am I')


@inject
def use_dependency(another_thing=None):
    return another_thing


print(use_dependency())
# ('I am a dependency', 'So am i')
```	

# Testing

You can run the included test suite with pytest

1. Clone this repository
2. `cd path/to/giveme`
3. Install pytest -> `pip install pytest`
4. Run the tests -> `pytest tests.py`

# Contributing

If you run into bugs or have questions, don't hesitate to open an issue. Pull requests are always welcome.  
