import pytest

from content_settings.utils import class_names, call_base_str
from content_settings.types.basic import SimpleString, SimpleInt
from content_settings.types.datetime import TimeString
from content_settings import functools


@pytest.mark.parametrize(
    "cls, expected",
    [
        pytest.param(
            SimpleString,
            [("content_settings.types.basic", "SimpleString")],
            id="SimpleString",
        ),
        pytest.param(
            SimpleInt, [("content_settings.types.basic", "SimpleInt")], id="SimpleInt"
        ),
        pytest.param(
            TimeString,
            [
                ("content_settings.types.datetime", "TimeString"),
                ("content_settings.types.datetime", "DateTimeString"),
                ("content_settings.types.datetime", "ProcessInputFormats"),
                ("content_settings.types.mixins", "EmptyNoneMixin"),
            ],
            id="TimeString",
        ),
    ],
)
def test_class_names(cls, expected):
    assert list(class_names(cls)) == expected


def my_odd(x: int) -> bool:
    return x % 2 == 1


def my_even(x: int) -> bool:
    return x % 2 == 0


def my_false(x: int) -> bool:
    return False


def my_true(x: int) -> bool:
    return True


@pytest.mark.parametrize(
    "base, func, value, expected",
    [
        pytest.param(
            "tests.test_unit_utils", "my_odd", 5, True, id="base_string_func_string"
        ),
        pytest.param(
            None, "tests.test_unit_utils.my_odd", 5, True, id="base_none_func_string"
        ),
        pytest.param(None, my_odd, 5, True, id="base_none_func_callable"),
        pytest.param(
            "tests.test_unit_utils",
            functools.not_("my_odd"),
            5,
            False,
            id="base_string_not_func_string",
        ),
        pytest.param(
            "tests.test_unit_utils",
            functools.or_("my_even", "my_false"),
            5,
            False,
            id="base_string_or_func_string",
        ),
        pytest.param(
            "tests.test_unit_utils",
            functools.or_("my_even", "my_false", my_true),
            5,
            True,
            id="base_string_or_func_string_and_ref",
        ),
    ],
)
def test_call_base_str_odd(base, func, value, expected):
    assert call_base_str(func, value, call_base=base) == expected
