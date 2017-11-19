import pytest

from giveme.injector import Injector


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
    return (*args, simple_dep)


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


def test_class_injection(gm):
    gm.register(simple_dep)

    class Thinger:
        param = gm.resolve('simple_dep')



