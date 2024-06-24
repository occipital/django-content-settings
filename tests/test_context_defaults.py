import pytest

from content_settings.types.basic import SimpleString
from content_settings.permissions import any, none

from content_settings.defaults.context import defaults
from content_settings.defaults.modifiers import add_tags

pytestmark = [pytest.mark.django_db(transaction=True)]


def test_context_defaults():
    with defaults(fetch_permission=any):
        assert SimpleString(fetch_permission=any).fetch_permission == any
        assert SimpleString().fetch_permission == any
        assert SimpleString(fetch_permission=none).fetch_permission == none


def test_nested():
    with defaults(fetch_permission=any):
        assert SimpleString().fetch_permission == any
        with defaults(fetch_permission=none):
            assert SimpleString().fetch_permission == none
            assert SimpleString(fetch_permission=any).fetch_permission == any
        assert SimpleString().fetch_permission == any


def test_ignore_unkown_kwargs():
    with defaults(unknown_kwarg="value", fetch_permission=any):
        assert SimpleString().fetch_permission == any
        assert not hasattr(SimpleString(), "unknown_kwarg")


def test_add_tags_nested():
    with defaults(add_tags({"main"})):
        assert SimpleString().tags == {"main"}

        with defaults(add_tags({"second"})):
            assert SimpleString().tags == {"main", "second"}

        assert SimpleString().tags == {"main"}
