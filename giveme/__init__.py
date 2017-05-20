import inspect

from functools import wraps


class Manager(object):

    def __init__(self):
        self._registered = {}

    def register(self, func):
        """
        Register a dependency function
        """
        self._registered[func.__name__] = func
        return func

    def remove(self, name):
        """
        Remove a dependency by name
        """
        del self._registered[name]

    def get(self, name):
        """
        Get a dependency by name, None if not registered
        """
        return self._registered.get(name)


manager = Manager()


def register(func):
    return manager.register(func)


def inject(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        signature = inspect.signature(func)
        params = signature.parameters
        if not params:
            return func(*args, **kwargs)
        args = list(args)
        for i, param in enumerate(signature.parameters):
            service = manager.get(param)
            if not service:
                continue
            args.insert(i, service())
        return func(*args, **kwargs)
    return wrapper
