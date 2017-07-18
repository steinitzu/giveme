# Giveme: dependency injection for python

[![Build Status](https://travis-ci.org/steinitzu/giveme.svg?branch=master)](https://travis-ci.org/steinitzu/giveme)

Giveme is a general purpose dependency injector for python, heavily inspired pytest's fixtures. Use it to inject databases, API clients, framework pieces or anything else that you don't want tightly coupled to your code.

- [Install](#org492d6de)
- [Usage](#org5d55f59)
  - [Quickstart](#org9880d2f)
  - [Singleton and threadlocal dependencies](#org16b02cc)
  - [Override dependencies](#org0f12126)
- [Testing](#orgd0e861b)
- [Contributing](#orgc75efc6)


<a id="org492d6de"></a>

# Install

Python3.4 and up are supported `pip install giveme`


<a id="org5d55f59"></a>

# Usage


<a id="org9880d2f"></a>

## Quickstart

Here we use giveme to inject a random animal into a function.

```python
import random

from giveme import register, inject


def random_animal_factory():
    animals = ['duck', 'goose', 'horse', 'tiger', 'cow', 'sheep', 'pig']
    return random.choice(animals)


@register
def animal():
    return random_animal_factory()


@inject
def print_animal(animal=None): 
    print("It's a", animal)


print_animal()
print_animal()
print_animal()

```

    It's a sheep
    It's a duck
    It's a pig

By default the `animal` function is called each time it's injected. In this case, each time `print_animal` is called.

We can also inject the animal factory itself:

```python
@register
def animal_factory():
    return random_animal_factory


@inject
def print_animal(animal_factory=None): 
    print("It's a", animal_factory())


print_animal()
print_animal()
print_animal()

```

    It's a cow
    It's a sheep
    It's a pig


<a id="org16b02cc"></a>

## Singleton and threadlocal dependencies

You may want only one instance of something throughout the lifetime of your application, or one instance per thread. `@register` accepts the keyword arguments `singleton` and `threadlocal` to support this.

```python
@register(singleton=True)
def animal():
    return random_animal_factory()


@inject
def print_animal(animal=None): 
    print("It's a", animal)


print_animal()
print_animal()
print_animal()

```

    It's a pig
    It's a pig
    It's a pig

Now `animal` is only called once and every function that injects it gets the same animal. `@register(threadlocal=True)` works the same way, except the animal instance is only available to the thread that created it.


<a id="org0f12126"></a>

## Override dependencies

Injected dependencies can always be overridden by passing a value manually. Great for testing!

```python
@inject
def print_animal(animal=None): 
    print("It's a", animal)


print_animal()
# Manual override, must use the named argument explictly
print_animal(animal='snake')
```

    It's a pig
    It's a snake


<a id="orgd0e861b"></a>

# Testing

You can run the included test suite with pytest

1.  Clone this repository
2.  cd path/to/giveme
3.  Install pytest -> pip install pytest
4.  Run the tests -> pytest tests.py


<a id="orgc75efc6"></a>

# Contributing

If you run into bugs or have questions, please open an issue. Pull requests are welcome.
