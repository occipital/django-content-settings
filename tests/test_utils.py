from content_settings.utils import remove_same_ident


def test_remove_same_ident_ident_is_not_removed():
    assert remove_same_ident("a\n  b\n    c\n      d") == "a\n  b\n    c\n      d"


def test_remove_same_ident_ident_is_removed():
    assert (
        remove_same_ident("  b\n    c\n      d\n        e") == "b\n  c\n    d\n      e"
    )


def test_remove_same_ident_ident_is_removed_with_windows_newlines():
    assert (
        remove_same_ident("  b\r\n    c\r\n      d\r\n        e")
        == "b\r\n  c\r\n    d\r\n      e"
    )


def test_remove_same_ident_empty_string():
    assert remove_same_ident("") == ""


def test_remove_same_ident_only_spaces():
    assert remove_same_ident("  ") == "  "


def test_remove_same_ident_only_spaces_with_newlines():
    assert (
        remove_same_ident("\n  \n    \n      \n        \n")
        == "\n  \n    \n      \n        \n"
    )


def test_remove_same_ident_with_multiline_str():
    assert (
        remove_same_ident(
            """
    a
        b
            c
                d
    """
        )
        == """
a
    b
        c
            d
"""
    )
