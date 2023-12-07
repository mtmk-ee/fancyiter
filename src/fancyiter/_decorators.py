import functools


def exhausts(func):
    """Indicates that the decorated method immediately exhausts the iterable"""
    return func


def chainable(func):
    """Indicates that the decorated method is chainable"""
    return func


def require_member_attr(member: str, attr: str):
    def outer(func):
        @functools.wraps(func)
        def inner(self, *args, **kwargs):
            obj = getattr(self, member)
            if not hasattr(obj, attr):
                raise AttributeError(f"Wrapped object has no attribute {attr}")
            return func(self, *args, **kwargs)

        return inner

    return outer
