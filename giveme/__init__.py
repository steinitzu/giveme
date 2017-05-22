import inspect

from functools import wraps


class Manager(object):

    def __init__(self):
        self._registered = {}
        self._singletons = {}

    def register(self, func, singleton=False):
        """
        Register a dependency function
        """
        func._giveme_singleton = singleton
        self._registered[func.__name__] = func
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
        value = self._singletons.get(name)
        if value:
            return value
        function = self._registered.get(name)

        if function:
            value = function()
            if function._giveme_singleton:
                self._singletons[name] = value
            return value
        raise KeyError('Name not found')

    def clear(self):
        self._registered = {}
        self._singletons = {}


manager = Manager()


def register(function=None, singleton=False):
    def decorator(function):
        return manager.register(function, singleton=singleton)
    if function:
        return decorator(function)
    else:
        return decorator


def inject(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        signature = inspect.signature(func)
        params = signature.parameters
        if not params:
            return func(*args, **kwargs)
        args = list(args)
        for i, param in enumerate(signature.parameters):
            try:
                service = manager.get_value(param)
            except KeyError:
                continue
            args.insert(i, service)
        return func(*args, **kwargs)
    return wrapper
