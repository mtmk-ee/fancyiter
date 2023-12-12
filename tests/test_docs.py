import inspect
import typing

import pytest

from fancyiter import FancyIter


class TestDocs:
    @pytest.fixture
    def methods(self):
        parent_method_names = set(dir(object))
        all_method_names = set(dir(FancyIter))
        non_inherited_method_names = all_method_names - parent_method_names
        return [
            getattr(FancyIter, x)
            for x in non_inherited_method_names
            if callable(getattr(FancyIter, x)) and x not in ["__class_getitem__"]
        ]

    def test_documentation(self, methods):
        for func in methods:
            assert func.__doc__ is not None and func.__doc__.strip() != ""

    def test_typehint_presence(self, methods):
        for func in methods:
            annotations = inspect.get_annotations(func)
            argspec = inspect.getfullargspec(func)

            for arg in argspec.args:
                if arg == "self":
                    continue
                assert arg in annotations
            for kwarg in argspec.kwonlyargs:
                assert kwarg in annotations
