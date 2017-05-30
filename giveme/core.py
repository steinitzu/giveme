import inspect

from functools import wraps
import threading


class Manager(object):

    def __init__(self):
        self._registered = {}
        self._singletons = {}
        self._threadlocals = threading.local()

    def register(self, func, singleton=False, threadlocal=False):
        """
        Register a dependency function
        """
        func._giveme_singleton = singleton
        func._giveme_threadlocal = threadlocal
        
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


def register(function=None, singleton=False, threadlocal=False):
    """
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
    """
    def decorator(function):
        return manager.register(function, singleton=singleton, threadlocal=threadlocal)
    if function:
        return decorator(function)
    else:
        return decorator


def inject(func):
    """
    Inject a dependency into given function's arguments.  
    Can be used as a decorator.

    Args: 
        func (callable): The function that accepts a dependency.
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        signature = inspect.signature(func)
        params = signature.parameters
        if not params:
            return func(*args, **kwargs)
        args = list(args)
        if len(args)+len(kwargs) == len(params):
            return func(*args, **kwargs)
        for i, param in enumerate(signature.parameters):
            try:
                service = manager.get_value(param)
            except KeyError:
                continue
            args.insert(i, service)
        return func(*args, **kwargs)
    return wrapper
