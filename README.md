- [Documentation](#org7e529b6)
- [Quick start](#org07a14b0)
- [Install](#orgfce85dd)
- [Changes in version 1.0](#orgd8ed99f)
  - [Migrating from <1.0](#org4c92880)
- [Testing](#orgdce1e44)
- [Contributing](#org6ef425e)

[![Build Status](https://travis-ci.org/steinitzu/giveme.svg?branch=master)](https://travis-ci.org/steinitzu/giveme)

# Giveme: dependency injection for python

GiveMe is a simple, no-nonsense dependency injection framework for python.

Its features include:

-   Simple `register` and `inject` decorators to register dependency factories or classes and inject their return value into other function/method arguments.
-   Painfree configuration for singleton and thread local dependencies
-   Injected dependencies can always be overridden by manually passed arguments (great for testing)


<a id="org7e529b6"></a>

# Documentation

Examples and API documentation can be found on ReadTheDocs: <https://giveme.readthedocs.io>


<a id="org07a14b0"></a>

# Quick start

```python
from giveme import Injector

injector = Injector()

@injector.register
def magic_number():
    return 42

@injector.inject
def multiply(n, magic_number):
    return n*magic_number

multiply(2)
```

```python
84
```

GiveMe has many more advanced options, for more examples and full API documentation please visit <https://giveme.readthedocs.io>


<a id="orgfce85dd"></a>

# Install

`pip install giveme`

Python3.5 and up are supported.


<a id="orgd8ed99f"></a>

# Changes in version 1.0

GiveMe has received some improvements in 1.0:

-   New `Injector` class with `register` and `inject` decorators as instance methods. To support more than one dependency registry in a project.
-   Module level decoraters `giveme.register` and `giveme.inject` have been deprecated, `Injector.register` and `Injector.inject` should be used instead.
-   Vastly improved argument binding in `Injector.inject` which acts in accordance to default python argument binding. Better distinction between injected arguments and manually passed arguments.
-   `DependencyNotFoundError` thrown from `inject` when an explicitly mapped (e.g. arg<sub>name</sub>='dependency<sub>name</sub>') dependency is not registered or passed in manually for easier debugging
-   `DependencyNotFoundWarning` raised in ambigious cases where an argument is not explicitly mapped to dependency and not passed in manually.


<a id="org4c92880"></a>

## Migrating from <1.0

The API is mostly the same. If you were using the module levels decorators in a standard way before:

```python
from giveme import register, inject

@register
def something():
    ...

@inject
def do_stuff(something):
    ...
```

The only change you'll have to make is to create an instance of `Injector` and use its instance method decorators instead:

```python
from giveme import Injector

injector = Injector()

@injector.register
def something():
    ...

@injector.inject
def do_stuff(something):
    ...
```


<a id="orgdce1e44"></a>

# Testing

You can run the included test suite with pytest

1.  Clone this repository
2.  cd path/to/giveme
3.  Install pytest -> `pip install pytest`
4.  Run the tests -> `pytest tests.py`


<a id="org6ef425e"></a>

# Contributing

Pull requests are welcome. Please post any bug reports, questions and suggestions to the issue tracker <https://github.com/steinitzu/giveme/issues>
