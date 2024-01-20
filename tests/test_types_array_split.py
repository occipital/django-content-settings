import pytest
from decimal import Decimal

from django.core.exceptions import ValidationError
from django.test import Client

from content_settings.models import ContentSetting
from content_settings.types.basic import SimpleText, SimpleDecimal
from content_settings.types.mixins import mix, DictSuffixesMixin
from content_settings.types.array import (
    SplitByFirstLine,
    NOT_FOUND_DEFAULT,
    NOT_FOUND_KEY_ERROR,
    NOT_FOUND_VALUE,
    SPLIT_SUFFIX_USE_PARENT,
    SPLIT_SUFFIX_SPLIT_OWN,
    SPLIT_SUFFIX_SPLIT_PARENT,
)

pytestmark = [pytest.mark.django_db(transaction=True)]


def test_help():
    var = SplitByFirstLine(split_default_key="EN", help="Some Help")
    assert var.get_help() == "Some Help"


def test_empty_line():
    var = SplitByFirstLine(split_default_key="EN")
    var.validate_value("")
    assert var.to_python("") == {"EN": ""}
    assert var.give_python("") == ""


def test_without_splitter():
    var = SplitByFirstLine(split_default_key="EN")
    var.validate_value("A Simple Line")
    assert var.to_python("A Simple Line") == {"EN": "A Simple Line"}
    assert var.give_python("A Simple Line") == "A Simple Line"


def test_with_only_one_value():
    var = SplitByFirstLine(split_default_key="EN")
    text = """
==== EN ====
A Simple Line
    """.strip()
    var.validate_value(text)
    assert var.to_python(text) == {"EN": "A Simple Line"}
    assert var.give_python(text) == "A Simple Line"


def test_with_two_values():
    var = SplitByFirstLine(split_default_key="EN")
    text = """
==== EN ====
A Simple Line
==== UA ====
Проста Лінія
    """.strip()
    var.validate_value(text)
    assert var.to_python(text) == {"EN": "A Simple Line", "UA": "Проста Лінія"}
    assert var.give_python(text) == "A Simple Line"
    assert var.give_python(text, "ua") == "Проста Лінія"


def test_with_two_decimal_values():
    var = SplitByFirstLine(split_default_key="EN", split_type=SimpleDecimal())
    text = """
==== EN ====
4.5
==== UA ====
3.3
    """.strip()
    var.validate_value(text)
    assert var.to_python(text) == {"EN": Decimal("4.5"), "UA": Decimal("3.3")}


def test_with_two_decimal_values_custom_spliter():
    def split_values(text):
        return dict([val.split(":") for val in text.split()])

    var = SplitByFirstLine(
        split_default_key="EN", split_type=SimpleDecimal(), split_values=split_values
    )
    text = "EN:4.5 UA:3.3"
    var.validate_value(text)
    assert var.to_python(text) == {"EN": Decimal("4.5"), "UA": Decimal("3.3")}


def test_validate_value():
    var = SplitByFirstLine(split_default_key="EN", split_type=SimpleDecimal())
    text = """
==== EN ====
4.5
==== UA ====
second
    """.strip()
    with pytest.raises(ValidationError) as err:
        var.validate_value(text)
    assert err.value.message == "UA: ['Enter a number.']"

    text = """
==== EN ====
one
==== UA ====
second
    """.strip()
    with pytest.raises(ValidationError) as err:
        var.validate_value(text)
    assert err.value.message == "Enter a number."


def test_default_chooser_two_possible():
    choice = "EN"

    def split_default_chooser(value):
        return choice

    var = SplitByFirstLine(
        split_default_key="EN", split_default_chooser=split_default_chooser
    )
    text = """
==== EN ====
A Simple Line
==== UA ====
Проста Лінія
    """.strip()
    var.validate_value(text)
    assert var.give_python(text) == "A Simple Line"

    choice = "UA"
    assert var.give_python(text) == "Проста Лінія"


def test_default_chooser_one_possible():
    choice = "EN"

    def split_default_chooser(value):
        return choice

    var = SplitByFirstLine(
        split_default_key="EN", split_default_chooser=split_default_chooser
    )
    text = """
A Simple Line
    """.strip()
    var.validate_value(text)
    assert var.give_python(text) == "A Simple Line"


def test_split_not_found_default():
    var = SplitByFirstLine(split_default_key="EN", split_not_found=NOT_FOUND_DEFAULT)
    text = """
==== EN ====
A Simple Line
==== UA ====
Проста Лінія
    """.strip()
    assert var.give_python(text, "ff") == "A Simple Line"


def test_split_not_found_value():
    var = SplitByFirstLine(
        split_default_key="EN",
        split_not_found=NOT_FOUND_VALUE,
        split_not_found_value="Not Found",
    )
    text = """
==== EN ====
A Simple Line
==== UA ====
Проста Лінія
    """.strip()
    assert var.give_python(text, "ff") == "Not Found"


