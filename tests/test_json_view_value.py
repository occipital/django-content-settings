import pytest
from content_settings.types.basic import (
    SimpleString,
    SimpleInt,
    SimpleHTML,
    SimpleDecimal,
    SimpleBool,
)
from content_settings.types.markup import SimpleJSON, SimpleYAML

from tests.books.models import Book
from tests.tools import adjust_params
from tests import yaml_installed

pytestmark = [pytest.mark.django_db(transaction=True)]


@pytest.mark.parametrize(
    "var,value,initial",
    adjust_params(
        [
            (
                SimpleString("Hello worlds"),
                '"Hello worlds"',
            ),
            (SimpleHTML("<p>Hello worlds</p>"), '"<p>Hello worlds</p>"'),
            (SimpleInt("13"), "13"),
            (SimpleDecimal("1.23"), '"1.23"'),
            (SimpleBool("1"), "true"),
            (SimpleBool("0"), "false"),
            (SimpleJSON('{"a": 1}'), '{"a": 1}'),
        ]
    ),
)
def test_value(var, value, initial):
    if initial:
        initial()
    in_value = var.give_python(var.default)
    assert var.json_view_value(in_value) == value


@pytest.mark.skipif(not yaml_installed, reason="yaml is installed")
def test_value_yaml():
    var = SimpleYAML(
        """
- a: 1
  b: flex
                           """
    )
    in_value = var.give_python(var.default)
    assert var.json_view_value(in_value) == '[{"a": 1, "b": "flex"}]'
