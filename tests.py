import pytest
import time
import inspect
from functools import wraps
from multiprocessing.pool import ThreadPool

from giveme import register, inject, DependencyNotFoundError


def test_inject():
    @register
    def something():
        return 124

    @inject
    def do_some(something=None):
        return something

    assert do_some() == 124


def test_with_other_params():
    @register
    def something():
        return 124

    @inject
    def do_some(a, b, something=None):
        return a, b, something

    assert do_some(2, 4) == (2, 4, 124)


def test_with_kwargs():
    @register
    def something():
        return 124

    @inject
    def do_some(a, b, something=None, c=7):
        return a, b, something, c

    assert do_some(2, 4) == (2, 4, 124, 7)
    assert do_some(2, 4, c=12) == (2, 4, 124, 12)


def test_manual_override_kwargs():
    @register
    def something():
        return 'something'

    @inject
    def do_some(a, b=2, something=None, **kwargs):
        return a, b, something, kwargs

    assert do_some(2, b=3, something='nothing', c=4) == (2, 3, 'nothing', {'c': 4})
    assert do_some(1, 2, something='nothing') == (1, 2, 'nothing', {})


def test_manual_override_args_kwargs():
    @register
    def something():
        return 'something'

    @inject
    def do_some(*args, something=None, **kwargs):
        return args, something, kwargs
    r4 = tuple(range(4))
    assert do_some(*r4) == (r4, 'something', {})
    assert do_some(*r4, a='a') == (r4, 'something', {'a': 'a'})


def test_nested():
    @register
    def something():
        return 128

    @register
    @inject
    def something_else(something=None):
        return something*2

    @inject
    def do_some(something_else=None):
        return something_else

    assert do_some() == 128*2


def test_with_outside_decorator():
    @register
    def something():
        return 128

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            kwargs['c'] = 'changed'
            return func(*args, **kwargs)
        return wrapper

    @inject
    @decorator
    def do_some(a, something, c='original'):
        return a, something, c

    @decorator
    @inject
    def do_some_flipped(a, something, c='original'):
        return a, something, c

    assert do_some(12) == (12, 128, 'changed')
    assert do_some_flipped(12) == (12, 128, 'changed')


def test_instance_method():
    @register
    def something():
        return 128

    class SomeClass(object):

        @inject
        def do_some(self, something):
            return something

    s = SomeClass()
    assert s.do_some() == 128


def test_not_singleton():
    class Something(object):
        def __init__(self):
            self.size = 22

    @register
    def something():
        return Something()

    @inject
    def do_some(something):
        something.size = 42
        return something

    @inject
    def do_some_again(something):
        return something

    assert do_some() is not do_some_again()
    assert do_some().size == 42 and do_some_again().size == 22


def test_singleton():
    class Something(object):
        def __init__(self):
            self.size = 22

    @register(singleton=True)
    def something():
        return Something()

    @inject
    def do_some(something):
        something.size = 42
        return something

    @inject
    def do_some_again(something):
        return something

    assert do_some() is do_some_again()
    assert do_some().size == 42 and do_some_again().size == 42


def test_threadlocal():
    @register(threadlocal=True)
    def something():
        return [1, 2, 3]

    @inject
    def do_some(add, something=None):
        time.sleep(0.5)  # Make sure they run in separate threads
        something.append(add)
        return something

    tp = ThreadPool()

    t1 = tp.apply_async(do_some, args=(4, ))
    t2 = tp.apply_async(do_some, args=(5, ))

    r1 = t1.get()
    r2 = t2.get()

    assert r1 == [1, 2, 3, 4]
    assert r2 == [1, 2, 3, 5]


def test_no_decorator():
    def something():
        return [1, 2, 3]

    def do_some(something):
        something.append(4)
        return something

    register(something)
    do_some = inject(do_some)

    assert do_some() == [1, 2, 3, 4]


def test_inject_name_override():
    @register
    def dependency():
        return 1

    @inject(d='dependency')
    def do(d):
        return d

    assert do() == 1


# New Injector API

from giveme import Injector
from giveme.deferredproperty import DeferredProperty


@pytest.fixture
def gm():
    return Injector()


def simple_dep():
    return 42


def double_dep(simple_dep):
    return simple_dep*2


def double_f(a, b, c, double_dep):
    return a, b, c, double_dep


def simple_f(a, b, c, simple_dep):
    return a, b, c, simple_dep


