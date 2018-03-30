import inspect
from weakref import WeakKeyDictionary


class DeferredProperty:
    def __init__(self, getter):
        self._getter = getter
        self._cache = WeakKeyDictionary()

    def __get__(self, obj, owner, *a, **kw):
        if not obj:
            return self
        cache = self._cache
        if obj in cache:
            return cache[obj]
        cache[obj] = value = self._getter()
        return value


