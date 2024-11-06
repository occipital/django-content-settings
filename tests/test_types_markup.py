import pytest
from decimal import Decimal
from functools import partial

from django.core.exceptions import ValidationError

from content_settings.types.basic import (
    SimpleString,
    SimpleDecimal,
    SimpleBool,
)
from content_settings.types.markup import (
    SimpleJSON,
    SimpleCSV,
    SimpleYAML,
)
from content_settings.types.template import DjangoTemplateNoArgs
from content_settings.types import required, optional

from tests import yaml_installed


pytestmark = [pytest.mark.django_db]


@pytest.mark.parametrize(
    "cs_type",
    [
        SimpleJSON,
        partial(SimpleCSV, csv_fields=["name", "price"]),
    ],
)
def test_empty_value(cs_type):
    var = cs_type()
    var.validate_value("")


@pytest.mark.parametrize(
    "cs_type",
    [
        SimpleJSON,
    ],
)
def test_empty_value_is_none(cs_type):
    var = cs_type()
    assert var.give_python("") is None


def test_simple_json():
    var = SimpleJSON()

    assert var.give_python('{"a": 45}') == {"a": 45}


def test_simple_csv_empty_is_none():
    var = SimpleCSV(csv_fields=["name", "price"])

    assert var.give_python("") == []


def test_simple_json_invalid():
    var = SimpleJSON()

    with pytest.raises(ValidationError) as error:
        var.give_python("invalid json")

    assert error.value.messages == ["Expecting value: line 1 column 1 (char 0)"]


CSV_TEXT = """
Kateryna,1.2
The Will,200
    """


def test_csv():
    var = SimpleCSV(csv_fields=["name", "price"])
    var.validate_value(CSV_TEXT)
    assert var.give_python(CSV_TEXT) == [
        {"name": "Kateryna", "price": "1.2"},
        {"name": "The Will", "price": "200"},
    ]


def test_csv_typed():
    var = SimpleCSV(
        csv_fields={
            "name": SimpleString(),
            "price": SimpleDecimal(),
        }
    )
    var.validate_value(CSV_TEXT)
    assert var.give_python(CSV_TEXT) == [
        {"name": "Kateryna", "price": Decimal("1.2")},
        {"name": "The Will", "price": Decimal("200")},
    ]


def test_csv_typed_suffix():
    var = SimpleCSV(
        csv_fields={
            "name": SimpleString(),
            "available": SimpleBool(),
            "price": SimpleDecimal(),
        },
        suffixes={"available": lambda all: [v for v in all if v.get("available")]},
    )

    TEXT = """
abs,1,10
second,0,5.55
green,1,0
"""

    assert var.give_python(TEXT) == [
        {"name": "abs", "available": True, "price": Decimal("10")},
        {"name": "second", "available": False, "price": Decimal("5.55")},
        {"name": "green", "available": True, "price": Decimal("0")},
    ]

    assert var.give_python(TEXT, "available") == [
        {"name": "abs", "available": True, "price": Decimal("10")},
        {"name": "green", "available": True, "price": Decimal("0")},
    ]


def test_csv_typed_template_no_args():
    var = SimpleCSV(
        csv_fields={
            "name": SimpleString(),
            "price": SimpleDecimal(),
            "pic": DjangoTemplateNoArgs(),
        }
    )
    text = """
Kateryna,1.2,{{SETTINGS.STATIC_URL}}cover/kateryna.jpg
The Will,200,{{SETTINGS.STATIC_URL}}cover/will.jpg
    """
    var.validate_value(text)
    assert var.give_python(text) == [
        {
            "name": "Kateryna",
            "price": Decimal("1.2"),
            "pic": "/static/cover/kateryna.jpg",
        },
        {"name": "The Will", "price": Decimal("200"), "pic": "/static/cover/will.jpg"},
    ]


def test_csv_overload():
    var = SimpleCSV(csv_fields=["name", "price"])

    text = """
Kateryna,1.2,light
The Will,200
    """

    var.validate_value(text)
    assert var.give_python(text) == [
        {"name": "Kateryna", "price": "1.2"},
        {"name": "The Will", "price": "200"},
    ]


def test_csv_missing():
    var = SimpleCSV(csv_fields=["name", "price"])

    text = """
Kateryna,1.2
The Will
    """
    var.validate_value(text)
    assert var.give_python(text) == [
        {"name": "Kateryna", "price": "1.2"},
        {"name": "The Will"},
    ]


def test_csv_empty():
    var = SimpleCSV(csv_fields=["name", "price"])

    text = ""
    var.validate_value(text)
    assert var.give_python(text) == []


def test_csv_fields_list_default_required():
    var = SimpleCSV(
        csv_fields=["name", "price"], csv_fields_list_type=SimpleString(required)
    )

    with pytest.raises(ValidationError) as error:
        var.validate_value("Alex")

    assert error.value.messages == ["item #1: Missing required key price"]

    var.validate_value("Alex,1.2")


def test_csv_typed_required():
    var = SimpleCSV(
        csv_fields={
            "name": SimpleString(required),
            "balance": SimpleDecimal(required),
            "price": SimpleDecimal(optional),
        },
    )
    var.validate_value("Alex, 0")
    var.validate_value("Alex, 0, 1.2")
    with pytest.raises(ValidationError) as error:
        var.validate_value("Alex")

    assert error.value.messages == ["item #1: Missing required key balance"]

    var.validate_value("Alex,1.2")


