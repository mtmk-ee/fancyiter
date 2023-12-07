import itertools
import functools
import typing

from fancyiter._collect import extend
from fancyiter._decorators import require_member_attr, chainable
from fancyiter.exceptions import ItemNotFoundError
from fancyiter import input_validation


T = typing.TypeVar("T")
U = typing.TypeVar("U")
C = typing.TypeVar("C")


class FancyIter(typing.Generic[T]):
    __slots__ = ("_iterable",)

    def __init__(self, iterable: typing.Iterable[T]):
        input_validation.require_iterable(iterable)
        self._iterable = iterable

    def __iter__(self) -> typing.Iterator[T]:
        return self._iterable.__iter__()

    def __repr__(self) -> str:
        return f"FancyIter[{repr(self._iterable)}]"

    def __str__(self) -> str:
        return str(self._iterable)

    @require_member_attr("_iterable", "__len__")
    def __len__(self) -> int:
        return len(self._iterable)

    @require_member_attr("_iterable", "__contains__")
    def __contains__(self, item) -> bool:
        return self._iterable.__contains__(item)

    @require_member_attr("_iterable", "__getitem__")
    def __getitem__(self, key):
        return self._iterable[key]

    def all(self, func: typing.Callable[[T], bool]) -> bool:
        """Check if all elements in the iterable satisfy the given condition.

        Args:
            func (callable): A function that takes an element from the iterable as input and returns a boolean value.

        Returns:
            bool: True if all elements in the iterable satisfy the given condition.
        """
        input_validation.require_callable(func)
        return all(func(x) for x in self._iterable)

    def any(self, func: typing.Callable[[T], bool]) -> bool:
        """Apply the given function to each element of the iterable and return True if any of the results are True.

        Args:
            func (typing.Callable[[T], bool]): The function to apply to each element of the iterable.

        Returns:
            bool: True if any of the elements in the iterable satisfy the given condition.
        """
        input_validation.require_callable(func)
        return any(func(x) for x in self._iterable)

    @chainable
    def chain(self, *iterables: typing.Iterable[typing.Any]) -> "FancyIter[T]":
        """Chains multiple iterables together.

        Once the first iterable is exhausted, the next one is used, and so on.

        Args:
            *iterables (typing.Iterable[typing.Any]): The iterables to chain together.
        """
        for it in iterables:
            input_validation.require_iterable(it)
        return FancyIter(itertools.chain(self._iterable, *iterables))

    @chainable
    def chunks(self, n: int) -> "FancyIter[typing.List[T]]":
        """Split the iterable into chunks of size n.

        Each item in the returned FancyIter is a list of length n, except possibly
        the last list, which may be shorter.

        Args:
            n: The size of each chunk.
        """
        input_validation.require_positive_integer(n)
        return FancyIter(_chunks_impl(self._iterable, n))

    @chainable
    def chunks_exact(self, n: int) -> "FancyIter[typing.List[T]]":
        """Like `chunks`, but skips the last chunk if it is incomplete.

        Each item in the returned FancyIter is a list of length n.

        Args:
            n (int): The size of each chunk.
        """
        return self.chunks(n).filter(lambda x: len(x) == n)

    def collect(self, func: typing.Callable[[typing.Iterable[T]], C] = list) -> C:
        """Collect all the items into a container.

        This is equivalent to `func(fancy_iter)`.

        Args:
            func: The function or type to collect the items with. Defaults to `list`.
        """
        input_validation.require_callable(func)
        return func(self._iterable)

    def collect_into(self, collection: typing.Collection[T]):
        """Collect all the items into an existing container.

        The container must be mutable and implement the interface of
        a Set, Sequence, or Mapping.

        Args:
            collection: The container to collect the items into.
        """
        input_validation.require_collection(collection)
        extend(collection, self._iterable)

    def contains(self, item: T) -> bool:
        """Check if the iterable contains an item.

        Args:
            item: The item to check for.

        Returns:
            bool: True if the item is in the iterable, False otherwise.
        """
        return self.filter(lambda x: x == item).any()

    def count(self, func: typing.Callable[[T], bool] = None) -> int:
        """Count the number of items in the iterable which (optionally) match a predicate.

        Args:
            func: a predicate function indicating whether an item should be counted.
                If not specified, all items are counted.

        Returns:
            int: the number of items counted.
        """
        if func is None:
            return len(self._iterable)
        else:
            return len(self.filter(func))

    @chainable
    def cycle(self) -> "FancyIter[T]":
        """Repeat the iterable forever."""
        return FancyIter(itertools.cycle(self._iterable))

    @chainable
    def enumerate(self) -> "FancyIter[typing.Tuple[int, T]]":
        return FancyIter(enumerate(self._iterable))

    @chainable
    def filter(self, func: typing.Callable[[T], bool]) -> "FancyIter[T]":
        input_validation.require_callable(func)
        return FancyIter(filter(func, self._iterable))

    @chainable
    def filter_map(
        self, func: typing.Callable[[T], typing.Optional[U]]
    ) -> "FancyIter[U]":
        return self.map(func).filter(lambda x: x is not None)

    def find(self, func: typing.Callable[[T], bool]) -> typing.Optional[T]:
        """Find the first item in the iterable that matches a predicate.

        Args:
            func: a predicate function indicating whether an item should be returned.

        Returns:
            T: the first item in the iterable that matches the predicate, or None if no item matches.
        """
        try:
            return next(filter(func, self._iterable))
        except StopIteration:
            raise ItemNotFoundError("Item not found")

    @chainable
    def flatten(self) -> "FancyIter[T]":
        return FancyIter(itertools.chain.from_iterable(self._iterable))

    def fold(self, initial: U, func: typing.Callable[[U, T], U]) -> U:
        return functools.reduce(func, self._iterable, initial)

    def for_each(self, func: typing.Callable[[T], None]):
        for item in self._iterable:
            func(item)

    @chainable
    def fuse(self, stop_value: typing.Optional[T] = None) -> "FancyIter[T]":
        """Creates an iterator which stops at the first occurrence of `stop_value`."""
        return self.take_while(lambda x: x != stop_value)

    @chainable
    def inspect(self, func: typing.Callable[[T], None]) -> "FancyIter[T]":
        """Call a function on each item in the iterable, passing the original item along.

        This is useful for debugging, or as a non-consuming `for_each`.
        """
        return self.map(lambda x: (x, func(x))[0])

    def last(self) -> T:
        """Get the last item in the iterable.

        Raises:
            ValueError: if the iterable is empty.
        """
        for item in self._iterable:
            pass
        try:
            return item
        except NameError:
            raise ItemNotFoundError("Iterable is empty")

    @chainable
    def map(self, func: typing.Callable[[T], U]) -> "FancyIter[U]":
        input_validation.require_callable(func)
        return FancyIter(map(func, self._iterable))

    def max(self, key: typing.Callable[[T], typing.Any] = None) -> T:
        if key is None:
            return max(self._iterable)
        else:
            input_validation.require_callable(key)
            return max(self._iterable, key=key)

    def min(self, key: typing.Callable[[T], typing.Any] = None) -> T:
        if key is None:
            return min(self._iterable)
        else:
            input_validation.require_callable(key)
            return min(self._iterable, key=key)

    def nth(self, n: int) -> T:
        """Get the nth item in the iterable.

        Args:
            n: the index of the item to get starting from 0.
        """
        input_validation.require_non_negative_integer(n)
        return self.enumerate().find(lambda x: x[0] == n)[1]

    def partition(
        self, func: typing.Callable[[T], bool]
    ) -> typing.Tuple[list[T], list[T]]:
        """Partition the iterable into two lists based on a predicate.

        Args:
            func: a predicate returning True or False for each item in the iterable.

        Returns:
            tuple[list[T], list[T]]: a tuple of two lists, the first containing the items for
                which the predicate returned True, and the second containing the items
                for which it returned False.
        """
        input_validation.require_callable(func)
        trues = []
        falses = []
        for item in self._iterable:
            if func(item):
                trues.append(item)
            else:
                falses.append(item)
        return (trues, falses)

    def position(self, item: T) -> int:
        """Get the position of an item in the iterable.

        Args:
            item: The item to find the position of.

        Returns:
            int: the position of the item in the iterable starting from 0.

        Raises:
            ValueError: if the item is not in the iterable.
        """
        return self.enumerate().find(lambda x: x[1] == item)[0]

    def reduce(self, func: typing.Callable[[T, T], T]) -> T:
        input_validation.require_callable(func)
        return functools.reduce(func, self._iterable)

    @chainable
    def skip(self, n: int) -> "FancyIter[T]":
        input_validation.require_non_negative_integer(n)
        return FancyIter(itertools.islice(self._iterable, n, None))

    @chainable
    def skip_while(self, func: typing.Callable[[T], bool]) -> "FancyIter[T]":
        input_validation.require_callable(func)
        return FancyIter(itertools.dropwhile(func, self._iterable))

    @chainable
    def step_by(self, n: int) -> "FancyIter[T]":
        input_validation.require_positive_integer(n)
        return FancyIter(itertools.islice(self._iterable, 0, None, n))

    @chainable
    def take(self, n: int) -> "FancyIter[T]":
        input_validation.require_non_negative_integer(n)
        return FancyIter(itertools.islice(self._iterable, 0, n))

    @chainable
    def take_while(self, func: typing.Callable[[T], bool]) -> "FancyIter[T]":
        input_validation.require_callable(func)
        return FancyIter(itertools.takewhile(func, self._iterable))

    @chainable
    def windows(self, n: int) -> "FancyIter[typing.List[T]]":
        input_validation.require_non_negative_integer(n)
        return FancyIter(_windows_impl(self._iterable, n))

    @chainable
    def windows_exact(self, n: int) -> "FancyIter[typing.List[T]]":
        return self.windows(n).filter(lambda x: len(x) == n)

    @chainable
    def zip(
        self, *iterables: typing.Iterable[typing.Any]
    ) -> "FancyIter[typing.Tuple[T, ...]]":
        for it in iterables:
            input_validation.require_iterable(it)
        return FancyIter(zip(self._iterable, *iterables))

    @chainable
    def zip_longest(
        self,
        *iterables: typing.Iterable[typing.Any],
    ) -> "FancyIter[typing.Tuple[T, ...]]":
        for it in iterables:
            input_validation.require_iterable(it)
        return FancyIter(itertools.zip_longest(self._iterable, *iterables))


def _chunks_impl(iterable, n: int):
    chunk = []
    for item in iterable:
        chunk.append(item)
        if len(chunk) == n:
            yield chunk
            chunk = []
    if chunk:
        yield chunk


def _windows_impl(iterable, n: int):
    window = []
    it = iter(iterable)
    for _ in range(n - 1):
        try:
            window.append(next(it))
        except StopIteration:
            # if the iterable is shorter than n, then there's only one possible window
            yield window
            return

    for item in it:
        window += [item]
        yield window
        window = window[1:]
