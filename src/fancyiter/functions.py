import itertools
import typing

from fancyiter import FancyIter, input_validation

T = typing.TypeVar("T")


def fancyiter(value: typing.Iterable[T]) -> FancyIter[T]:
    return FancyIter(value)


def repeat(value: T, n: int = None) -> FancyIter[T]:
    if n is None:
        return FancyIter(itertools.repeat(value))
    input_validation.require_non_negative_integer(n)
    return FancyIter(itertools.repeat(value, n))


def product(*iterables: typing.Iterable[T]) -> FancyIter[T]:
    return FancyIter(itertools.product(*iterables))


def chain(*iterables: typing.Iterable[T]) -> FancyIter[T]:
    return FancyIter(itertools.chain(*iterables))
