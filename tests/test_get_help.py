import pytest

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
    SplitByFirstLine,
)

from tests.books.models import Book
from tests.tools import adjust_params

pytestmark = [pytest.mark.django_db(transaction=True)]


@pytest.mark.parametrize(
    "var,value,initial",
    adjust_params(
        [
            (
                SimpleString(),
                "string",
            ),
            (
                SimpleString(help="A value"),
                "A value<br><br>string",
            ),
            (
                SimpleString(help="A value", help_format="A format"),
                "A value<br><br>A format",
            ),
            (
                SimpleString(help_format="A format"),
                "A format",
            ),
            (
                SimpleInt(help="A value"),
                "A value<br><br>Any number",
            ),
            (
                SimpleBool(help="A value"),
                "A value<br><br>boolean (True/False) value. Accepted values: 'yes', 'true', '1', 'no', 'false', '0', empty",
            ),
            (
                SimpleText(help="A value"),
                "A value<br><br>string",
            ),
            (
                SimpleHTML(help="A value"),
                "A value<br><br>HTML format",
            ),
            (
                URLString(help="A value"),
                "A value<br><br>URL",
            ),
            (
                EmailString(help="A value"),
                "A value<br><br>Email",
            ),
            (
                SimpleDecimal(help="A value"),
                "A value<br><br>Decimal number with floating point",
            ),
            (
                SimplePassword(help="A value"),
                "A value<br><br>string",
            ),
            (
                DateTimeString(help="A value"),
                r"A value<br><br>Use any of the following formats: <ul><li>%Y-%m-%d %H:%M:%S</li><li>%Y-%m-%d %H:%M:%S.%f</li><li>%Y-%m-%d %H:%M</li><li>%m/%d/%Y %H:%M:%S</li><li>%m/%d/%Y %H:%M:%S.%f</li><li>%m/%d/%Y %H:%M</li><li>%m/%d/%y %H:%M:%S</li><li>%m/%d/%y %H:%M:%S.%f</li><li>%m/%d/%y %H:%M</li><li>%Y-%m-%d</li></ul>",
            ),
            (
                DateString(help="A value"),
                r"A value<br><br>Use any of the following formats: <ul><li>%Y-%m-%d</li><li>%m/%d/%Y</li><li>%m/%d/%y</li><li>%b %d %Y</li><li>%b %d, %Y</li><li>%d %b %Y</li><li>%d %b, %Y</li><li>%B %d %Y</li><li>%B %d, %Y</li><li>%d %B %Y</li><li>%d %B, %Y</li></ul>",
            ),
            (
                TimeString(help="A value"),
                "A value<br><br>Use any of the following formats: <ul><li>%H:%M:%S</li><li>%H:%M:%S.%f</li><li>%H:%M</li></ul>",
            ),
            (
                SimpleTimedelta(help="A value"),
                "A value<br><br>Time Delta Format<ul><li>s - seconds</li><li>m - minutes</li><li>h - hours</li><li>d - days</li><li>w - weeks</li></ul>\n            Examples:\n            <ul>\n                <li>1d - in one day</li>\n                <li>1d 3h - in one day and 3 hours</li>\n            </ul>\n        ",
            ),
            (
                SimpleYAML(help="A value"),
                "A value<br><br>Simple <a href='https://en.wikipedia.org/wiki/YAML' target='_blank'>YAML format</a>",
            ),
            (
                SimpleJSON(help="A value"),
                "A value<br><br>Simple <a href='https://en.wikipedia.org/wiki/JSON' target='_blank'>JSON format</a>",
            ),
            (
                SimpleCSV(help="A value", csv_fields=["id", "name"]),
                "A value<br><br>Simple <a href='https://en.wikipedia.org/wiki/Comma-separated_values' target='_blank'>CSV format</a><br>Fields:<br><i>id</i> - (optional) string<br><i>name</i> - (optional) string",
            ),
            (
                SimpleCSV(
                    help="A value",
                    csv_fields={
                        "name": SimpleString(required),
                        "value": SimpleString(default="default value"),
                        "description": SimpleString(optional),
                    },
                ),
                "A value<br><br>Simple <a href='https://en.wikipedia.org/wiki/Comma-separated_values' target='_blank'>CSV format</a><br>Fields:<br><i>name</i> - (required) string<br><i>value</i> - (default: default value) string<br><i>description</i> - (optional) string",
            ),
            (
                SimpleCSV(
                    help="A value",
                    csv_fields={
                        "name": SimpleString(),
                        "price": SimpleDecimal("0"),
                    },
                ),
                "A value<br><br>Simple <a href='https://en.wikipedia.org/wiki/Comma-separated_values' target='_blank'>CSV format</a><br>Fields:<br><i>name</i> - (default: <i>empty</i>) string<br><i>price</i> - (default: 0) Decimal number with floating point",
            ),
            (
                DjangoTemplate(help="A value"),
                "A value<br><br>Simple <a href='https://docs.djangoproject.com/en/3.2/topics/templates/' target='_blank'>Django Template</a>. Available objects:<ul><li>CONTENT_SETTINGS</li><li>SETTINGS</li></ul>",
            ),
            (
                DjangoTemplate(
                    help="A value", template_args_default={"name": "Undefined"}
                ),
                "A value<br><br>Simple <a href='https://docs.djangoproject.com/en/3.2/topics/templates/' target='_blank'>Django Template</a>. Available objects:<ul><li>name - 'Undefined'</li><li>CONTENT_SETTINGS</li><li>SETTINGS</li></ul>",
            ),
            (
                DjangoModelTemplate(help="A value"),
                "A value<br><br>Simple <a href='https://docs.djangoproject.com/en/3.2/topics/templates/' target='_blank'>Django Template</a>. Available objects:<ul><li>object - required</li><li>CONTENT_SETTINGS</li><li>SETTINGS</li></ul>",
            ),
            (
                SimpleEval(help="A value"),
                "A value<br><br>Python code that returns a value. Available objects:<ul><li>CONTENT_SETTINGS</li><li>SETTINGS</li></ul>",
            ),
            (
                SimpleExec(help="A value"),
                "A value<br><br>Python code that execute and returns generated variables. Available objects:<ul><li>CONTENT_SETTINGS</li><li>SETTINGS</li></ul>Return Dict is not specified",
            ),
            (
                SimpleExec(help="A value", call_return=["name", "value"]),
                "A value<br><br>Python code that execute and returns generated variables. Available objects:<ul><li>CONTENT_SETTINGS</li><li>SETTINGS</li></ul>Return Dict: <ul><li>name - default: None</li><li>value - default: None</li></ul>",
            ),
            (
                SimpleStringsList(help="A value"),
                "A value<br><br>List of values with the following format:<ul><li>each line is a new value</li><li>strip spaces from the beginning and from the end of the value</li><li>remove empty values</li><li> use # to comment a line</li><li>empty values are removed</li></ul>",
            ),
            (
                TypedStringsList(help="A value", line_type=SimpleInt()),
                "A value<br><br>List of values with the following format:<ul><li>each line is a new value</li><li>strip spaces from the beginning and from the end of the value</li><li>remove empty values</li><li> use # to comment a line</li><li>empty values are removed</li></ul>Each line is Any number",
            ),
        ]
    ),
)
def test_value(var, value, initial):
    if initial:
        initial()
    assert var.get_help() == value
