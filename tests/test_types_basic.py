import pytest
from decimal import Decimal

from django.test import Client
from django.core.exceptions import ValidationError

from content_settings.types.basic import (
    SimpleString,
    SimpleText,
    SimpleInt,
    SimpleDecimal,
    SimpleBool,
    EmailString,
)
from content_settings.types.mixins import (
    MinMaxValidationMixin,
    CallToPythonMixin,
    mix,
)
from content_settings.models import ContentSetting
from content_settings.caching import recalc_checksums


pytestmark = [pytest.mark.django_db]


def test_simple_string():
    var = SimpleString()

    assert var.give_python("New BookStore") == "New BookStore"


def test_simple_string_empty_is_none():
    var = SimpleString()

    assert var.give_python("") == ""

    var = SimpleString(empty_is_none=True)

    assert var.give_python("") is None


def test_simple_text():
    var = SimpleText()

    assert var.give_python("New BookStore") == "New BookStore"


def test_simple_int():
    var = SimpleInt()

    assert var.give_python("123") == 123
    assert var.give_python("-1") == -1
    assert var.give_python("0") == 0


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

    assert var.give_python("123.45") == Decimal("123.45")
    assert var.give_python("-1.23") == Decimal("-1.23")
    assert var.give_python("0.0") == Decimal("0.0")


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

    assert var.give_python("1") is True
    assert var.give_python("0") is False
    assert var.give_python("") is False


class SimpleFormat(CallToPythonMixin, SimpleString):
    def prepare_python_call(self, value):
        return {"prepared": value.format}

    def python_call(self, name, prepared):
        return prepared(name=name)


def test_call():
    var = SimpleFormat()

    assert var.give_python("Hello, {name}!")("John") == "Hello, John!"


def test_assert_unknown_attribute():
    with pytest.raises(AssertionError):
        var = SimpleFormat(unknown="value")


def test_assert_default_not_string():
    with pytest.raises(AssertionError):
        var = SimpleFormat(123)


def test_assert_version_not_string():
    with pytest.raises(AssertionError):
        var = SimpleFormat("123", version=2)


def test_assert_version_not_supported():
    from content_settings.settings import CACHE_SPLITER

    with pytest.raises(AssertionError):
        var = SimpleFormat("123", version=f"2{CACHE_SPLITER}1")


def test_email_validate_fail():
    var = EmailString()
    with pytest.raises(ValidationError) as error:
        var.validate_value("invalid email")
    assert error.value.message == "Enter a valid email address."


def test_email_validate_fail():
    var = EmailString()
    var.validate_value("name@checkio.org")


def test_simple_html_template_tag():
    cs = ContentSetting.objects.get(name="TITLE")
    cs.value = "<h1>Simple HTML</h1>"
    cs.save()

    recalc_checksums()

    client = Client()
    resp = client.get("/books/simple-html/")
    assert resp.status_code == 200
    assert (
        resp.content
        == b"SIMPLE_HTML_FIELD: <h1>Simple HTML</h1>\n\nTITLE: &lt;h1&gt;Simple HTML&lt;/h1&gt;"
    )
