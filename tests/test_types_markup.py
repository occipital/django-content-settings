import pytest
from decimal import Decimal

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
from content_settings.types.mixins import mix, DictSuffixesMixin


pytestmark = [pytest.mark.django_db]

yaml_installed = False
try:
    import yaml

    yaml_installed = True
except ImportError:
    pass


def test_simple_json():
    var = SimpleJSON()

    assert var.give_python('{"a": 45}') == {"a": 45}


def test_simple_json_empty_is_none():
    var = SimpleJSON(empty_is_none=True)

    assert var.give_python("") is None
    assert var.give_python(" ") is None


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
    var = SimpleCSV(fields=["name", "price"])

    assert var.give_python(CSV_TEXT) == [
        {"name": "Kateryna", "price": "1.2"},
        {"name": "The Will", "price": "200"},
    ]


def test_csv_typed():
    var = SimpleCSV(
        fields={
            "name": SimpleString(),
            "price": SimpleDecimal(),
        }
    )

    assert var.give_python(CSV_TEXT) == [
        {"name": "Kateryna", "price": Decimal("1.2")},
        {"name": "The Will", "price": Decimal("200")},
    ]


def test_csv_typed_suffix():
    var = mix(DictSuffixesMixin, SimpleCSV)(
        fields={
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
        fields={
            "name": SimpleString(),
            "price": SimpleDecimal(),
            "pic": DjangoTemplateNoArgs(),
        }
    )

    assert var.give_python(
        """
Kateryna,1.2,{{SETTINGS.STATIC_URL}}cover/kateryna.jpg
The Will,200,{{SETTINGS.STATIC_URL}}cover/will.jpg
    """
    ) == [
        {
            "name": "Kateryna",
            "price": Decimal("1.2"),
            "pic": "/static/cover/kateryna.jpg",
        },
        {"name": "The Will", "price": Decimal("200"), "pic": "/static/cover/will.jpg"},
    ]


def test_csv_overload():
    var = SimpleCSV(fields=["name", "price"])

    text = """
Kateryna,1.2,light
The Will,200
    """

    assert var.give_python(text) == [
        {"name": "Kateryna", "price": "1.2"},
        {"name": "The Will", "price": "200"},
    ]


def test_csv_missing():
    var = SimpleCSV(fields=["name", "price"])

    text = """
Kateryna,1.2
The Will
    """

    assert var.give_python(text) == [
        {"name": "Kateryna", "price": "1.2"},
        {"name": "The Will"},
    ]


def test_csv_empty():
    var = SimpleCSV(fields=["name", "price"])

    text = ""

    assert var.give_python(text) == []


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