def test_split_not_found_key_error():
    var = SplitByFirstLine(split_default_key="EN", split_not_found=NOT_FOUND_KEY_ERROR)
    text = """
==== EN ====
A Simple Line
==== UA ====
Проста Лінія
    """.strip()

    with pytest.raises(KeyError) as err:
        var.give_python(text, "ff")


def test_split_key_validator():
    def split_validator(value):
        if value not in ["EN", "UA"]:
            raise ValidationError(f"Wrong Name {value}")

    var = SplitByFirstLine(split_default_key="EN", split_key_validator=split_validator)
    text = """
==== EN ====
4.5
==== UA ====
70
    """.strip()
    var.validate_value(text)

    text = """
==== EN ====
4.5
==== UA ====
70
==== FF ====
80
    """.strip()

    with pytest.raises(ValidationError) as err:
        var.validate_value(text)
    assert err.value.message == "Wrong Name FF"


class TruncText(DictSuffixesMixin, SimpleText):
    suffixes = {
        "trunc": lambda text, max_length=10: (text[: max_length - 3] + "...")
        if len(text) > max_length
        else text
    }


class SplitTruncText(SplitByFirstLine):
    split_type = TruncText()
    split_default_key = "EN"
    is_ua = False

    def split_default_choose(self, value):
        return "UA" if self.is_ua else "EN"


def test_split_trunc_text():
    var = SplitTruncText()
    text = """
==== EN ====
A Simple Line
==== UA ====
Проста Лінія
    """.strip()
    assert var.give_python(text) == "A Simple Line"
    assert var.give_python(text, "ua") == "Проста Лінія"

    var.is_ua = True
    assert var.give_python(text) == "Проста Лінія"
    assert var.give_python(text, "en") == "A Simple Line"


def test_split_trunc_text_use_parent():
    var = SplitTruncText(split_suffix=SPLIT_SUFFIX_USE_PARENT)
    text = """
==== EN ====
A Simple Line
==== UA ====
Проста Лінія
    """.strip()
    assert var.give_python(text) == "A Simple Line"
    assert var.give_python(text, "trunc") == "A Simpl..."


def test_split_trunc_text_split_own():
    var = SplitTruncText(split_suffix=SPLIT_SUFFIX_SPLIT_OWN, split_suffix_value="_to_")
    text = """
==== EN ====
A Simple Line
==== UA ====
Проста Лінія
    """.strip()
    assert var.give_python(text) == "A Simple Line"
    assert var.give_python(text, "ua") == "Проста Лінія"
    assert var.give_python(text, "trunc") == "A Simple Line"
    assert var.give_python(text, "ua_to_trunc") == "Проста ..."
    assert var.give_python(text, "en_to_trunc") == "A Simpl..."


def test_split_trunc_text_split_parent():
    var = SplitTruncText(
        split_suffix=SPLIT_SUFFIX_SPLIT_PARENT, split_suffix_value="_to_"
    )
    text = """
==== EN ====
A Simple Line
==== UA ====
Проста Лінія
    """.strip()
    assert var.give_python(text) == "A Simple Line"
    with pytest.raises(KeyError) as err:
        var.give_python(text, "ua")

    assert var.give_python(text, "trunc") == "A Simpl..."

    var.is_ua = True
    assert var.give_python(text, "trunc") == "Проста ..."
    assert var.give_python(text, "en_to_trunc") == "A Simpl..."


def test_split_translation_with_default_value():
    client = Client()
    resp = client.get("/content-settings/fetch/COMPANY_DESCRIPTION/")
    assert resp.status_code == 200
    assert resp.json() == {
        "COMPANY_DESCRIPTION": "The best Company",
    }

    resp = client.get(
        "/content-settings/fetch/COMPANY_DESCRIPTION/", HTTP_ACCEPT_LANGUAGE="ua"
    )
    assert resp.status_code == 200
    assert resp.json() == {
        "COMPANY_DESCRIPTION": "The best Company",
    }


def test_split_translation_with_available_translations():
    cs = ContentSetting.objects.get(name="COMPANY_DESCRIPTION")
    cs.value = """
!!!! EN !!!!
The best Company
!!!! ES !!!!
La mejor empresa
    """.strip()
    cs.save()

    client = Client()
    resp = client.get(
        "/content-settings/fetch/COMPANY_DESCRIPTION/",
        headers={"accept-language": "en"},
    )
    assert resp.status_code == 200
    assert resp.json() == {
        "COMPANY_DESCRIPTION": "The best Company",
    }

    resp = client.get(
        "/content-settings/fetch/COMPANY_DESCRIPTION/",
        headers={"accept-language": "es"},
    )
    assert resp.status_code == 200
    assert resp.json() == {
        "COMPANY_DESCRIPTION": "La mejor empresa",
    }
