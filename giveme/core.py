"""
:deprecated: 1.0.0
"""

import inspect
from functools import wraps
import threading
import warnings


class Manager(object):
    """
    :deprecated: 1.0.0
    """

    def __init__(self):
        self._registered = {}
        self._singletons = {}
        self._threadlocals = threading.local()

    def register(self, func, singleton=False, threadlocal=False, name=None):
        """
        Register a dependency function
        """
        func._giveme_singleton = singleton
        func._giveme_threadlocal = threadlocal

        if name is None:
            name = func.__name__
        self._registered[name] = func
        return func

    def remove(self, name):
        """
        Remove a dependency by name
        """
        del self._registered[name]

    def get(self, name):
        """
        Get a dependency factory by name, None if not registered
        """
        return self._registered.get(name)

    def get_value(self, name):
        """
        Get return value of a dependency factory or
        a live singleton instance.
        """
        factory = self._registered.get(name)
        if not factory:
            raise KeyError('Name not registered')
        if factory._giveme_singleton:
            if name in self._singletons:
                return self._singletons[name]
            self._singletons[name] = factory()
            return self._singletons[name]
        elif factory._giveme_threadlocal:
            if hasattr(self._threadlocals, name):
                return getattr(self._threadlocals, name)
            setattr(self._threadlocals, name, factory())
            return getattr(self._threadlocals, name)
        return factory()

    def clear(self):
        self._registered = {}
        self._singletons = {}


manager = Manager()


def register(function=None, *, singleton=False, threadlocal=False, name=None):
    """
    :deprecated: 1.0.0
    Use :class:`giveme.injector.Injector` instead.

    Register a dependency factory in the dependency manager. The function name is the
    name of the dependency.
    This can be used as a decorator.

    Args:
        function (callable): The dependency factory function
            Not needed when used as decorator.
        singleton (``bool``, optional): If ``True`` the given function is only called once
            during the application lifetime. Injectees will receive the already created
            instance when available. Defaults to ``False``
        threadlocal (``bool``, optional): Same as singleton except the returned instance
            is available only to the thread that created it. Defaults to ``False``
        name (``str``, optional): Overridden name for the dependency.
            Defaults to the name of the registered function.
    """
    warnings.warn(
        (
            'Module level `register` decorator has been deprecated and will '
            'be removed in a future release. '
            'Use the Injector class instead'
        ),
        DeprecationWarning
    )

    def decorator(function):

        return manager.register(function, singleton=singleton, threadlocal=threadlocal, name=name)
    if function:
        return decorator(function)
    else:
        return decorator


def inject(function=None, **overridden_names):
    """
    :deprecated: 1.0.0
    Use :class:`giveme.injector.Injector` instead.

    Inject dependencies into given function's arguments.
    By default the injector looks for keyword arguments
    matching registered dependency names.

    Example:

        @register
        def db_connection():
            return create_db_connection()

        @inject
        def save_thing(thing, db_connection=None):
            db_connection.store(thing)

    Arbitrary arguments may also be mapped to
    specific dependency names by passing them to the
    decorator as ``arg='dependency_name'``

    Example:
        @inject(db='db_connection')
        def save_thing(thing, db=None):  # `db_connection` injected as `db`

    Args:
        function (callable): The function that accepts a dependency.
            Implicitly passed when used as a decorator.
        **overridden_names: Mappings of `function` arguments to
            dependency names in the form of ``function_argument='dependency name'``
    """
    warnings.warn(
        (
            'Module level `inject` decorator has been deprecated and will '
            'be removed in a future release. '
            'Use the Injector class instead'
        ),
        DeprecationWarning
    )
    
    def decorator(function):        
        @wraps(function)
        def wrapper(*args, **kwargs):
            signature = inspect.signature(function)
            params = signature.parameters
            if not params:
                return function(*args, **kwargs)
            for name, param in params.items():
                if param.kind not in (param.KEYWORD_ONLY, param.POSITIONAL_OR_KEYWORD):
                    continue
                if name in kwargs:
                    # Manual override, ignore it
                    continue
                try:
                    resolved_name = overridden_names.get(name, name)
                    kwargs[name] = manager.get_value(resolved_name)
                except KeyError:
                    pass
            return function(*args, **kwargs)
        return wrapper
    if function:
        return decorator(function)
    else:
        return decorator
