import pytest
from decimal import Decimal

from django.core.exceptions import ValidationError

from content_settings.types.template import (
    DjangoTemplateNoArgs,
    DjangoModelTemplate,
    DjangoTemplate,
    SimpleEval,
    SimpleEvalNoArgs,
    DjangoModelEval,
)
from content_settings.types.basic import SimpleString, SimpleInt, EmailString
from content_settings.types.array import SimpleStringsList
from content_settings.types.validators import call_validator
from content_settings.types.template import required
from content_settings.types.mixins import MakeCallMixin, mix
from content_settings.context_managers import context_defaults
from content_settings.types import PREVIEW_HTML, PREVIEW_TEXT, PREVIEW_PYTHON

from tests.books.models import Book
from tests.tools import adjust_params

pytestmark = [pytest.mark.django_db(transaction=True)]


def init_books():
    Book.objects.create(title="The Poplar", description="A book about poplar trees")


with context_defaults(admin_preview_as=PREVIEW_HTML):

    @pytest.mark.parametrize(
        "var,value,initial",
        adjust_params(
            [
                (
                    DjangoTemplateNoArgs(
                        "{{CONTENT_SETTINGS.TITLE}} is the best book store in the world"
                    ),
                    "Book Store is the best book store in the world",
                ),
                (
                    DjangoModelTemplate(
                        "<b>{{book.title}}</b><br><i>{{book.description}}</i>",
                        model_queryset=Book.objects.all(),
                        obj_name="book",
                    ),
                    "<b>The Poplar</b><br><i>A book about poplar trees</i>",
                    init_books,
                ),
                (
                    DjangoModelEval(
                        '{"name": object.title, "description": object.description}',
                        model_queryset=Book.objects.all(),
                    ),
                    "{'name': 'The Poplar', 'description': 'A book about poplar trees'}",
                    init_books,
                ),
                (
                    SimpleString("Book Store"),
                    "Book Store",
                ),
                (
                    SimpleInt("1"),
                    "1",
                ),
                (
                    SimpleStringsList("1,2,3", split_lines=","),
                    "['1', '2', '3']",
                ),
                (
                    DjangoTemplate(
                        "{{CONTENT_SETTINGS.TITLE}} is the best book store in the world"
                    ),
                    "Book Store is the best book store in the world",
                ),
                (
                    DjangoTemplate(
                        "{{CONTENT_SETTINGS.TITLE}} is the best book store in the world",
                        validators=(call_validator(),),
                    ),
                    "Book Store is the best book store in the world",
                ),
                (
                    DjangoTemplate(
                        "{{CONTENT_SETTINGS.TITLE}} is the {{SETTINGS.STATIC_URL}}title.png",
                        validators=(call_validator(),),
                    ),
                    "Book Store is the /static/title.png",
                ),
                (
                    DjangoTemplate(
                        "{{CONTENT_SETTINGS.TITLE}} is {{award}} book store in the world",
                        validators=(call_validator(),),
                        template_args_default={"award": "fantastic"},
                    ),
                    "Book Store is fantastic book store in the world",
                ),
                (
                    DjangoTemplate(
                        "{{CONTENT_SETTINGS.TITLE}} is {{award}} book store in the world",
                        validators=(call_validator(award="fantastic"),),
                    ),
                    "Book Store is fantastic book store in the world",
                ),
                (
                    DjangoTemplate(
                        "{{CONTENT_SETTINGS.TITLE}} is {{award}} {% if %} book store in the world",
                        validators=(call_validator(award="fantastic"),),
                    ),
                    "ERROR!!! Unexpected end of expression in if tag.",
                ),
                (
                    DjangoTemplate(
                        "{{CONTENT_SETTINGS.TITLE}} is {{award}} book store in the world",
                        validators=(
                            call_validator(),
                            call_validator("the best"),
                        ),
                        template_args_default={"award": "fantastic"},
                    ),
                    "<pre>>>> VAR()</pre>\nBook Store is fantastic book store in the world\n<pre>>>> VAR('the best')</pre>\nBook Store is the best book store in the world",
                ),
                (
                    DjangoTemplate(
                        "{{CONTENT_SETTINGS.TITLE}} is {{award}} book store in the world",
                        validators=(
                            call_validator(),
                            call_validator("the best"),
                        ),
                        template_args_default={"award": "fantastic"},
                    ),
                    "<pre>>>> VAR()</pre>\nBook Store is fantastic book store in the world\n<pre>>>> VAR('the best')</pre>\nBook Store is the best book store in the world",
                ),
                (
                    DjangoTemplate(
                        "{{CONTENT_SETTINGS.TITLE}} is {{award}} book store in the world",
                        validators=(
                            call_validator(),
                            call_validator(award="the best"),
                        ),
                        template_args_default={"award": "fantastic"},
                    ),
                    "<pre>>>> VAR()</pre>\nBook Store is fantastic book store in the world\n<pre>>>> VAR(award='the best')</pre>\nBook Store is the best book store in the world",
                ),
                (
                    mix(MakeCallMixin, SimpleString)(
                        "{{CONTENT_SETTINGS.TITLE}} is {{award}} book store in the world"
                    ),
                    "{{CONTENT_SETTINGS.TITLE}} is {{award}} book store in the world",
                ),
            ]
        ),
    )
    def test_html_preview(var, value, initial):
        if initial:
            initial()
        val = var.give_python_to_admin(var.default, "VAR")
        assert var.get_admin_preview_object(val, "VAR") == value


