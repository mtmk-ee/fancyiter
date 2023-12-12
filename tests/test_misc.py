import pytest

from fancyiter import FancyIter, ItemNotFoundError


class TestMisc:
    @pytest.fixture
    def seq_obj(self) -> FancyIter:
        return FancyIter(range(100))

    @pytest.fixture
    def dict_obj(self) -> FancyIter:
        return FancyIter({"a": 1, "b": 2})

    def test_all(self, seq_obj: FancyIter):
        assert isinstance(seq_obj.all(lambda x: x < 100), bool)
        assert seq_obj.all(lambda x: x < 100)
        assert not seq_obj.all(lambda x: x < 50)

    def test_any(self, seq_obj: FancyIter):
        assert isinstance(seq_obj.any(lambda x: x < 100), bool)
        assert not seq_obj.any(lambda x: x >= 100)
        assert seq_obj.any(lambda x: x < 50)

    def test_chain(self, seq_obj: FancyIter):
        assert list(seq_obj.chain([1, 2, 3])) == list(range(100)) + [1, 2, 3]

    def test_chunks(self, seq_obj: FancyIter):
        assert list(seq_obj.chunks(5)) == [
            [j + i for j in range(5)] for i in range(0, 100, 5)
        ]
        assert list(seq_obj.chain([-1, -2, -3]).chunks(5)) == [
            [j + i for j in range(5)] for i in range(0, 100, 5)
        ] + [[-1, -2, -3]]

    def test_chunks_exact(self, seq_obj: FancyIter):
        assert list(seq_obj.chunks_exact(5)) == [
            [j + i for j in range(5)] for i in range(0, 100, 5)
        ]
        assert list(seq_obj.chain([-1, -2, -3]).chunks_exact(5)) == [
            [j + i for j in range(5)] for i in range(0, 100, 5)
        ]

    def test_contains(self, seq_obj: FancyIter):
        assert seq_obj.contains(50)
        assert not seq_obj.contains(100)

    def test_count(self, seq_obj: FancyIter):
        assert seq_obj.count(lambda x: x < 50) == 50

    def test_cycle(self, seq_obj: FancyIter):
        it = seq_obj.cycle().take(seq_obj.count() * 5)
        assert list(it) == list(seq_obj) * 5

    def test_enumerate(self, seq_obj: FancyIter):
        assert list(seq_obj.enumerate()) == list(enumerate(seq_obj))

    def test_filter(self, seq_obj: FancyIter):
        assert list(seq_obj.filter(lambda x: x < 50)) == list(range(50))

    def test_filter_map(self, seq_obj: FancyIter):
        assert list(seq_obj.filter_map(lambda x: x * 2 if x < 50 else None)) == list(
            range(0, 100, 2)
        )

    def test_find(self, seq_obj: FancyIter):
        assert seq_obj.find(lambda x: x == 50) == 50

        with pytest.raises(ItemNotFoundError):
            seq_obj.find(lambda x: x == 100)

    def test_flatten(self, seq_obj: FancyIter):
        assert list(seq_obj.flatten()) == list(range(100))
        assert list(seq_obj.map(lambda x: [x, x]).flatten()) == list(
            i // 2 for i in range(200)
        )

    def test_fold(self, seq_obj: FancyIter):
        assert seq_obj.fold(0, lambda x, y: x + y) == 4950

    def test_for_each(self, seq_obj: FancyIter):
        count = 0

        def fn(x):
            nonlocal count
            count += x

        seq_obj.for_each(fn)
        assert count == 4950

    def test_fuse(self, seq_obj: FancyIter):
        assert list(seq_obj.fuse()) == list(range(100))
        assert list(seq_obj.fuse(50)) == list(range(50))

    def test_insert(self, seq_obj: FancyIter):
        assert list(seq_obj.insert(50, 100)) == list(range(50)) + [100] + list(
            range(50, 100)
        )
        assert list(seq_obj.insert(0, 100)) == [100] + list(range(100))

    def test_inspect(self, seq_obj: FancyIter):
        def dummy(x):
            pass

        assert seq_obj.inspect(lambda x: dummy(x)).collect() == list(seq_obj)

    def test_last(self, seq_obj: FancyIter):
        assert seq_obj.last() == 99
        assert seq_obj.take_while(lambda x: x < 50).last() == 49

        with pytest.raises(ItemNotFoundError):
            FancyIter([]).last()

    def test_map(self, seq_obj: FancyIter):
        assert list(seq_obj.map(lambda x: x * 2)) == list(range(0, 200, 2))

    def test_max(self, seq_obj: FancyIter):
        assert seq_obj.max() == 99
        with pytest.raises(ItemNotFoundError):
            FancyIter([]).max()

        assert seq_obj.max(key=lambda x: -x) == 0
        with pytest.raises(ItemNotFoundError):
            FancyIter([]).max(key=lambda x: -x)

    def test_min(self, seq_obj: FancyIter):
        assert seq_obj.min() == 0
        with pytest.raises(ItemNotFoundError):
            FancyIter([]).min()

        assert seq_obj.min(key=lambda x: -x) == 99
        with pytest.raises(ItemNotFoundError):
            FancyIter([]).min(key=lambda x: -x)

    def test_nth(self, seq_obj: FancyIter):
        assert seq_obj.nth(50) == 50
        with pytest.raises(ItemNotFoundError):
            seq_obj.nth(100)

    def test_pairs(self, seq_obj: FancyIter):
        assert list(seq_obj.pairs()) == [(i, i + 1) for i in range(99)]
        assert list(seq_obj.take(99).pairs()) == [(i, i + 1) for i in range(98)]

    def test_partition(self, seq_obj: FancyIter):
        assert seq_obj.partition(lambda x: x < 50) == (
            list(range(50)),
            list(range(50, 100)),
        )
        assert seq_obj.partition(lambda x: x % 3 == 0) == (
            list(range(0, 100, 3)),
            [i for i in range(100) if i % 3 != 0],
        )

    def test_position(self, seq_obj: FancyIter):
        assert seq_obj.position(50) == 50
        assert seq_obj.position(0) == 0
        assert seq_obj.position(99) == seq_obj.count() - 1
        assert seq_obj.map(lambda x: x + 1).position(100) == 99

        with pytest.raises(ItemNotFoundError):
            seq_obj.position(100)

    def test_reduce(self, seq_obj: FancyIter):
        assert seq_obj.reduce(lambda x, y: x + y) == 4950

    def test_skip(self, seq_obj: FancyIter):
        assert list(seq_obj.skip(50)) == list(range(50, 100))
        assert list(seq_obj.skip(100)) == []
        assert list(seq_obj.skip(0)) == list(range(100))

    def test_skip_while(self, seq_obj: FancyIter):
        assert list(seq_obj.skip_while(lambda x: x < 50)) == list(range(50, 100))
        assert list(seq_obj.skip_while(lambda x: x < 100)) == []
        assert list(seq_obj.skip_while(lambda x: x < 0)) == list(range(100))

    def test_take(self, seq_obj: FancyIter):
        assert list(seq_obj.take(50)) == list(range(50))
        assert list(seq_obj.take(100)) == list(range(100))
        assert list(seq_obj.take(0)) == []

    def test_take_while(self, seq_obj: FancyIter):
        assert list(seq_obj.take_while(lambda x: x < 50)) == list(range(50))
        assert list(seq_obj.take_while(lambda x: x < 100)) == list(range(100))
        assert list(seq_obj.take_while(lambda x: x < 0)) == []

    def test_windows(self, seq_obj: FancyIter):
        for n in range(1, 10):
            assert list(seq_obj.windows(n)) == list(
                zip(*[range(i, 100) for i in range(n)])
            )

        assert list(FancyIter([]).windows(1)) == []
        assert list(FancyIter([1]).windows(1)) == [(1,)]
        assert list(FancyIter([1]).windows(2)) == [(1,)]

        with pytest.raises(ValueError):
            seq_obj.windows(0)

    def test_windows_exact(self, seq_obj: FancyIter):
        for n in range(1, 10):
            assert list(seq_obj.windows_exact(n)) == list(
                zip(*[range(i, 100) for i in range(n)])
            )

        assert list(FancyIter([]).windows_exact(1)) == []
        assert list(FancyIter([1]).windows_exact(1)) == [(1,)]
        assert list(FancyIter([1]).windows_exact(2)) == []

        with pytest.raises(ValueError):
            seq_obj.windows_exact(0)

    def test_zip(self, seq_obj: FancyIter):
        for n in range(1, 10):
            assert list(seq_obj.zip(*[range(i + 1, 100) for i in range(n)])) == list(
                zip(*[range(i, 100) for i in range(n + 1)])
            )
