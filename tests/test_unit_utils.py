import pytest

from content_settings.utils import class_names
from content_settings.types.basic import SimpleString, SimpleInt
from content_settings.types.datetime import TimeString
from content_settings.types.template import SimpleExecOneKey


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
        pytest.param(
            SimpleExecOneKey,
            [
                ("content_settings.types.template", "SimpleExecOneKey"),
                ("content_settings.types.template", "GiveOneKeyMixin"),
                ("content_settings.types.template", "SimpleExec"),
                ("content_settings.types.template", "SimpleCallTemplate"),
                ("content_settings.types.mixins", "CallToPythonMixin"),
                ("content_settings.types.template", "StaticDataMixin"),
                ("content_settings.types.basic", "SimpleText"),
            ],
            id="SimpleExecOneKey",
        ),
    ],
)
def test_class_names(cls, expected):
    assert list(class_names(cls)) == expected
