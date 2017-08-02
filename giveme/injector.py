import threading
from functools import wraps
from inspect import signature as get_signature


class DependencyNotFound(Exception):
    pass


class Dependency:
    def __init__(self, name, factory, singleton=False, threadlocal=False):
        self.name = name
        self.factory = factory
        self.singleton = singleton
        self.threadlocal = threadlocal

    
class Injector:

    def __init__(self):
        self._local = threading.local()
        self._singleton = {}
        self._registry = {}

    def cache(self, dependency, value):
        """
        Cache instance of dependency.
        """
        if dependency.threadlocal:
            setattr(self._local, dependency.name, value)
        elif dependency.singleton:
            self._singleton[dependency.name] = value

    def cached(self, dependency):
        """
        Get a cached instance of dependency.
        """
        if dependency.threadlocal:
            return getattr(self._local, dependency.name, None)
        elif dependency.singleton:
            return self._singleton.get(dependency.name)

    def set(self, name, factory, singleton=False, threadlocal=False):
        name = name or factory.__name__
        dep = Dependency(name, factory, singleton, threadlocal)
        self._registry[name] = dep

    def get(self, name):
        """
        Get an instance of dependency,
        this can be either a cached instance
        or a new one (in which case the factory is called)
        """
        dep = None
        try:
            dep = self._registry[name]
        except KeyError:
            raise DependencyNotFound(name)
        value = self.cached(dep)
        if value is None:
            value = dep.factory()
            self.cache(dep, value)
        return value
        
    def exists(self, name):
        return name in self._registry

    def delete(self, name):
        del self._registry[name]

    def register(self, function=None, *, singleton=False, threadlocal=False, name=None):
        def decorator(function=None):
            self.set(name, function, singleton, threadlocal)
            return function
        if function:
            return decorator(function)
        return decorator

    def inject(self, function=None, **names):
        def decorator(function):
            @wraps(function)
            def wrapper(*args, **kwargs):
                signature = get_signature(function)
                params = signature.parameters
                if not params:
                    return function(*args, **kwargs)
                for name, param in params.items():
                    ptypes = (param.KEYWORD_ONLY, param.POSITIONAL_OR_KEYWORD)
                    if param.kind not in ptypes:
                        continue
                    if name in kwargs:
                        # Manual override, ignore it
                        continue
                    try:
                        resolved_name = names.get(name, name)
                        kwargs[name] = self.get(resolved_name)
                    except DependencyNotFound:
                        pass
                return function(*args, **kwargs)
            return wrapper
        if function:
            return decorator(function)
        return decorator
