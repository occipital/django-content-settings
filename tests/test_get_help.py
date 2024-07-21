import pytest
import django

from content_settings.types import required, optional
from content_settings.types.basic import (
    SimpleString,
    SimpleInt,
    SimpleText,
    SimpleHTML,
    SimpleDecimal,
    SimpleBool,
    URLString,
    EmailString,
    SimplePassword,
)
from content_settings.types.datetime import (
    DateTimeString,
    DateString,
    TimeString,
    SimpleTimedelta,
)
from content_settings.types.markup import SimpleYAML, SimpleJSON, SimpleCSV
from content_settings.types.template import (
    DjangoTemplate,
    DjangoModelTemplate,
    SimpleEval,
    SimpleExec,
)
from content_settings.types.array import (
    SimpleStringsList,
    TypedStringsList,
    SplitTranslation,
)

from tests.books.models import Book
from tests.tools import adjust_id_params
from tests import yaml_installed, testing_settings_full

pytestmark = [pytest.mark.django_db(transaction=True)]


@pytest.mark.parametrize(
    "var,value,initial",
    adjust_id_params(
        [
            (
                "SimpleString",
                SimpleString(),
                "string",
            ),
            (
                "SimpleString_with_help",
                SimpleString(help="A value"),
                "A value<br><br>string",
            ),
            (
                "SimpleString_with_help_text",
                SimpleString(help_text="A value"),
                "A value<br><br>string",
            ),
            (
                "SimpleString_with_help_format",
                SimpleString(help="A value", help_format="A format"),
                "A value<br><br>A format",
            ),
            (
                "SimpleString_with_help_format_only",
                SimpleString(help_format="A format"),
                "A format",
            ),
            (
                "SimpleInt_with_help",
                SimpleInt(help="A value"),
                "A value<br><br>Any number",
            ),
            (
                "SimpleBool_with_help",
                SimpleBool(help="A value"),
                "A value<br><br>boolean (True/False) value. Accepted values: 'yes', 'true', '1', '+', 'ok', 'no', 'not', 'false', '0', '-', empty",
            ),
            (
                "SimpleText_with_help",
                SimpleText(help="A value"),
                "A value<br><br>string",
            ),
            (
                "SimpleHTML_with_help",
                SimpleHTML(help="A value"),
                "A value<br><br>string in HTML format",
            ),
            (
                "URLString_with_help",
                URLString(help="A value"),
                "A value<br><br>URL",
            ),
            (
                "EmailString_with_help",
                EmailString(help="A value"),
                "A value<br><br>Email",
            ),
            (
                "SimpleDecimal_with_help",
                SimpleDecimal(help="A value"),
                "A value<br><br>Decimal number with floating point",
            ),
            (
                "SimplePassword_with_help",
                SimplePassword(help="A value"),
                (
                    "<i>Do Not Share</i><br>A value<br><br>string"
                    if testing_settings_full
                    else "A value<br><br>string"
                ),
            ),
            (
                "DateTimeString_with_help",
                DateTimeString(help="A value"),
                (
                    r"A value<br><br>Use any of the following formats: <ul><li>%Y-%m-%d %H:%M:%S</li><li>%Y-%m-%d %H:%M:%S.%f</li><li>%Y-%m-%d %H:%M</li><li>%m/%d/%Y %H:%M:%S</li><li>%m/%d/%Y %H:%M:%S.%f</li><li>%m/%d/%Y %H:%M</li><li>%m/%d/%y %H:%M:%S</li><li>%m/%d/%y %H:%M:%S.%f</li><li>%m/%d/%y %H:%M</li><li>%Y-%m-%d</li></ul>"
                    if django.VERSION > (3, 3)
                    else r"A value<br><br>Use any of the following formats: <ul><li>%Y-%m-%d %H:%M:%S</li><li>%Y-%m-%d %H:%M:%S.%f</li><li>%Y-%m-%d %H:%M</li><li>%m/%d/%Y %H:%M:%S</li><li>%m/%d/%Y %H:%M:%S.%f</li><li>%m/%d/%Y %H:%M</li><li>%m/%d/%y %H:%M:%S</li><li>%m/%d/%y %H:%M:%S.%f</li><li>%m/%d/%y %H:%M</li></ul>"
                ),
            ),
            (
                "DateString_with_help",
                DateString(help="A value"),
                r"A value<br><br>Use any of the following formats: <ul><li>%Y-%m-%d</li><li>%m/%d/%Y</li><li>%m/%d/%y</li><li>%b %d %Y</li><li>%b %d, %Y</li><li>%d %b %Y</li><li>%d %b, %Y</li><li>%B %d %Y</li><li>%B %d, %Y</li><li>%d %B %Y</li><li>%d %B, %Y</li></ul>",
            ),
            (
                "TimeString_with_help",
                TimeString(help="A value"),
                "A value<br><br>Use any of the following formats: <ul><li>%H:%M:%S</li><li>%H:%M:%S.%f</li><li>%H:%M</li></ul>",
            ),
            (
                "SimpleTimedelta_with_help",
                SimpleTimedelta(help="A value"),
                "A value<br><br>Time Delta Format<ul><li>s - seconds</li><li>m - minutes</li><li>h - hours</li><li>d - days</li><li>w - weeks</li></ul>Examples:<ul><li>1d - in one day</li><li>1d 3h - in one day and 3 hours</li></ul>",
            ),
            (
                "SimpleJSON_with_help",
                SimpleJSON(help="A value"),
                "A value<br><br>Simple <a href='https://en.wikipedia.org/wiki/JSON' target='_blank'>JSON format</a>",
            ),
            (
                "SimpleCSV_with_help",
                SimpleCSV(help="A value", csv_fields=["id", "name"]),
                "A value<br><br>Simple <a href='https://en.wikipedia.org/wiki/Comma-separated_values' target='_blank'>CSV format</a>A list of items. Each item should be: <div class='subitem'>A dictionary. Keys: <div class='subitem'><i>id</i> - (optional) string</div><div class='subitem'><i>name</i> - (optional) string</div></div>",
            ),
            (
                "SimpleCSV_with_help_fields",
                SimpleCSV(
                    help="A value",
                    csv_fields={
                        "name": SimpleString(required),
                        "value": SimpleString(default="default value"),
                        "description": SimpleString(optional),
                    },
                ),
                "A value<br><br>Simple <a href='https://en.wikipedia.org/wiki/Comma-separated_values' target='_blank'>CSV format</a>A list of items. Each item should be: <div class='subitem'>A dictionary. Keys: <div class='subitem'><i>name</i> - (required) string</div><div class='subitem'><i>value</i> - (default: default value) string</div><div class='subitem'><i>description</i> - (optional) string</div></div>",
            ),
            (
                "SimpleCSV_with_help_fields_default",
                SimpleCSV(
                    help="A value",
                    csv_fields={
                        "name": SimpleString(),
                        "price": SimpleDecimal("0"),
                    },
                ),
                "A value<br><br>Simple <a href='https://en.wikipedia.org/wiki/Comma-separated_values' target='_blank'>CSV format</a>A list of items. Each item should be: <div class='subitem'>A dictionary. Keys: <div class='subitem'><i>name</i> - (default: <i>empty</i>) string</div><div class='subitem'><i>price</i> - (default: 0) Decimal number with floating point</div></div>",
            ),
            (
                "DjangoTemplate_with_help",
                DjangoTemplate(help="A value"),
                "A value<br><br>Simple <a href='https://docs.djangoproject.com/en/3.2/topics/templates/' target='_blank'>Django Template</a>. Available objects:<ul><li>CONTENT_SETTINGS</li><li>SETTINGS</li></ul>",
            ),
            (
                "DjangoTemplate_with_help_default",
                DjangoTemplate(
                    help="A value", template_args_default={"name": "Undefined"}
                ),
                "A value<br><br>Simple <a href='https://docs.djangoproject.com/en/3.2/topics/templates/' target='_blank'>Django Template</a>. Available objects:<ul><li>name - 'Undefined'</li><li>CONTENT_SETTINGS</li><li>SETTINGS</li></ul>",
            ),
            (
                "DjangoModelTemplate_with_help",
                DjangoModelTemplate(help="A value"),
                "A value<br><br>Simple <a href='https://docs.djangoproject.com/en/3.2/topics/templates/' target='_blank'>Django Template</a>. Available objects:<ul><li>object - required</li><li>CONTENT_SETTINGS</li><li>SETTINGS</li></ul>",
            ),
            (
                "SimpleEval_with_help",
                SimpleEval(help="A value"),
                "A value<br><br>Python code that returns a value. Available objects:<ul><li>CONTENT_SETTINGS</li><li>SETTINGS</li></ul>",
            ),
            (
                "SimpleExec_with_help",
                SimpleExec(help="A value"),
                "A value<br><br>Python code that execute and returns generated variables. Available objects:<ul><li>CONTENT_SETTINGS</li><li>SETTINGS</li></ul>Return Dict is not specified",
            ),
            (
                "SimpleExec_with_help_return",
                SimpleExec(help="A value", call_return=["name", "value"]),
                "A value<br><br>Python code that execute and returns generated variables. Available objects:<ul><li>CONTENT_SETTINGS</li><li>SETTINGS</li></ul>Return Dict: <ul><li>name - default: None</li><li>value - default: None</li></ul>",
            ),
            (
                "SimpleStringsList_with_help",
                SimpleStringsList(help="A value"),
                "A value<br><br>List of values with the following format:<ul><li>each line is a new value</li><li>strip spaces from the beginning and from the end of the value</li><li>remove empty values</li><li>use # to comment a line</li><li>empty values are removed</li></ul>",
            ),
            (
                "TypedStringsList_with_help",
                TypedStringsList(help="A value", line_type=SimpleInt()),
                "A value<br><br>List of values with the following format:<ul><li>each line is a new value</li><li>strip spaces from the beginning and from the end of the value</li><li>remove empty values</li><li>use # to comment a line</li><li>empty values are removed</li></ul>A list of items. Each item should be: <div class='subitem'>Any number</div>",
            ),
            (
                "SplitTranslation_with_help",
                SplitTranslation(help="A value"),
                "A value<br><br>Translated Text. The first line can initialize the translation splitter. The initial language is EN. The first line can be '===== EN ====='. The format for the value inside the translation is: string",
            ),
            (
                "SplitTranslation_with_help_html",
                SplitTranslation(split_type=SimpleHTML(), help="A value"),
                "A value<br><br>Translated Text. The first line can initialize the translation splitter. The initial language is EN. The first line can be '===== EN ====='. The format for the value inside the translation is: string in HTML format",
            ),
        ]
    ),
)
def test_value(var, value, initial):
    if initial:
        initial()
    assert var.get_help() == value


@pytest.mark.skipif(not yaml_installed, reason="yaml is installed")
def test_value_yaml():
    var = SimpleYAML(help="A value")
    assert (
        var.get_help()
        == "A value<br><br>Simple <a href='https://en.wikipedia.org/wiki/YAML' target='_blank'>YAML format</a>"
    )
