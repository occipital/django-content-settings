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
)
from content_settings.types.each import (
    EachMixin,
    Item,
    Keys,
)
from content_settings.types.mixins import mix
from content_settings.types.template import DjangoTemplateNoArgs
from content_settings.types.mixins import mix, DictSuffixesMixin
from content_settings.types import required, optional


pytestmark = [pytest.mark.django_db]


class EachJSON(EachMixin, SimpleJSON):
    pass


@pytest.mark.parametrize(
    "name, var, value, expected",
    [
        (
            "simple keys decimal",
            EachJSON(each=Keys(price=SimpleDecimal())),
            '{"name": "Book", "price": "100"}',
            {"name": "Book", "price": Decimal("100")},
        ),
        (
            "simple keys string+decimal",
            EachJSON(each=Keys(name=SimpleString(), price=SimpleDecimal())),
            '{"name": "Book", "price": "100"}',
            {"name": "Book", "price": Decimal("100")},
        ),
        (
            "simple keys string+decimal(None)",
            EachJSON(each=Keys(name=SimpleString(), price=SimpleDecimal())),
            '{"name": "Book"}',
            {"name": "Book", "price": None},
        ),
        (
            "simple keys string+decimal(None)",
            EachJSON(each=Keys(name=SimpleString(), price=SimpleDecimal(optional))),
            '{"name": "Book"}',
            {"name": "Book"},
        ),
        (
            "simple keys string+decimal(default)",
            EachJSON(each=Keys(name=SimpleString(), price=SimpleDecimal("100"))),
            '{"name": "Book"}',
            {"name": "Book", "price": Decimal("100")},
        ),
        (
            "simple keys string+decimal(required but provided)",
            EachJSON(each=Keys(name=SimpleString(), price=SimpleDecimal(required))),
            '{"name": "Book", "price": "100"}',
            {"name": "Book", "price": Decimal("100")},
        ),
        (
            "item simple keys string+decimal",
            EachJSON(each=Item(Keys(name=SimpleString(), price=SimpleDecimal()))),
            '[{"name": "Book", "price": "100"}]',
            [{"name": "Book", "price": Decimal("100")}],
        ),
        (
            "item simple keys string+decimal + one empty row",
            EachJSON(each=Item(Keys(name=SimpleString(), price=SimpleDecimal()))),
            '[{"name": "Book", "price": "100"}, {}]',
            [{"name": "Book", "price": Decimal("100")}, {"name": "", "price": None}],
        ),
    ],
)
def test_each_keys_decimal(name, var, value, expected):
    var.validate_value(value)
    assert var.give_python(value) == expected


@pytest.mark.parametrize(
    "name, var, value, expected",
    [
        (
            "simple keys Enter a number",
            EachJSON(each=Keys(price=SimpleDecimal())),
            '{"name": "Book", "price": "Zero"}',
            "key price: Enter a number.",
        ),
        (
            "simple keys required",
            EachJSON(each=Keys(price=SimpleDecimal(required))),
            '{"name": "Book"}',
            "Missing required key price",
        ),
        (
            "item keys required",
            EachJSON(each=Item(Keys(price=SimpleDecimal(required)))),
            '[{"name": "Book"}]',
            "item #1: Missing required key price",
        ),
    ],
)
def test_each_validate(name, var, value, expected):
    with pytest.raises(ValidationError) as e:
        var.validate_value(value)
    assert e.value.message == expected
