from venom import register, inject

# Basic


@register
def something():
    return 'I am a dependency'


@inject
def use_dependency(something):
    return something


print(use_dependency())
# I am a dependency

assert use_dependency() == something()


# Nested

@register
def something():
    return 'I am a dependency'


@register
@inject
def another_thing(something):
    return (something, 'So am I')


@inject
def use_dependency(another_thing):
    return another_thing


print(use_dependency())
# ('I am a dependency', 'So am i')

assert use_dependency() == ('I am a dependency', 'So am I')
