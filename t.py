import inspect


class InjectedDependency:
    def __init__(self, value):
        self.value = value

        
        


def inject(name):
    return InjectedDependency(42)
    print(name)

    f = inspect.currentframe().f_back
    f = inspect.stack()[1]
    
    print(f)


def getown(func, *args, **kwargs):
    print(func.__name__)
    return func(*args, **kwargs)

import random

class Injector:
    def get(self, name):
        return random.randint(0, 20)

    def get_later(self, name, persist_on=None):
        return DeferredProperty(
                self, name, persist_on=persist_on
            )


class DeferredProperty:
    def __init__(self, injector, name, persist_on=None):
        self.injector = injector
        self.name = name
        self.injector = injector
        self.persisted = False
        self.cached = None
        self.persist_on = persist_on

    def __get__(self, destobj, *args, **kwargs):
        if not self.persisted:
            val = self.injector.get(self.name)
            if self.persist_on:
                setattr(destobj, self.persist_on, val)
                self.persisted = True
                return val
            self.persisted = True            
            self.cached = val
        return self.cached


injector = Injector()


class Something:

    b = injector.get_later('depname', 'b')
    c = injector.get_later('depname', 'c')

    def __init__(self):
        pass

    

x = Something()
print(x.b)
print(x.b)
print(x.c)
print(x.c)
