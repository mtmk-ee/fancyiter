import pytest

from fancyiter import FancyIter


class TestDunders:
    def test_str(self):
        assert str(FancyIter(range(10))) == str(range(10))
        assert str(FancyIter([])) == str([])
        assert str(FancyIter({1: 5, 2: 6})) == str({1: 5, 2: 6})

    def test_repr(self):
        assert repr(FancyIter(range(10))) == f"FancyIter[{repr(range(10))}]"
        assert repr(FancyIter([])) == f"FancyIter[{repr([])}]"
        assert repr(FancyIter({1: 5, 2: 6})) == f"FancyIter[{repr({1: 5, 2: 6})}]"

    def test_iter(self):
        assert list(iter(FancyIter(range(10)))) == list(range(10))
        assert list(iter(FancyIter([]))) == []
        assert list(iter(FancyIter({1: 5, 2: 6}))) == [1, 2]

        for i, x in enumerate(FancyIter(range(10))):
            assert i == x

        it = iter(FancyIter({1: 5, 2: 6}))
        assert next(it) == 1
        assert next(it) == 2
        with pytest.raises(StopIteration):
            next(it)
