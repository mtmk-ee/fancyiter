import typing
import functools
from collections.abc import MutableMapping, MutableSequence, MutableSet

C = typing.TypeVar("C")

@functools.singledispatch
def extend(container: C, items) -> C:
    raise TypeError(f"Cannot extend container of type {type(container).__name__}")


@extend.register
def _(container: MutableSequence, items) -> MutableSequence:
    container.extend(items)
    return container


@extend.register
def _(container: MutableMapping, items) -> MutableMapping:
    container.update(items)
    return container


@extend.register
def _(container: MutableSet, items) -> MutableSet:
    if isinstance(container, set):
        container.update(items)
    else:
        for item in items:
            container.add(items)