with context_defaults(admin_preview_as=PREVIEW_TEXT):

    @pytest.mark.parametrize(
        "var,value,initial",
        adjust_params(
            [
                (
                    DjangoTemplateNoArgs(
                        "{{CONTENT_SETTINGS.TITLE}} is the best book store in the world"
                    ),
                    "<pre>Book Store is the best book store in the world</pre>",
                ),
                (
                    DjangoTemplate(
                        "{{CONTENT_SETTINGS.TITLE}} is the best book store in the world"
                    ),
                    "<pre>Book Store is the best book store in the world</pre>",
                ),
                (
                    DjangoTemplate(
                        "{{CONTENT_SETTINGS.TITLE}} is the best book store in the world",
                        validators=(call_validator(),),
                    ),
                    "<pre>Book Store is the best book store in the world</pre>",
                ),
                (
                    DjangoTemplate(
                        "{{CONTENT_SETTINGS.TITLE}} is the {{SETTINGS.STATIC_URL}}title.png",
                        validators=(call_validator(),),
                    ),
                    "<pre>Book Store is the /static/title.png</pre>",
                ),
                (
                    DjangoTemplate(
                        "{{CONTENT_SETTINGS.TITLE}} is {{award}} book store in the world",
                        template_args_default={"award": "fantastic"},
                    ),
                    "<pre>Book Store is fantastic book store in the world</pre>",
                ),
                (
                    DjangoTemplate(
                        "{{CONTENT_SETTINGS.TITLE}} is {{award}} book store in the world",
                        validators=(call_validator(award="fantastic"),),
                    ),
                    "<pre>Book Store is fantastic book store in the world</pre>",
                ),
                (
                    DjangoTemplate(
                        "{{CONTENT_SETTINGS.TITLE}} is {{award}} {% if %} book store in the world",
                        validators=(call_validator(award="fantastic"),),
                    ),
                    "ERROR!!! Unexpected end of expression in if tag.",
                ),
                (
                    DjangoTemplate(
                        "{{CONTENT_SETTINGS.TITLE}} is {{award}} book store in the world",
                        validators=(
                            call_validator(),
                            call_validator("the best"),
                        ),
                        template_args_default={"award": "fantastic"},
                    ),
                    "<pre>>>> VAR()</pre>\n<pre>Book Store is fantastic book store in the world</pre>\n<pre>>>> VAR('the best')</pre>\n<pre>Book Store is the best book store in the world</pre>",
                ),
                (
                    SimpleEval("1+3"),
                    "<pre>4</pre>",
                ),
                (
                    SimpleEvalNoArgs("1+3"),
                    "<pre>4</pre>",
                ),
                (
                    SimpleEval("1+3", validators=(call_validator(),)),
                    "<pre>4</pre>",
                ),
                (
                    SimpleEval(
                        "1+3",
                        validators=(call_validator(),),
                    ),
                    "<pre>4</pre>",
                ),
                (
                    SimpleEval(
                        "1+val",
                        validators=(call_validator(val=7),),
                    ),
                    "<pre>8</pre>",
                ),
                (
                    SimpleEval(
                        "1+val",
                        validators=(call_validator(4),),
                        template_args_default={"val": required},
                    ),
                    "<pre>5</pre>",
                ),
                (
                    SimpleEval(
                        "1+val",
                        validators=(call_validator(),),
                        template_args_default={"val": required},
                    ),
                    "ERROR!!! [\"['Missing required argument val']\"]",
                ),
                (
                    SimpleEval(
                        "1+val",
                        validators=(
                            call_validator(),
                            call_validator(5),
                        ),
                        template_args_default={"val": 3},
                    ),
                    "<pre>>>> VAR()</pre>\n<pre>4</pre>\n<pre>>>> VAR(5)</pre>\n<pre>6</pre>",
                ),
                (
                    SimpleEval(
                        "SETTINGS.STATIC_URL + name + '.png'",
                        validators=(
                            call_validator(),
                            call_validator("face"),
                        ),
                        template_args_default={"name": "title"},
                    ),
                    "<pre>>>> VAR()</pre>\n<pre>/static/title.png</pre>\n<pre>>>> VAR('face')</pre>\n<pre>/static/face.png</pre>",
                ),
                (
                    SimpleEval(
                        "CONTENT_SETTINGS.TITLE + ' ' + explain",
                        validators=(
                            call_validator(),
                            call_validator("epic"),
                        ),
                        template_args_default={"explain": "the best"},
                    ),
                    "<pre>>>> VAR()</pre>\n<pre>Book Store the best</pre>\n<pre>>>> VAR('epic')</pre>\n<pre>Book Store epic</pre>",
                ),
                (
                    SimpleEval(
                        "CONTENT_SETTINGS.TITLE + ' ' + explain",
                        validators=(
                            call_validator(),
                            call_validator("epic"),
                        ),
                        template_args_default={"explain": "the best"},
                        template_static_includes=(),
                    ),
                    "<pre>>>> VAR()</pre>\nERROR!!! [\"name 'CONTENT_SETTINGS' is not defined\"]\n<pre>>>> VAR('epic')</pre>\nERROR!!! [\"name 'CONTENT_SETTINGS' is not defined\"]",
                ),
                (
                    SimpleEval(
                        "Decimal('1.2')/val",
                        validators=(
                            call_validator(val=Decimal("2")),
                            call_validator(Decimal("0.5")),
                        ),
                        template_args_default={"val": Decimal("1")},
                        template_static_data={"Decimal": Decimal},
                    ),
                    "<pre>>>> VAR(val=Decimal('2'))</pre>\n<pre>0.6</pre>\n<pre>>>> VAR(Decimal('0.5'))</pre>\n<pre>2.4</pre>",
                ),
                (
                    SimpleEval(
                        "Decimal('1.2')/val + plus",
                        validators=(
                            call_validator(val=Decimal("2")),
                            call_validator(Decimal("0.5")),
                        ),
                        template_args_default={"val": Decimal("1")},
                        template_static_data=lambda: {"Decimal": Decimal, "plus": 20},
                    ),
                    "<pre>>>> VAR(val=Decimal('2'))</pre>\n<pre>20.6</pre>\n<pre>>>> VAR(Decimal('0.5'))</pre>\n<pre>22.4</pre>",
                ),
            ]
        ),
    )
    def test_text_preview(var, value, initial):
        if initial:
            initial()
        val = var.give_python_to_admin(var.default, "VAR")
        assert var.get_admin_preview_object(val, "VAR") == value


