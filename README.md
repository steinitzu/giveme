# Giveme 
A python dependency injection framework

[![Build Status](https://travis-ci.org/steinitzu/giveme.svg?branch=master)](https://travis-ci.org/steinitzu/giveme)

# Quickstart

```python
from giveme import register, inject

@register
def something():
    return 'I am a dependency'


@inject
def use_dependency(something):
    return something


print(use_dependency())
# I am a dependency
```

# Nested dependencies

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



