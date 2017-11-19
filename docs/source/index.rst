.. giveme documentation master file, created by
   sphinx-quickstart on Fri Nov 24 16:36:30 2017.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to giveme's documentation!
==================================
.. toctree::
   :maxdepth: 2
   :caption: Contents:


Giveme is a dependency injection framework for python.
It gives you the tools to separate external services, such as database wrappers and web frameworks from
your business logic.


Quickstart
==========

The :py:class:`~giveme.injector.Injector` class is at the heart of giveme.
It acts as a dependency registry and injects dependencies into function
arguments.

You register a dependency factory using its :py:meth:`~giveme.injector.Injector.register` decorator
and inject a dependency into a another function or method using
the :py:meth:`~giveme.injector.Injector.inject` decorator.


.. code-block:: python
                
    from giveme import Injector

    injector = Injector()

    @injector.register
    def magic_number():
        return 42

    @injector.inject
    def double_number(magic_number):
        return magic_number*2

    double_number()


.. testoutput::

   84   
   
Dependency cache (singleton and thread local dependencies)
============================================

By default, the injector calls the dependency factory every time its used.
So in the example above, ``magic_number()`` is called every time you call
``double_number`` without arguments

In the real world, your dependencies are generally more complex objects that may involve
network calls that are expensive to initalize or carry some kind of state that you want to persist
between uses.

Using :py:meth:`~giveme.injector.Injector.register` with the ``singleton`` argument achieves this
by only calling the dependency factory the first time it's used, after that its return value
is cached for subsequent uses. E.g.

.. code-block:: python

   @injector.register(singleton=True)
   def number_list():
       return [1, 2, 3]

   @injector.inject
   def increment_list(number_list):
       for i in range(len(number_list)):
           number_list[i] += 1
       return number_list

   print(increment_list())
   print(increment_list())

.. code-block:: python

   [2, 3, 4]
   [3, 4, 5]

Every call to ``increment_list()`` operates on the same instance of ``number_list()``

``threadlocal`` can also be used for the same effect, that makes the dependency cache
use ``Threading.local`` storage behind the scenes so that each instance of a dependency is
only available to the thread that created it.


Naming dependencies
===================

By default :py:meth:`~giveme.injector.Injector.register` uses the name of the
decorated function as the dependency name.

This can be overriden using the ``name`` keyword argument:

.. code-block:: python

    @injector.register(name='cache_wrapper')
    def redis_cache():
        ...


When injecting :py:meth:`~giveme.injector.Injector.inject` matches dependency names
to the decorated function's arguments.  
This can also be overriden by passing any number of keyword arguments in the
format of ``argument_name='dependency_name'``

Example:

.. code-block:: python

    @injector.inject(cache='cache_wrapper')
    def do_cache_stuff(cache):
        # cache receives the 'cache_wrapper' dependency
        ...

Nested dependencies
===================

A dependency may have its own dependencies. For instance you might have two database wrappers that share a
database connection (pool).
Luckily you can inject dependencies into other dependencies same as anything else, e.g.:


.. code-block:: python

   import redis


   @injector.register(singleton=True)   
   def redis_client():
       return redis.Redis.from_url('my_redis_url')


   @injector.register(singleton=True)
   @injector.inject
   def cache(redis_client):
       return MyRedisCache(redis_client)


   @injector.register(singleton=True)
   @injector.inject
   def session_store(redis_client):
       return MyRedisSessionStore(redis_client)



You can now inject ``cache`` or ``session_store`` into other functions and both will use the same ``Redis`` instance
behind the scenes.


Argument binding
================

:py:meth:`~giveme.injector.Injector.inject` handles any combination of injected and manually passed
arguments and it only injects for arguments that are not explicitly passed in.
Ordering does not matter beyond python's regular argument order rules.


E.g. This works as expected:

.. code-block:: python

    @injector.register
    def something():
        return 'This is a dependency'
    
    
    @injector.inject
    def do_something(a, *args, something, b=100, c=200, **kwargs):
        return a, args, something, b, c, kwargs

    do_something(1, 2, 3, 4, 5, b=200, c=300, x=55)


And to override the dependency

.. code-block:: python

    do_something(1, 2, 3, 4, 5, something='overriden dependency', b=200, c=300, x=55)



Bypass injection
==================

Dependency injection can always be bypassed by manually passing in replacement values for their
respective arguments.

For instance in our ``increment_list`` function above:

.. code-block:: python

    print(increment_list())
    print(increment_list([0, 0, 0])

.. code-block:: python

   [2, 3, 4]
   [1, 1, 1]


API reference
=============

:mod:`giveme.injector`
=======================

.. automodule:: giveme.injector
    :members:
    :undoc-members:
    :special-members: __init__
    :show-inheritance:


Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
       