def kwargs_f(a, b, c, simple_dep, d=4):
    return a, b, c, simple_dep, d


def varargs_f(*args, simple_dep):
    return tuple(list(args)+[simple_dep])


def list_dep():
    return [1,2,3,4]


def list_f(list_dep):
    return list_dep


class DepClass:
    def __init__(self):
        self.param = 42


def test_simple_f(gm):
    gm.register(simple_dep)
    result = gm.inject(simple_f)(11, 22, 33)
    assert result == (11, 22, 33, 42)


def test_kwargs_f(gm):
    gm.register(simple_dep)
    result = gm.inject(kwargs_f)(1, 2, 3, d=5)
    assert result == (1, 2, 3, 42, 5)


def test_dep_override_positional(gm):
    gm.register(simple_dep)
    result = gm.inject(simple_f)(1, 2, 3, 4)
    assert result == (1, 2, 3, 4)


def test_dep_override_kw(gm):
    gm.register(simple_dep)
    result = gm.inject(simple_f)(1, 2, 3, simple_dep=4)
    assert result == (1, 2, 3, 4)


def test_nested_dep(gm):
    gm.register(simple_dep)
    gm.register(gm.inject(double_dep))
    result = gm.inject(double_f)(1, 2, 3)
    assert result == (1, 2, 3, 42*2)


def test_with_varargs(gm):
    gm.register(simple_dep)
    result = gm.inject(varargs_f)(1, 2, 3, 4)
    assert result == (1, 2, 3, 4, 42)


def test_class_dependency(gm):
    gm.register(DepClass, name='simple_dep')
    result = gm.inject(simple_f)(1, 2, 3)
    assert result[:3] == (1, 2, 3)
    assert isinstance(result[3], DepClass)
    assert result[3].param == 42


def test_property_resolve_class_instance_behaviour(gm):
    gm.register(list_dep)

    class Thing:
        dep = gm.resolve(list_dep)

    assert isinstance(Thing.dep, DeferredProperty)
    assert isinstance(Thing().dep, list)


def test_property_resolve_instance_cache(gm):
    gm.register(list_dep)

    class Thing:
        dep = gm.resolve(list_dep)

    t1 = Thing()
    t1.dep.append(50)

    assert t1.dep[-1] == 50


def test_property_resolve_per_instance_cache(gm):

    gm.register(list_dep)

    class Thing:
        dep = gm.resolve(list_dep)

    t1 = Thing()
    t2 = Thing()

    assert t1.dep is not t2.dep


def test_proeprty_resolve_cache_cleared(gm):
    gm.register(list_dep)

    class Thing:
        dep = gm.resolve(list_dep)

    def nested():
        t1 = Thing()
        t1.dep
        t2 = Thing()
        t2.dep

    nested()
    assert len(list(Thing.dep._cache.keys())) == 0


def test_singleton_new(gm):
    gm.register(list_dep, singleton=True)
    a = gm.inject(list_f)()
    b = gm.inject(list_f)()
    assert a == b == list_dep()
    assert a is b


def test_threadlocal_new(gm):
    gm.register(list_dep, threadlocal=True)
    a = gm.inject(list_f)()
    b = gm.inject(list_f)()
    assert a == b == list_dep()
    assert a is b


def test_dep_not_found(gm):
    with pytest.raises(DependencyNotFoundError):
        gm.get("foo")


def test_dep_removed(gm):
    gm.register(list_dep, singleton=True)
    assert gm.get("list_dep") == list_dep()
    gm.delete("list_dep")
    with pytest.raises(DependencyNotFoundError):
        gm.get("list_dep")


def test_curry_decoration(gm):
    gm.register(singleton=True)(list_dep)
    assert gm.get("list_dep") == list_dep()


def test_inject_names(gm):
    gm.register(list_dep)

    @gm.inject(a="list_dep")
    def f(a):
        return a

    assert f() == list_dep()


def test_dep_not_found_on_inject(gm):
    @gm.inject
    def f(list_dep):
        return list_dep

    with pytest.raises(TypeError):
        f()


@pytest.mark.asyncio
async def test_async_inject(gm):
    gm.register(list_dep)

    @gm.inject
    async def f(list_dep):
        return list_dep

    assert list_dep() == await f()
    assert inspect.iscoroutinefunction(f)

    @gm.inject
    async def f(a):
        return a

    coro = f()
    with pytest.raises(TypeError):
        await coro
