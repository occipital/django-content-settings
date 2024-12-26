import pytest

from content_settings.conf import split_attr, SplitFormatError


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


@pytest.mark.parametrize(
    "line,msg",
    [
        ("title", "Invalid attribute name: title; name should be uppercase"),
        (
            "lazy__title",
            "Invalid attribute name: title in lazy__title; name should be uppercase",
        ),
        (
            "unknown__TITLE",
            "Invalid attribute name: unknown in unknown__TITLE; name should be uppercase or it is unknown prefix",
        ),
        (
            "TITLE__hi__NO",
            "Invalid attribute name: hi__NO in TITLE__hi__NO; suffix should be lowercase",
        ),
    ],
)
def test_split_attr_error(line, msg):
    with pytest.raises(SplitFormatError) as e:
        split_attr(line)
    assert str(e.value) == msg
