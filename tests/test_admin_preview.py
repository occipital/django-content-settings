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

from tests.books.models import Book

pytestmark = [pytest.mark.django_db(transaction=True)]


def init_books():
    Book.objects.create(title="The Poplar", description="A book about poplar trees")


def adjust_params(params):
    def _():
        for v in params:
            if len(v) == 3:
                yield v
            else:
                yield v + (None,)

    return list(_())


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
                1,
            ),
            (
                SimpleStringsList("1,2,3", split_lines=","),
                ["1", "2", "3"],
            ),
            (
                DjangoTemplate(
                    "{{CONTENT_SETTINGS.TITLE}} is the best book store in the world"
                ),
                "No preview (add at least one validator to preview_validators)",
            ),
            (
                DjangoTemplate(
                    "{{CONTENT_SETTINGS.TITLE}} is the best book store in the world",
                    preview_validators=(call_validator(),),
                ),
                "<div>VAR()</div><div>Book Store is the best book store in the world</div>",
            ),
            (
                DjangoTemplate(
                    "{{CONTENT_SETTINGS.TITLE}} is the best book store in the world",
                    preview_validators=(call_validator(),),
                    admin_preview_call=False,
                ),
                "Book Store is the best book store in the world",
            ),
            (
                DjangoTemplate(
                    "{{CONTENT_SETTINGS.TITLE}} is the {{SETTINGS.STATIC_URL}}title.png",
                    preview_validators=(call_validator(),),
                    admin_preview_call=False,
                ),
                "Book Store is the /static/title.png",
            ),
            (
                DjangoTemplate(
                    "{{CONTENT_SETTINGS.TITLE}} is {{award}} book store in the world",
                    preview_validators=(call_validator(),),
                    template_args_default={"award": "fantastic"},
                    admin_preview_call=False,
                ),
                "Book Store is fantastic book store in the world",
            ),
            (
                DjangoTemplate(
                    "{{CONTENT_SETTINGS.TITLE}} is {{award}} book store in the world",
                    preview_validators=(call_validator(award="fantastic"),),
                    admin_preview_call=False,
                ),
                "Book Store is fantastic book store in the world",
            ),
            (
                DjangoTemplate(
                    "{{CONTENT_SETTINGS.TITLE}} is {{award}} {% if %} book store in the world",
                    preview_validators=(call_validator(award="fantastic"),),
                    admin_preview_call=False,
                ),
                "ERROR!!! Unexpected end of expression in if tag.",
            ),
            (
                DjangoTemplate(
                    "{{CONTENT_SETTINGS.TITLE}} is {{award}} book store in the world",
                    preview_validators=(
                        call_validator(),
                        call_validator("the best"),
                    ),
                    template_args_default={"award": "fantastic"},
                    admin_preview_call=False,
                ),
                "<div>Book Store is fantastic book store in the world</div><div>Book Store is the best book store in the world</div>",
            ),
            (
                DjangoTemplate(
                    "{{CONTENT_SETTINGS.TITLE}} is {{award}} book store in the world",
                    preview_validators=(
                        call_validator(),
                        call_validator("the best"),
                    ),
                    template_args_default={"award": "fantastic"},
                ),
                "<div>VAR()</div><div>Book Store is fantastic book store in the world</div>"
                "<div>VAR('the best')</div><div>Book Store is the best book store in the world</div>",
            ),
            (
                DjangoTemplate(
                    "{{CONTENT_SETTINGS.TITLE}} is {{award}} book store in the world",
                    preview_validators=(
                        call_validator(),
                        call_validator(award="the best"),
                    ),
                    template_args_default={"award": "fantastic"},
                ),
                "<div>VAR()</div><div>Book Store is fantastic book store in the world</div>"
                "<div>VAR(award='the best')</div><div>Book Store is the best book store in the world</div>",
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
    assert var.get_admin_preview_html(var.default, "VAR") == value


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
                DjangoTemplate(
                    "{{CONTENT_SETTINGS.TITLE}} is the best book store in the world"
                ),
                "No preview (add at least one validator to preview_validators)",
            ),
            (
                DjangoTemplate(
                    "{{CONTENT_SETTINGS.TITLE}} is the best book store in the world",
                    preview_validators=(call_validator(),),
                ),
                ">>> VAR()\n<<< 'Book Store is the best book store in the world'",
            ),
            (
                DjangoTemplate(
                    "{{CONTENT_SETTINGS.TITLE}} is the best book store in the world",
                    preview_validators=(call_validator(),),
                    admin_preview_call=False,
                ),
                "Book Store is the best book store in the world",
            ),
            (
                DjangoTemplate(
                    "{{CONTENT_SETTINGS.TITLE}} is the {{SETTINGS.STATIC_URL}}title.png",
                    preview_validators=(call_validator(),),
                    admin_preview_call=False,
                ),
                "Book Store is the /static/title.png",
            ),
            (
                DjangoTemplate(
                    "{{CONTENT_SETTINGS.TITLE}} is {{award}} book store in the world",
                    preview_validators=(call_validator(),),
                    template_args_default={"award": "fantastic"},
                    admin_preview_call=False,
                ),
                "Book Store is fantastic book store in the world",
            ),
            (
                DjangoTemplate(
                    "{{CONTENT_SETTINGS.TITLE}} is {{award}} book store in the world",
                    preview_validators=(call_validator(award="fantastic"),),
                    admin_preview_call=False,
                ),
                "Book Store is fantastic book store in the world",
            ),
            (
                DjangoTemplate(
                    "{{CONTENT_SETTINGS.TITLE}} is {{award}} {% if %} book store in the world",
                    preview_validators=(call_validator(award="fantastic"),),
                    admin_preview_call=False,
                ),
                "ERROR!!! Unexpected end of expression in if tag.",
            ),
            (
                DjangoTemplate(
                    "{{CONTENT_SETTINGS.TITLE}} is {{award}} book store in the world",
                    preview_validators=(
                        call_validator(),
                        call_validator("the best"),
                    ),
                    template_args_default={"award": "fantastic"},
                    admin_preview_call=False,
                ),
                "<<< 'Book Store is fantastic book store in the world'\n<<< 'Book Store is the best book store in the world'",
            ),
            (
                DjangoTemplate(
                    "{{CONTENT_SETTINGS.TITLE}} is {{award}} book store in the world",
                    preview_validators=(
                        call_validator(),
                        call_validator("the best"),
                    ),
                    template_args_default={"award": "fantastic"},
                ),
                ">>> VAR()\n<<< 'Book Store is fantastic book store in the world'\n"
                ">>> VAR('the best')\n<<< 'Book Store is the best book store in the world'",
            ),
            (
                DjangoTemplate(
                    "{{CONTENT_SETTINGS.TITLE}} is {{award}} book store in the world",
                    preview_validators=(
                        call_validator(),
                        call_validator(award="the best"),
                    ),
                    template_args_default={"award": "fantastic"},
                ),
                ">>> VAR()\n<<< 'Book Store is fantastic book store in the world'\n"
                ">>> VAR(award='the best')\n<<< 'Book Store is the best book store in the world'",
            ),
            (
                SimpleEval("1+3"),
                "No preview (add at least one validator to preview_validators)",
            ),
            (
                SimpleEvalNoArgs("1+3"),
                "4",
            ),
            (
                SimpleEval("1+3", preview_validators=(call_validator(),)),
                ">>> VAR()\n<<< 4",
            ),
            (
                SimpleEval(
                    "1+3",
                    preview_validators=(call_validator(),),
                    admin_preview_call=False,
                ),
                "4",
            ),
            (
                SimpleEval(
                    "1+val",
                    preview_validators=(call_validator(val=7),),
                    admin_preview_call=False,
                ),
                "8",
            ),
            (
                SimpleEval(
                    "1+val",
                    preview_validators=(call_validator(4),),
                    admin_preview_call=False,
                    template_args_default={"val": required},
                ),
                "5",
            ),
            (
                SimpleEval(
                    "1+val",
                    preview_validators=(call_validator(),),
                    admin_preview_call=False,
                    template_args_default={"val": required},
                ),
                "ERROR!!! [\"['Missing required argument val']\"]",
            ),
            (
                SimpleEval(
                    "1+val",
                    preview_validators=(
                        call_validator(),
                        call_validator(5),
                    ),
                    admin_preview_call=False,
                    template_args_default={"val": 3},
                ),
                "<<< 4\n<<< 6",
            ),
            (
                SimpleEval(
                    "1+val",
                    preview_validators=(
                        call_validator(),
                        call_validator(5),
                    ),
                    template_args_default={"val": 3},
                ),
                ">>> VAR()\n<<< 4\n>>> VAR(5)\n<<< 6",
            ),
            (
                SimpleEval(
                    "SETTINGS.STATIC_URL + name + '.png'",
                    preview_validators=(
                        call_validator(),
                        call_validator("face"),
                    ),
                    template_args_default={"name": "title"},
                ),
                ">>> VAR()\n<<< '/static/title.png'\n>>> VAR('face')\n<<< '/static/face.png'",
            ),
            (
                SimpleEval(
                    "CONTENT_SETTINGS.TITLE + ' ' + explain",
                    preview_validators=(
                        call_validator(),
                        call_validator("epic"),
                    ),
                    template_args_default={"explain": "the best"},
                ),
                ">>> VAR()\n<<< 'Book Store the best'\n>>> VAR('epic')\n<<< 'Book Store epic'",
            ),
            (
                SimpleEval(
                    "CONTENT_SETTINGS.TITLE + ' ' + explain",
                    preview_validators=(
                        call_validator(),
                        call_validator("epic"),
                    ),
                    template_args_default={"explain": "the best"},
                    template_static_includes=(),
                ),
                ">>> VAR()\nERROR!!! [\"name 'CONTENT_SETTINGS' is not defined\"]\n>>> VAR('epic')\nERROR!!! [\"name 'CONTENT_SETTINGS' is not defined\"]",
            ),
            (
                SimpleEval(
                    "Decimal('1.2')/val",
                    preview_validators=(
                        call_validator(val=Decimal("2")),
                        call_validator(Decimal("0.5")),
                    ),
                    template_args_default={"val": Decimal("1")},
                    template_static_data={"Decimal": Decimal},
                ),
                ">>> VAR(val=Decimal('2'))\n<<< Decimal('0.6')\n>>> VAR(Decimal('0.5'))\n<<< Decimal('2.4')",
            ),
            (
                SimpleEval(
                    "Decimal('1.2')/val + plus",
                    preview_validators=(
                        call_validator(val=Decimal("2")),
                        call_validator(Decimal("0.5")),
                    ),
                    template_args_default={"val": Decimal("1")},
                    template_static_data=lambda: {"Decimal": Decimal, "plus": 20},
                ),
                ">>> VAR(val=Decimal('2'))\n<<< Decimal('20.6')\n>>> VAR(Decimal('0.5'))\n<<< Decimal('22.4')",
            ),
        ]
    ),
)
def test_text_preview(var, value, initial):
    if initial:
        initial()
    assert var.get_admin_preview_text(var.default, "VAR") == value


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
                SimpleEval("1+3"),
                [],
            ),
            (
                SimpleEvalNoArgs("1+3"),
                4,
            ),
            (
                SimpleEval("1+3", preview_validators=(call_validator(),)),
                [("VAR()", 4)],
            ),
            (
                SimpleEval(
                    "1+3",
                    preview_validators=(call_validator(),),
                    admin_preview_call=False,
                ),
                4,
            ),
            (
                SimpleEval(
                    "1+val",
                    preview_validators=(call_validator(val=7),),
                    admin_preview_call=False,
                ),
                8,
            ),
            (
                SimpleEval(
                    "1+val",
                    preview_validators=(
                        call_validator(),
                        call_validator(5),
                    ),
                    admin_preview_call=False,
                    template_args_default={"val": 3},
                ),
                [4, 6],
            ),
            (
                SimpleEval(
                    "1+val",
                    preview_validators=(
                        call_validator(),
                        call_validator(5),
                    ),
                    template_args_default={"val": 3},
                ),
                [("VAR()", 4), ("VAR(5)", 6)],
            ),
            (
                SimpleEval(
                    "SETTINGS.STATIC_URL + name + '.png'",
                    preview_validators=(
                        call_validator(),
                        call_validator("face"),
                    ),
                    template_args_default={"name": "title"},
                ),
                [("VAR()", "/static/title.png"), ("VAR('face')", "/static/face.png")],
            ),
            (
                SimpleEval(
                    "Decimal('1.2')/val",
                    preview_validators=(
                        call_validator(val=Decimal("2")),
                        call_validator(Decimal("0.5")),
                    ),
                    template_args_default={"val": Decimal("1")},
                    template_static_data={"Decimal": Decimal},
                ),
                [
                    ("VAR(val=Decimal('2'))", Decimal("0.6")),
                    ("VAR(Decimal('0.5'))", Decimal("2.4")),
                ],
            ),
        ]
    ),
)
def test_python_preview(var, value, initial):
    if initial:
        initial()
    assert var.get_admin_preview_python(var.default, "VAR") == value


def test_python_preview_error():
    var = SimpleEval(
        "1+val",
        preview_validators=(call_validator(),),
        admin_preview_call=False,
        template_args_default={"val": required},
    )
    ret = var.get_admin_preview_python(var.default, "VAR")
    assert isinstance(ret, ValidationError)
    assert ret.message == "['Missing required argument val']"


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
