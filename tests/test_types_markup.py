import pytest
from decimal import Decimal

from django.core.exceptions import ValidationError

from content_settings.types.basic import (
    SimpleString,
    SimpleDecimal,
)
from content_settings.types.markup import (
    SimpleJSON,
    SimpleCSV,
    SimpleYAML,
)


pytestmark = [pytest.mark.django_db]

yaml_installed = False
try:
    import yaml

    yaml_installed = True
except ImportError:
    pass


def test_simple_json():
    var = SimpleJSON()

    assert var.to_python('{"a": 45}') == {"a": 45}


def test_simple_json_empty_is_none():
    var = SimpleJSON(empty_is_none=True)

    assert var.to_python("") is None
    assert var.to_python(" ") is None


def test_simple_json_invalid():
    var = SimpleJSON()

    with pytest.raises(ValidationError) as error:
        var.to_python("invalid json")

    assert error.value.messages == ["Expecting value: line 1 column 1 (char 0)"]


CSV_TEXT = """
Kateryna,1.2
The Will,200
    """


def test_csv():
    var = SimpleCSV(fields=["name", "price"])

    assert var.to_python(CSV_TEXT) == [
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

    assert var.to_python(CSV_TEXT) == [
        {"name": "Kateryna", "price": Decimal("1.2")},
        {"name": "The Will", "price": Decimal("200")},
    ]


def test_csv_overload():
    var = SimpleCSV(fields=["name", "price"])

    text = """
Kateryna,1.2,light
The Will,200
    """

    assert var.to_python(text) == [
        {"name": "Kateryna", "price": "1.2"},
        {"name": "The Will", "price": "200"},
    ]


def test_csv_missing():
    var = SimpleCSV(fields=["name", "price"])

    text = """
Kateryna,1.2
The Will
    """

    assert var.to_python(text) == [
        {"name": "Kateryna", "price": "1.2"},
        {"name": "The Will"},
    ]


def test_csv_empty():
    var = SimpleCSV(fields=["name", "price"])

    text = ""

    assert var.to_python(text) == []


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

    assert var.to_python(text) == [
        {"name": "Kateryna", "price": 1.2},
        {"name": "The Will", "price": 200},
    ]
