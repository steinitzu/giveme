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
    
    __slots__ = ('name', 'factory', 'singleton', 'threadlocal')
    
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

    def cache(self, dependency: Dependency, value):
        """
        Store an instance of dependency in the cache.
        Does nothing if dependency is NOT a threadlocal
        or a singleton.  

        :param dependency: The ``Dependency`` to cache
        :param value: The value to cache for dependency

        :type dependency: Dependency
        """
        if dependency.threadlocal:
            setattr(self._local, dependency.name, value)
        elif dependency.singleton:
            self._singleton[dependency.name] = value

    def cached(self, dependency):
        """
        Get a cached instance of dependency.

        :param dependency: The ``Dependency`` to retrievie value for
        :type dependency: ``Dependency``
        :return: The cached value        
        """
        if dependency.threadlocal:
            return getattr(self._local, dependency.name, None)
        elif dependency.singleton:
            return self._singleton.get(dependency.name)

    def _set(self, name, factory, singleton=False, threadlocal=False):
        """
        Add a dependency factory to the registry

        :param name: Name of dependency
        :param factory: function/callable that returns dependency
        :param singleton: When True, makes the dependency a singleton.
            Factory will only be called on first use, subsequent 
            uses receive a cached value.
        :param threadlocal: When True, register dependency as a threadlocal singleton,
            Same functionality as ``singleton`` except :class:`Threading.local` is used
            to cache return values.
        """
        name = name or factory.__name__
        dep = Dependency(name, factory, singleton, threadlocal)
        self._registry[name] = dep

    def get(self, name: str):
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

    def delete(self, name):
        """
        Delete (unregister) a dependency by name.
        """
        del self._registry[name]

    def register(self, function=None, *, singleton=False, threadlocal=False, name=None):
        """
        Add an object to the injector's registry.

        Can be used as a decorator like so:
        
        >>> @injector.register
        ... def my_dependency(): ...

        or a plain function call by passing in a callable
        injector.register(my_dependency)

        :param function: The function or callable to add to the registry
        :param name: Set the name of the dependency. Defaults to the name of `function`
        :param singleton: When True, register dependency as a singleton, this
            means that `function` is called on first use and its 
            return value cached for subsequent uses. Defaults to False
        :param threadlocal: When True, register dependency as a threadlocal singleton,
            Same functionality as ``singleton`` except :class:`Threading.local` is used
            to cache return values.
        :type function: callable
        :type singleton: bool
        :type threadlocal: bool
        :type name: string
        """
        def decorator(function=None):
            self._set(name, function, singleton, threadlocal)
            return function
        if function:
            return decorator(function)
        return decorator

    def inject(self, function=None, **names):
        """
        Inject dependencies into `funtion`'s arguments when called.

        >>> @injector.inject
        ... def use_dependency(dependency_name):
                ...
        >>> use_dependency()

        The `Injector` will look for registered dependencies
        matching named arguments and automatically pass
        them to the given function when it's called.

        :param function: The function to inject into
        :type function: callable
        :param \**names: in the form of ``argument='name'`` to override
            the default behavior which matches dependency names with argument
            names.
        """
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
