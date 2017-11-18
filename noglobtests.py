import pytest

from giveme.injector import Injector


@pytest.fixture
def gm():
    return Injector()    


def simple_dep():
    return 42


def simple_f(a, b, c, simple_dep):
    return a, b, c, simple_dep


def test_simple_f(gm):
    gm.register(simple_dep)
    result = gm.inject(simple_f)(11, 22, 33)
    assert result == (11, 22, 33, 42)
    
