[![Build Status](https://travis-ci.org/steinitzu/giveme.svg?branch=master)](https://travis-ci.org/steinitzu/giveme)

# Giveme: dependency injection for python

Giveme is a general purpose dependency injector for python, heavily inspired pytest's fixtures.  
Use it to inject databases, API clients, framework pieces or anything else that you don't want tightly coupled
to your code.

- [Install](#org53cfba9)
- [Usage](#orgce81443)
  - [Quickstart](#orgdbe7ef4)
  - [Singleton and threadlocal dependencies](#org2e1bcce)
  - [Override dependencies](#orgb3c77d1)
  - [Naming dependencies](#org859df28)
- [Testing](#org78420ca)
- [Contributing](#org4d66ef7)


<a id="org53cfba9"></a>

# Install

Python3.4 and up are supported `pip install giveme`


<a id="orgce81443"></a>

# Usage


<a id="orgdbe7ef4"></a>

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

    It's a cow
    It's a goose
    It's a cow

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

    It's a pig
    It's a horse
    It's a sheep


<a id="org2e1bcce"></a>

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

    It's a horse
    It's a horse
    It's a horse

Now `animal` is only called once and every function that injects it gets the same animal. `@register(threadlocal=True)` works the same way, except the animal instance is only available to the thread that created it.


<a id="orgb3c77d1"></a>

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

    It's a horse
    It's a snake


<a id="org859df28"></a>

## Naming dependencies

By default when using `@register` , the dependency is named after the decorated function. To override this a custom name can be passed using the `name` keyword argument:

```python
@register(name='cache_db')
def redis_client():
    return MyRedisClient()p

@inject
def do_cache_stuff(cache_db=None):
    ...
```

`@inject` binds registered dependency names to argument names by default. You can override this behavior and specify which dependencies are injected into which arguments by passing pairs of `argument_name='dependency_name'` to `@inject`

Example:

```python
@inject(db='cache_db')
def do_cache_stuff(db=None):
    # db is cache_db
    ...
```


<a id="org78420ca"></a>

# Testing

You can run the included test suite with pytest

1.  Clone this repository
2.  cd path/to/giveme
3.  Install pytest -> pip install pytest
4.  Run the tests -> pytest tests.py


<a id="org4d66ef7"></a>

# Contributing

If you run into bugs or have questions, please open an issue. Pull requests are welcome.
