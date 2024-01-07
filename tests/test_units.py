import pytest

from content_settings.conf import split_attr


@pytest.mark.parametrize(
    "line,val",
    [
        ("TITLE", (None, "TITLE", None)),
        ("type__TITLE", ("type", "TITLE", None)),
        ("type__TITLE", ("type", "TITLE", None)),
        ("type__TITLE_SUBTITLE", ("type", "TITLE_SUBTITLE", None)),
        ("type__TITLE__SUBTITLE", ("type", "TITLE__SUBTITLE", None)),
        ("TITLE__SUBTITLE", (None, "TITLE__SUBTITLE", None)),
        ("TITLE__SUBTITLE__name", (None, "TITLE__SUBTITLE", "name")),
        ("TITLE__SUBTITLE__name__upper", (None, "TITLE__SUBTITLE", "name__upper")),
        (
            "type__TITLE__SUBTITLE__name__upper",
            ("type", "TITLE__SUBTITLE", "name__upper"),
        ),
    ],
)
def test_split_attr(line, val):
    assert split_attr(line) == val
