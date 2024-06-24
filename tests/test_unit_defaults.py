import pytest

from content_settings.defaults.filters import any_name, name_exact
from content_settings.defaults.modifiers import (
    set_if_missing,
    unite_set_remove,
    add_tags,
    remove_tags,
    add_tag,
    remove_tag,
    help_prefix,
    help_suffix,
)
from content_settings.defaults.context import (
    defaults,
    default_help_prefix,
    default_help_suffix,
    default_tags,
)

from content_settings.types.array import SimpleStringsList
from content_settings.types.markup import SimpleCSV
from content_settings.types.mixins import mix, AdminPreviewMenuMixin
from content_settings.types.basic import SimpleString


@pytest.mark.parametrize(
    "filter, cls, expected",
    [
        pytest.param(any_name, SimpleStringsList, True, id="any"),
        pytest.param(
            name_exact("SimpleStringsList"),
            SimpleStringsList,
            True,
            id="name_exact_self_name",
        ),
        pytest.param(
            name_exact("SimpleText"),
            SimpleStringsList,
            True,
            id="name_exact_direct_parent",
        ),
        pytest.param(
            name_exact("SimpleBool"), SimpleStringsList, False, id="name_exact_no_match"
        ),
        pytest.param(
            name_exact("SimpleText"), SimpleCSV, True, id="name_exact_grandparent"
        ),
        pytest.param(
            name_exact("AdminPreviewMenuMixin"),
            mix(AdminPreviewMenuMixin, SimpleCSV),
            True,
            id="name_exact_from_mix",
        ),
        pytest.param(
            name_exact("SimpleText"),
            mix(AdminPreviewMenuMixin, SimpleCSV),
            True,
            id="name_exact_from_mix_grantparent",
        ),
    ],
)
def test_filter(filter, cls, expected):
    assert filter(cls) == expected


@pytest.mark.parametrize(
    "modifier, kwargs, expected",
    [
        pytest.param(set_if_missing(a=3), {"a": 1}, {}, id="set_if_missing_skip"),
        pytest.param(set_if_missing(b=2), {"a": 1}, {"b": 2}, id="set_if_missing_set"),
        pytest.param(
            unite_set_remove(tags=["a"]),
            {"tags": ["a", "b"]},
            {"tags": {"b"}},
            id="unite_set_remove",
        ),
        pytest.param(
            unite_set_remove(tags=["a"]), {"f": 1}, {}, id="unite_set_remove_new"
        ),
        pytest.param(
            add_tags(["a", "b"]), {"tags": ["a"]}, {"tags": {"a", "b"}}, id="add_tags"
        ),
        pytest.param(
            add_tags(["a", "b"]), {"f": 1}, {"tags": ["a", "b"]}, id="add_tags_new"
        ),
        pytest.param(
            remove_tags(["a"]), {"tags": ["a", "b"]}, {"tags": {"b"}}, id="remove_tags"
        ),
        pytest.param(remove_tags(["a"]), {"f": 1}, {}, id="remove_tags_new"),
        pytest.param(
            add_tag("a"), {"tags": ["a", "b"]}, {"tags": {"a", "b"}}, id="add_tag"
        ),
        pytest.param(add_tag("a"), {"f": 1}, {"tags": {"a"}}, id="add_tag_new"),
        pytest.param(
            remove_tag("a"), {"tags": ["a", "b"]}, {"tags": {"b"}}, id="remove_tag"
        ),
        pytest.param(remove_tag("a"), {"f": 1}, {}, id="remove_tag_new"),
        pytest.param(
            help_prefix("prefix"),
            {"help": "help"},
            {"help": "prefix<br>help"},
            id="help_prefix",
        ),
        pytest.param(
            help_suffix("suffix"),
            {"help": "help"},
            {"help": "help<br>suffix"},
            id="help_suffix",
        ),
    ],
)
def test_modifier(modifier, kwargs, expected):
    assert modifier(kwargs) == expected


TEST_SETTING = SimpleString()


def process_modifiers(kwargs):
    return TEST_SETTING.update_defaults_context(kwargs)


def test_process_nested():
    with defaults(help="first"):
        assert process_modifiers({}) == {"help": "first"}
        with defaults(help="second"):
            assert process_modifiers({}) == {"help": "second"}
        assert process_modifiers({}) == {"help": "first"}


def test_help_prefix():
    with default_help_prefix("prefix"):
        assert process_modifiers({"help": "value"}) == {"help": "prefix<br>value"}
        with default_help_prefix("prefix2"):
            assert process_modifiers({"help": "value2"}) == {
                "help": "prefix<br>prefix2<br>value2"
            }
    assert process_modifiers({"help": "value"}) == {"help": "value"}


def test_help_suffix():
    with default_help_suffix("suffix"):
        assert process_modifiers({"help": "value"}) == {"help": "value<br>suffix"}
        with default_help_suffix("suffix2"):
            assert process_modifiers({"help": "value2"}) == {
                "help": "value2<br>suffix2<br>suffix"
            }
    assert process_modifiers({"help": "value"}) == {"help": "value"}


def test_tags_set_nested_tags():
    with defaults(add_tags({"main"})):
        assert process_modifiers({}) == {"tags": {"main"}}

        with defaults(add_tags({"second"})):
            assert process_modifiers({}) == {"tags": {"main", "second"}}
            assert process_modifiers({"tags": ["third"]}) == {
                "tags": {"main", "second", "third"}
            }

        assert process_modifiers({}) == {"tags": {"main"}}


def test_tags_set_nested_inside_force():
    with defaults(add_tags({"main"})):
        with defaults(tags={"second"}):
            assert process_modifiers({}) == {"tags": {"second", "main"}}
            assert process_modifiers({"tags": ["third"]}) == {"tags": {"third", "main"}}

        assert process_modifiers({}) == {"tags": {"main"}}


def test_default_tags():
    with default_tags({"main"}):
        assert process_modifiers({}) == {"tags": {"main"}}
        with default_tags({"second"}):
            assert process_modifiers({}) == {"tags": {"second", "main"}}
            assert process_modifiers({"tags": ["third"]}) == {
                "tags": {"third", "main", "second"}
            }
