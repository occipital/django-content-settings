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
    NotSet,
)
from content_settings.defaults.context import (
    defaults,
    default_help_prefix,
    default_help_suffix,
    default_tags,
    update_defaults,
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
            add_tags(["a", "b"]), {"tags": ["a"]}, {"tags": {"a", "b"}}, id="add_tags"
        ),
        pytest.param(
            add_tags(["a", "b"]), {"f": 1}, {"tags": {"a", "b"}}, id="add_tags_new"
        ),
        pytest.param(
            add_tag("a"), {"tags": ["a", "b"]}, {"tags": {"a", "b"}}, id="add_tag"
        ),
        pytest.param(add_tag("a"), {"f": 1}, {"tags": {"a"}}, id="add_tag_new"),
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
def test_first_modifier(modifier, kwargs, expected):
    assert {
        k: v for k, v in modifier({}, kwargs).items() if v is not NotSet
    } == expected


TEST_SETTING = SimpleString()


def process_modifiers(kwargs):
    return update_defaults(TEST_SETTING, kwargs)


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
                "help": "prefix2<br>prefix<br>value2"
            }
    assert process_modifiers({"help": "value"}) == {"help": "value"}


def test_help_suffix():
    with default_help_suffix("suffix"):
        assert process_modifiers({"help": "value"}) == {"help": "value<br>suffix"}
        with default_help_suffix("suffix2"):
            assert process_modifiers({"help": "value2"}) == {
                "help": "value2<br>suffix<br>suffix2"
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
            assert process_modifiers({}) == {"tags": {"second"}}
            assert process_modifiers({"tags": ["third"]}) == {"tags": ["third"]}

        assert process_modifiers({}) == {"tags": {"main"}}


def test_default_tags():
    with default_tags({"main"}):
        assert process_modifiers({}) == {"tags": {"main"}}
        with default_tags({"second"}):
            assert process_modifiers({}) == {"tags": {"second", "main"}}
            assert process_modifiers({"tags": ["third"]}) == {
                "tags": {"third", "main", "second"}
            }


def test_forced_main_tag():
    with defaults(tags={"main"}):
        assert process_modifiers({}) == {"tags": {"main"}}
        assert process_modifiers({"tags": {"internal"}}) == {"tags": {"internal"}}
        with default_tags({"additional"}):
            assert process_modifiers({}) == {"tags": {"main", "additional"}}
            assert process_modifiers({"tags": {"internal"}}) == {
                "tags": {"internal", "additional"}
            }


def test_multiple_adding_tags():
    with defaults(add_tags({"first"})):
        with defaults(add_tags({"second"})):
            assert process_modifiers({}) == {"tags": {"first", "second"}}
            assert process_modifiers({"tags": {"main"}}) == {
                "tags": {"first", "second", "main"}
            }
        with defaults(add_tags({"third"})):
            assert process_modifiers({}) == {"tags": {"first", "third"}}
            assert process_modifiers({"tags": {"main"}}) == {
                "tags": {"first", "third", "main"}
            }


def test_one_main_tag_and_multiple_adding_tags():
    with defaults(tags={"main"}):
        with defaults(add_tags({"first"})):
            assert process_modifiers({}) == {"tags": {"main", "first"}}
            with defaults(add_tags({"second"})):
                assert process_modifiers({}) == {"tags": {"main", "first", "second"}}
                assert process_modifiers({"tags": {"internal"}}) == {
                    "tags": {"first", "second", "internal"}
                }


def test_removing_main_tag():
    with defaults(tags={"main"}):
        with defaults(remove_tag("main")):
            assert process_modifiers({}) == {}


def test_removing_main_tag_not_empty_not_set():
    with defaults(tags={"main"}):
        with defaults(remove_tag("main", _empty_not_set=False)):
            assert process_modifiers({}) == {"tags": set()}


def test_removing_main_tag_but_not_existing():
    with defaults(tags={"main"}):
        with defaults(remove_tag("main")):
            assert process_modifiers({"tags": {"main"}}) == {"tags": {"main"}}


def test_adding_three_tags_and_removing_one():
    with defaults(add_tags({"first", "second", "third"})):
        with defaults(remove_tag("second")):
            assert process_modifiers({}) == {"tags": {"first", "third"}}
