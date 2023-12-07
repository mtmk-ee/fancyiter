import typing
import functools
from collections.abc import MutableMapping, MutableSequence, MutableSet


@functools.singledispatch
def extend(container, items):
    raise TypeError(f"Cannot extend container of type {type(container).__name__}")


@extend.register
def _(container: MutableSequence, items):
    container.extend(items)


@extend.register
def _(container: MutableMapping, items):
    container.update(items)


@extend.register
def _(container: MutableSet, items):
    if isinstance(container, set):
        container.update(items)
    else:
        for item in items:
            container.add(items)
