import pytest

from content_settings.types.basic import SimpleString
from content_settings.context_managers import (
    context_defaults,
    set_add,
    set_remove,
    add_tags,
    remove_tags,
    str_prepend,
    help_format,
)
from content_settings.permissions import any, none

pytestmark = [pytest.mark.django_db(transaction=True)]


def test_context_defaults():
    with context_defaults(fetch_permission=any):
        assert SimpleString(fetch_permission=any).fetch_permission == any
        assert SimpleString().fetch_permission == any
        assert SimpleString(fetch_permission=none).fetch_permission == none


def test_nested():
    with context_defaults(fetch_permission=any):
        assert SimpleString().fetch_permission == any
        with context_defaults(fetch_permission=none):
            assert SimpleString().fetch_permission == none
            assert SimpleString(fetch_permission=any).fetch_permission == any
        assert SimpleString().fetch_permission == any


def test_ignore_unkown_kwargs():
    with context_defaults(unknown_kwarg="value", fetch_permission=any):
        assert SimpleString().fetch_permission == any
        assert not hasattr(SimpleString(), "unknown_kwarg")


def test_tags():
    with context_defaults(tags={"main", "second"}):
        assert SimpleString().tags == {"main", "second"}

        with context_defaults(tags={"third"}):
            assert SimpleString().tags == {"third"}


def test_set_add():
    with context_defaults(set_add(tags={"main"})):
        assert SimpleString().tags == {"main"}

        with context_defaults(set_add(tags={"second"})):
            assert SimpleString().tags == {"main", "second"}

        assert SimpleString().tags == {"main"}


def test_tags_set_add():
    with context_defaults(tags={"main"}):
        assert SimpleString().tags == {"main"}

        with context_defaults(set_add(tags={"second"})):
            assert SimpleString().tags == {"main", "second"}

        assert SimpleString().tags == {"main"}


def test_set_add_tags():
    with context_defaults(set_add(tags={"main"})):
        assert SimpleString().tags == {"main"}

        with context_defaults(tags={"second"}):
            assert SimpleString().tags == {"second"}

        assert SimpleString().tags == {"main"}


def test_tags_set_remove():
    with context_defaults(tags={"main", "second"}):
        assert SimpleString().tags == {"main", "second"}

        with context_defaults(set_remove(tags={"second"})):
            assert SimpleString().tags == {"main"}

        assert SimpleString().tags == {"main", "second"}


def test_set_add_tags_overwrite():
    with context_defaults(set_add(tags={"main"})):
        assert SimpleString().tags == {"main"}
        assert SimpleString(tags={"second"}).tags == {"second"}


def test_set_add_tags_init():
    with context_defaults(set_add(tags={"main"}, _init=True)):
        assert SimpleString().tags == {"main"}
        assert SimpleString(tags={"second"}).tags == {"second", "main"}


def test_add_tags():
    with context_defaults(add_tags({"main"})):
        assert SimpleString().tags == {"main"}
        assert SimpleString(tags={"second"}).tags == {"second", "main"}


@pytest.mark.parametrize(
    "context_tags,init_tags,result",
    [
        ("main", "second", {"second", "main"}),
        ({"main"}, "second", {"second", "main"}),
        ("main", {"second"}, {"second", "main"}),
        ({"main"}, {"second"}, {"second", "main"}),
        ({"main"}, None, {"main"}),
        ("main", ["second"], {"second", "main"}),
        ({"main"}, ["second"], {"second", "main"}),
        (["main"], ["second"], {"second", "main"}),
        (["main"], None, {"main"}),
        ("main", {"second", "third"}, {"second", "third", "main"}),
        ({"main"}, {"second", "third"}, {"second", "third", "main"}),
        ("main", {"second"}, {"second", "main"}),
        ({"main"}, {"second"}, {"second", "main"}),
        ("main", None, {"main"}),
    ],
)
def test_add_tags_convertion(context_tags, init_tags, result):
    with context_defaults(add_tags(context_tags)):
        assert SimpleString(tags=init_tags).tags == result


def test_add_tags_string_to_list():
    with context_defaults(add_tags("main")):
        assert SimpleString(tags=["second"]).tags == {"second", "main"}


def test_add_tags_deep():
    with context_defaults(add_tags({"main"})):
        assert SimpleString().tags == {"main"}
        with context_defaults(add_tags({"second"})):
            assert SimpleString().tags == {"second", "main"}
        assert SimpleString(tags={"second"}).tags == {"second", "main"}


def test_class_tags_cannot_be_removed():
    class TaggedString(SimpleString):
        tags = {"str"}

    with context_defaults(tags={"main"}):
        assert TaggedString().tags == {"main", "str"}

    with context_defaults(add_tags({"main"})):
        assert TaggedString().tags == {"main", "str"}

    with context_defaults(remove_tags({"str"})):
        assert TaggedString().tags == {"str"}


def test_help_as_default():
    with context_defaults(help="help"):
        assert SimpleString().help == "help"
        assert SimpleString(help="my help").help == "my help"


def test_help_prepend():
    with context_defaults(help="help"):
        with context_defaults(str_prepend(help="Important: ")):
            assert SimpleString().help == "Important: help"
            assert SimpleString(help="my help").help == "my help"


def test_help_prepend_init():
    with context_defaults(help="help"):
        with context_defaults(str_prepend(help="Important: ", _init=True)):
            assert SimpleString().help == "Important: help"
            assert SimpleString(help="my help").help == "Important: my help"


def test_help_format():
    with context_defaults(help="help"):
        with context_defaults(help_format("Important: {}")):
            assert SimpleString().help == "Important: help"
            assert SimpleString(help="my help").help == "Important: my help"
