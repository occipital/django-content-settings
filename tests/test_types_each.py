import pytest
from decimal import Decimal

from django.core.exceptions import ValidationError

from content_settings.types.basic import (
    SimpleString,
    SimpleDecimal,
)
from content_settings.types.markup import (
    SimpleJSON,
)
from content_settings.types.each import EachMixin, Item, Keys, Values
from content_settings.types.mixins import mix
from content_settings.types.template import DjangoTemplateNoArgs
from content_settings.types.mixins import mix, DictSuffixesMixin
from content_settings.types.markup import SimpleYAML
from content_settings.types.basic import SimpleHTML
from content_settings.types import required, optional
from content_settings.types.array import SplitTranslation


pytestmark = [pytest.mark.django_db]


class EachJSON(EachMixin, SimpleJSON):
    pass


@pytest.mark.parametrize(
    "var, value, expected",
    [
        pytest.param(
            EachJSON(each=Keys(price=SimpleDecimal())),
            '{"name": "Book", "price": "100"}',
            {"name": "Book", "price": Decimal("100")},
            id="simple_keys_decimal",
        ),
        pytest.param(
            EachJSON(each=Keys(name=SimpleString(), price=SimpleDecimal())),
            '{"name": "Book", "price": "100"}',
            {"name": "Book", "price": Decimal("100")},
            id="simple_keys_string_decimal",
        ),
        pytest.param(
            EachJSON(each=Keys(name=SimpleString(), price=SimpleDecimal())),
            '{"name": "Book"}',
            {"name": "Book", "price": None},
            id="simple_keys_string_decimal_none",
        ),
        pytest.param(
            EachJSON(each=Keys(name=SimpleString(), price=SimpleDecimal(optional))),
            '{"name": "Book"}',
            {"name": "Book"},
            id="simple_keys_string_decimal_optional",
        ),
        pytest.param(
            EachJSON(each=Keys(name=SimpleString(), price=SimpleDecimal("100"))),
            '{"name": "Book"}',
            {"name": "Book", "price": Decimal("100")},
            id="simple_keys_string_decimal_default",
        ),
        pytest.param(
            EachJSON(each=Item(Keys(name=SimpleString(), price=SimpleDecimal()))),
            '[{"name": "Book", "price": "100"}, {}]',
            [{"name": "Book", "price": Decimal("100")}, {"name": "", "price": None}],
            id="simple_keys_decimal_empty_row",
        ),
        pytest.param(
            EachJSON(each=Values(SimpleDecimal())),
            '{"book": "30", "cover": "0.5"}',
            {"book": Decimal("30"), "cover": Decimal("0.5")},
            id="simple_values_decimal",
        ),
        pytest.param(
            EachJSON(each=Values(SimpleDecimal())),
            "{}",
            {},
            id="simple_values_empty",
        ),
        pytest.param(
            EachJSON(each=Values(SimpleDecimal())),
            '"50"',
            "50",
            id="simple_values_not_a_dict",
        ),
        pytest.param(
            EachJSON(each=Item(Values(SimpleDecimal()))),
            '[{"book": "30", "cover": "0.5"}]',
            [{"book": Decimal("30"), "cover": Decimal("0.5")}],
            id="simple_item_values_decimal",
        ),
    ],
)
def test_validate_give(var, value, expected):
    var.validate_value(value)
    assert var.give_python(value) == expected


@pytest.mark.parametrize(
    "var, value, expected",
    [
        pytest.param(
            EachJSON(each=Keys(price=SimpleDecimal())),
            '{"name": "Book", "price": "Zero"}',
            "key price: Enter a number.",
            id="key_price",
        ),
        pytest.param(
            EachJSON(each=Keys(price=SimpleDecimal(required))),
            '{"name": "Book"}',
            "Missing required key price",
            id="key_required",
        ),
        pytest.param(
            EachJSON(each=Item(Keys(price=SimpleDecimal(required)))),
            '[{"name": "Book"}]',
            "item #1: Missing required key price",
            id="item_missing_required",
        ),
    ],
)
def test_each_validate(var, value, expected):
    with pytest.raises(ValidationError) as e:
        var.validate_value(value)
    assert e.value.message == expected


def test_preview_admin_html():
    var = mix(EachMixin, SimpleYAML)(
        "",
        each=Item(
            Keys(
                name=SimpleString(optional, help="The name of the song"),
                translation=SimpleHTML(optional, help="The translation of the song"),
            )
        ),
        help="The yaml of the site",
    )
    assert (
        var.get_admin_preview_value(
            """
- name: Song
  translation: '<b>Translation</b>'
""",
            "VAR",
        )
        == "[<div class='subitem'>{<div class='subitem'><i>name</i>: <pre>'Song'</pre></div>,<div class='subitem'><i>translation</i>: <b>Translation</b></div>}</div>]"
    )


def test_preview_admin_translation():
    var = mix(EachMixin, SimpleYAML)(
        "",
        each=Item(
            Keys(
                name=SimpleString(optional, help="The name of the song"),
                translation=SplitTranslation(
                    optional, help="The translation of the song"
                ),
            )
        ),
        help="The yaml of the site",
    )
    assert (
        var.get_admin_preview_value(
            """
- name: Song
  translation: >
    === EN ===\n
    English Shong\n
    === UA ===\n
    Ukrainian Song\n                     
""",
            "VAR",
        )
        == "[<div class='subitem'>{<div class='subitem'><i>name</i>: <pre>'Song'</pre></div>,<div class='subitem'><i>translation</i>: <div> <b>EN</b>  <a class=\"cs_set_params\" data-param-suffix=\"UA\">UA</a> </div><pre>'English Shong'</pre></div>}</div>]"
    )


def test_preview_admin_with_unknown_html():
    var = mix(EachMixin, SimpleYAML)(
        "",
        each=Item(
            Keys(
                name=SimpleString(optional, help="The name of the song"),
            )
        ),
        help="The yaml of the site",
    )
    assert (
        var.get_admin_preview_value(
            """
- name: Song
  translation: '<b>Translation</b>'
""",
            "VAR",
        )
        == "[<div class='subitem'>{<div class='subitem'><i>name</i>: <pre>'Song'</pre></div>,<div class='subitem'><i>translation</i>: <pre>&lt;b>Translation&lt;/b></pre></div>}</div>]"
    )