def test_csv_value_validation():
    var = SimpleCSV(
        csv_fields={
            "name": SimpleString(required),
            "price": SimpleDecimal(optional),
        },
    )

    var.validate_value("Alex, 0")
    var.validate_value("Alex")

    with pytest.raises(ValidationError) as error:
        var.validate_value("Alex, zero")

    assert error.value.messages == ["item #1: key price: Enter a number."]


def test_csv_default_value():
    var = SimpleCSV(
        csv_fields={
            "name": SimpleString(required),
            "price": SimpleDecimal("0"),
        },
    )

    var.validate_value("Alex")
    var.validate_value("Alex, 10")

    assert var.give_python("Alex") == [{"name": "Alex", "price": Decimal("0")}]
    assert var.give_python("Alex, 10") == [{"name": "Alex", "price": Decimal("10")}]


@pytest.mark.parametrize(
    "in_data, out_data",
    [
        ("Alex", [{"name": "Alex"}]),
        ("Alex, 20", [{"name": "Alex", "age": "20"}]),
        ("Alex, 20, fail", [{"name": "Alex", "age": "20"}]),
        ("Alex, 20\nBob", [{"name": "Alex", "age": "20"}, {"name": "Bob"}]),
    ],
)
def test_csv_list_fields(in_data, out_data):
    var = SimpleCSV(
        csv_fields=["name", "age"],
    )
    var.validate_value(in_data)
    assert var.give_python(in_data) == out_data


@pytest.mark.parametrize(
    "in_data, out_data",
    [
        ("", "[]"),
        (
            "Alex",
            "[<div class='subitem'>{<div class='subitem'><i>name</i>: <pre>'Alex'</pre></div>}</div>]",
        ),
        (
            "Alex\nBob",
            "[<div class='subitem'>{<div class='subitem'><i>name</i>: <pre>'Alex'</pre></div>}</div>,<div class='subitem'>{<div class='subitem'><i>name</i>: <pre>'Bob'</pre></div>}</div>]",
        ),
        (
            "Alex, 20\nBob",
            "[<div class='subitem'>{<div class='subitem'><i>name</i>: <pre>'Alex'</pre></div>,<div class='subitem'><i>age</i>: <pre>'20'</pre></div>}</div>,<div class='subitem'>{<div class='subitem'><i>name</i>: <pre>'Bob'</pre></div>}</div>]",
        ),
        (
            "Alex, 20, ignore\nBob",
            "[<div class='subitem'>{<div class='subitem'><i>name</i>: <pre>'Alex'</pre></div>,<div class='subitem'><i>age</i>: <pre>'20'</pre></div>}</div>,<div class='subitem'>{<div class='subitem'><i>name</i>: <pre>'Bob'</pre></div>}</div>]",
        ),
        (
            "Alex, 20, ignore\nBob\nMike,",
            "[<div class='subitem'>{<div class='subitem'><i>name</i>: <pre>'Alex'</pre></div>,<div class='subitem'><i>age</i>: <pre>'20'</pre></div>}</div>,<div class='subitem'>{<div class='subitem'><i>name</i>: <pre>'Bob'</pre></div>}</div>,<div class='subitem'>{<div class='subitem'><i>name</i>: <pre>'Mike'</pre></div>,<div class='subitem'><i>age</i>: <pre>''</pre></div>}</div>]",
        ),
    ],
)
def test_csv_list_fields_preview(in_data, out_data):
    var = SimpleCSV(
        csv_fields=["name", "age"],
    )
    assert var.get_admin_preview_value(in_data, "VAR") == out_data


@pytest.mark.skipif(yaml_installed, reason="yaml is installed")
def test_yaml_not_installed():
    with pytest.raises(AssertionError):
        var = SimpleYAML()


@pytest.mark.skipif(not yaml_installed, reason="yaml is not installed")
def test_yaml():
    var = SimpleYAML()

    text = """
- name: Kateryna
  price: 1.2
- name: The Will
  price: 200
        """

    assert var.give_python(text) == [
        {"name": "Kateryna", "price": 1.2},
        {"name": "The Will", "price": 200},
    ]


def test_attribute_suffix():
    from content_settings.conf import content_settings

    assert content_settings.BOOKS == [
        {"name": "Kateryna", "price": Decimal("1.2"), "is_available": True},
        {"name": "The Will", "price": Decimal("200"), "is_available": False},
        {"name": "The Poplar", "price": Decimal("12"), "is_available": True},
        {"name": "The Night of Taras", "price": Decimal("12"), "is_available": True},
    ]

    assert content_settings.BOOKS__available_names == [
        "Kateryna",
        "The Poplar",
        "The Night of Taras",
    ]


def test_lazy_attribute_suffix():
    from content_settings.conf import content_settings
    from content_settings.types.lazy import LazyObject

    assert isinstance(content_settings.lazy__BOOKS, LazyObject)
    assert list(content_settings.lazy__BOOKS) == [
        {"name": "Kateryna", "price": Decimal("1.2"), "is_available": True},
        {"name": "The Will", "price": Decimal("200"), "is_available": False},
        {"name": "The Poplar", "price": Decimal("12"), "is_available": True},
        {"name": "The Night of Taras", "price": Decimal("12"), "is_available": True},
    ]

    assert isinstance(content_settings.lazy__BOOKS__available_names, LazyObject)
    assert list(content_settings.lazy__BOOKS__available_names) == [
        "Kateryna",
        "The Poplar",
        "The Night of Taras",
    ]
