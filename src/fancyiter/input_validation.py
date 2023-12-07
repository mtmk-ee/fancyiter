import typing


def require_positive_integer(n):
    if not isinstance(n, int):
        raise TypeError("Value must be an integer")
    if n <= 0:
        raise ValueError("Value must be positive")


def require_non_negative_integer(n):
    if not isinstance(n, int):
        raise TypeError("Value must be an integer")
    if n < 0:
        raise ValueError("Value must be non-negative")


def require_iterable(x):
    try:
        _ = iter(x)
    except TypeError:
        raise TypeError("Object is not iterable")


def require_callable(x):
    if not callable(x) and not isinstance(x, typing.Callable):
        raise TypeError("Object is not callable")


def require_collection(x):
    if not isinstance(x, typing.Collection):
        raise TypeError("Object is not a collection")
