import threading
from functools import wraps
from inspect import signature
import warnings


class DependencyNotFoundError(Exception):
    pass


class DependencyNotFoundWarning(RuntimeWarning):
    pass


ambigious_not_found_msg = (
    'An ambigious DependencyNotFound error occured. '
    'Giveme could not find a dependency '
    'named "{}" but a matching argument'
    'was not passed. '
    'Unable to tell whether you meant to inject '
    'a dependency or simply forgot to pass '
    'the correct arguments.'
)


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
            raise DependencyNotFoundError(name) from None
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
                sig = signature(function)
                params = sig.parameters

                bound = sig.bind_partial(*args, **kwargs)
                bound.apply_defaults()

                injected_kwargs = {}
                for key, value in params.items():
                    if key not in bound.arguments:
                        name = names.get(key)
                        if name:
                            # Raise error when dep named explicitly
                            # and missing
                            injected_kwargs[key] = self.get(name)
                        else:
                            try:
                                injected_kwargs[key] = self.get(key)
                            except DependencyNotFoundError as e:
                                warnings.warn(
                                    ambigious_not_found_msg.format(key),
                                    DependencyNotFoundWarning
                                )
                            
                injected_kwargs.update(bound.kwargs)
                return function(*bound.args, **injected_kwargs)
            return wrapper
        if function:
            return decorator(function)
        return decorator