with context_defaults(admin_preview_as=PREVIEW_PYTHON):

    @pytest.mark.parametrize(
        "var,value,initial",
        adjust_params(
            [
                (
                    DjangoTemplateNoArgs(
                        "{{CONTENT_SETTINGS.TITLE}} is the best book store in the world"
                    ),
                    "<pre>>>> VAR()</pre>\n<pre>&lt;&lt;&lt; 'Book Store is the best book store in the world'</pre>",
                ),
                (
                    SimpleEval("1+3"),
                    "<pre>>>> VAR()</pre>\n<pre>&lt;&lt;&lt; 4</pre>",
                ),
                (
                    SimpleEvalNoArgs("1+3"),
                    "<pre>>>> VAR()</pre>\n<pre>&lt;&lt;&lt; 4</pre>",
                ),
                (
                    SimpleEval("1+3", validators=(call_validator(),)),
                    "<pre>>>> VAR()</pre>\n<pre>&lt;&lt;&lt; 4</pre>",
                ),
                (
                    SimpleEval(
                        "1+val",
                        validators=(call_validator(val=7),),
                    ),
                    "<pre>>>> VAR(val=7)</pre>\n<pre>&lt;&lt;&lt; 8</pre>",
                ),
                (
                    SimpleEval(
                        "1+val",
                        validators=(
                            call_validator(),
                            call_validator(5),
                        ),
                        template_args_default={"val": 3},
                    ),
                    "<pre>>>> VAR()</pre>\n<pre>&lt;&lt;&lt; 4</pre>\n<pre>>>> VAR(5)</pre>\n<pre>&lt;&lt;&lt; 6</pre>",
                ),
                (
                    SimpleEval(
                        "SETTINGS.STATIC_URL + name + '.png'",
                        validators=(
                            call_validator(),
                            call_validator("face"),
                        ),
                        template_args_default={"name": "title"},
                    ),
                    "<pre>>>> VAR()</pre>\n<pre>&lt;&lt;&lt; '/static/title.png'</pre>\n<pre>>>> VAR('face')</pre>\n<pre>&lt;&lt;&lt; '/static/face.png'</pre>",
                ),
                (
                    SimpleEval(
                        "Decimal('1.2')/val",
                        validators=(
                            call_validator(val=Decimal("2")),
                            call_validator(Decimal("0.5")),
                        ),
                        template_args_default={"val": Decimal("1")},
                        template_static_data={"Decimal": Decimal},
                    ),
                    "<pre>>>> VAR(val=Decimal('2'))</pre>\n<pre>&lt;&lt;&lt; Decimal('0.6')</pre>\n<pre>>>> VAR(Decimal('0.5'))</pre>\n<pre>&lt;&lt;&lt; Decimal('2.4')</pre>",
                ),
            ]
        ),
    )
    def test_python_preview(var, value, initial):
        if initial:
            initial()
        val = var.give_python_to_admin(var.default, "VAR")
        assert var.get_admin_preview_object(val, "VAR") == value


def test_python_preview_error():
    var = SimpleEval(
        "1+val",
        validators=(call_validator(),),
        template_args_default={"val": required},
    )
    val = var.give_python_to_admin(var.default, "VAR")
    ret = var.get_admin_preview_object(val, "VAR")
    assert (
        ret == "<pre>>>> VAR()</pre>\nERROR!!! [\"['Missing required argument val']\"]"
    )


"""
TODO:
- python preview for list
- python preview for typed list
- preview for eval
  - with no preview
  - with one preview
  - with two previews
  - with error
- json
- csv
"""
