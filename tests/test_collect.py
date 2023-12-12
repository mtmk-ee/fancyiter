import pytest

from fancyiter import FancyIter


class TestCollect:
    def test_collect_list(self):
        items = FancyIter(range(100)).collect(list)
        assert type(items) == list
        assert len(items) == 100
        assert list(items) == list(range(100))

    def test_collect_dict(self):
        items = FancyIter(range(100)).map(lambda x: (x, x + 100)).collect(dict)
        assert type(items) == dict
        assert len(items) == 100
        assert sorted(list(items.keys())) == list(range(100))
        assert sorted(list(items.values())) == list(range(100, 200))

    def test_collect_set(self):
        items = FancyIter(range(100)).collect(set)
        assert type(items) == set
        assert len(items) == 100
        assert sorted(list(items)) == list(range(100))

    def test_collect_fn(self):
        def fn(iterable):
            return list(iterable)

        items = FancyIter(range(100)).collect(fn)
        assert type(items) == list
        assert len(items) == 100
        assert list(items) == list(range(100))

    def test_collect_into_list(self):
        items = [0, 1, 2, 3]
        FancyIter(range(4, 100)).collect_into(items)
        assert type(items) == list
        assert len(items) == 100
        assert list(items) == list(range(100))

    def test_collect_into_dict(self):
        items = {
            0: 100,
            1: 101,
            2: 102,
            3: 103,
        }
        FancyIter(range(100)).map(lambda x: (x, x + 100)).collect_into(items)
        assert type(items) == dict
        assert len(items) == 100
        assert sorted(list(items.keys())) == list(range(100))
        assert sorted(list(items.values())) == list(range(100, 200))

    def test_collect_into_set(self):
        items = {0, 1, 2, 3}
        FancyIter(range(4, 100)).collect_into(items)
        assert type(items) == set
        assert len(items) == 100
        assert sorted(list(items)) == list(range(100))
