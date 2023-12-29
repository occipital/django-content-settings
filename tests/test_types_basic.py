import pytest
from decimal import Decimal

from content_settings.types.basic import (
    SimpleString,
    SimpleText,
    SimpleInt,
    SimpleDecimal,
    SimpleBool,
)
from content_settings.types.mixins import (
    MinMaxValidationMixin,
    CallToPythonMixin,
    mix,
)

from django.core.exceptions import ValidationError

pytestmark = [pytest.mark.django_db]


def test_simple_string():
    var = SimpleString()

    assert var.to_python("New BookStore") == "New BookStore"


def test_simple_string_empty_is_none():
    var = SimpleString()

    assert var.to_python("") == ""

    var = SimpleString(empty_is_none=True)

    assert var.to_python("") is None


def test_simple_text():
    var = SimpleText()

    assert var.to_python("New BookStore") == "New BookStore"


def test_simple_int():
    var = SimpleInt()

    assert var.to_python("123") == 123
    assert var.to_python("-1") == -1
    assert var.to_python("0") == 0


def test_simple_int_validate():
    var = SimpleInt()

    with pytest.raises(ValidationError) as error:
        var.validate_value("zero")
    assert error.value.message == "Enter a whole number."


def test_simple_int_min_max_validate_mixin():
    var = mix(MinMaxValidationMixin, SimpleInt)(min_value=100)
    with pytest.raises(ValidationError) as error:
        var.validate_value("5")
    assert error.value.message == "Value cannot be less than 100"
    var.validate_value("102")

    var = mix(MinMaxValidationMixin, SimpleInt)(max_value=100)
    with pytest.raises(ValidationError) as error:
        var.validate_value("120")
    assert error.value.message == "Value cannot be greater than 100"
    var.validate_value("70")

    with pytest.raises(ValidationError) as error:
        var.validate_value("")
    assert error.value.message == "Value cannot be None"


def test_simple_decimal():
    var = SimpleDecimal()

    assert var.to_python("123.45") == Decimal("123.45")
    assert var.to_python("-1.23") == Decimal("-1.23")
    assert var.to_python("0.0") == Decimal("0.0")


def test_simple_decimal_validate():
    var = SimpleDecimal()

    with pytest.raises(ValidationError) as error:
        var.validate_value("zero")
    assert error.value.message == "Enter a number."


def test_simple_decimal_validate_min():
    var = mix(MinMaxValidationMixin, SimpleDecimal)(min_value=0)

    with pytest.raises(ValidationError) as error:
        var.validate_value("-2")
    assert error.value.message == "Value cannot be less than 0"


def test_bool():
    var = SimpleBool()

    assert var.to_python("1") is True
    assert var.to_python("0") is False
    assert var.to_python("") is False


class SimpleFormat(CallToPythonMixin, SimpleString):
    def prepare_python_call(self, value):
        return {"prepared": value.format}

    def python_call(self, name, prepared):
        return prepared(name=name)


def test_call():
    var = SimpleFormat()

    assert var.to_python("Hello, {name}!")("John") == "Hello, John!"
