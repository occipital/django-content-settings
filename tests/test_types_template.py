import pytest

from django.core.exceptions import ValidationError

from content_settings.types.template import (
    DjangoTemplate,
    SimpleEval,
    SimpleEvalNoArgs,
    required,
    SimpleExec,
    SimpleExecNoCall,
    SimpleExecOneKeyNoCall,
    SimpleFunc,
)
from content_settings.types.validators import call_validator
from content_settings.types import PREVIEW

from tests.books.models import Book

pytestmark = [pytest.mark.django_db]


def test_simple_func():
    var = SimpleFunc(call_func=lambda name, prepared: prepared.format(name=name))

    template = "Welcome {name}"

    assert var.give_python(template)("Alex") == "Welcome Alex"


def test_simple_func_preview():
    var = SimpleFunc(
        call_func=lambda name, prepared: prepared.format(name=name),
        validators=(call_validator("Alex"),),
    )

    assert (
        var.get_admin_preview_value("Welcome {name}", "WELCOME_FUNC")
        == "<pre>>>> WELCOME_FUNC('Alex')</pre>\n<pre>&lt;&lt;&lt; 'Welcome Alex'</pre>"
    )


def test_django_template():
    var = DjangoTemplate(template_args_default={"title": "Undefined"})

    template = """
    <h1>{{ title }}</h1>
    """.strip()

    assert var.give_python(template)() == "<h1>Undefined</h1>"
    assert var.give_python(template)("Book Store") == "<h1>Book Store</h1>"
    assert var.give_python(template)("Book Store", "ignoring") == "<h1>Book Store</h1>"


def test_django_template_required():
    var = DjangoTemplate(template_args_default={"title": required})

    template = """
    <h1>{{ title }}</h1>
    """.strip()

    with pytest.raises(ValidationError):
        var.give_python(template)()


def test_django_template_with_validator():
    var = DjangoTemplate(
        template_args_default={"title": "Undefined"},
        validators=(call_validator("Book Store"),),
    )

    var.validate_value("<h1>{{ title }}</h1>")

    with pytest.raises(Exception):
        var.validate_value("<h1>{{ title ti }}</h1>")


def test_django_template_admin_preview_html():
    var = DjangoTemplate(
        template_args_default={"title": "Undefined"},
        validators=(call_validator("Book Store"),),
        admin_preview_as=PREVIEW.HTML,
    )

    assert (
        var.get_admin_preview_value("<h1>{{ title }}</h1>", "TITLE")
        == "<h1>Book Store</h1>"
    )


def test_django_template_admin_preview_text():
    var = DjangoTemplate(
        template_args_default={"title": "Undefined"},
        validators=(call_validator("Book Store"),),
        admin_preview_as=PREVIEW.HTML,
    )

    assert (
        var.get_admin_preview_value("<h1>{{ title }}</h1>", "TITLE")
        == "<h1>Book Store</h1>"
    )


def test_django_template_admin_preview_not_found():
    var = DjangoTemplate(
        template_args_default={"title": "Undefined"},
    )

    assert (
        var.get_admin_preview_value("<h1>{{ title }}</h1>", "TITLE")
        == "<pre>&lt;h1>Undefined&lt;/h1></pre>"
    )


def test_eval():
    var = SimpleEval(
        template_args_default={"first": 1, "second": 2},
    )

    assert var.give_python("first*2 + second")() == 4
    assert var.give_python("first*2 + second")(2) == 6


def test_eval_validation_error():
    var = SimpleEval(
        template_args_default={"total": 100},
        validators=(call_validator(0), call_validator(10)),
    )

    var.validate_value("10 * total")
    with pytest.raises(ValidationError):
        var.validate_value("10/total")


def test_books_list(webtest_user):
    Book.objects.create(title="Kateryna", description="lorem ipsum")
    Book.objects.create(title="The Will", description="dolor sit amet")
    resp = webtest_user.get("/books/list/")
    assert resp.status_int == 200

    assert "<b>Kateryna</b><br><i>lorem ipsum</i>" in resp.content.decode("utf-8")
    assert "<b>The Will</b><br><i>dolor sit amet</i>" in resp.content.decode("utf-8")


def test_book_reach_preview(webtest_admin):
    Book.objects.create(title="Kateryna", description="lorem ipsum")
    Book.objects.create(title="The Will", description="dolor sit amet")

    resp = webtest_admin.post(
        "/admin/content_settings/contentsetting/preview/",
        {
            "name": "BOOK_RICH_DESCRIPTION",
            "value": "Book:",
        },
    )
    assert resp.status_int == 200
    assert resp.json == {"html": "Book:"}

    resp = webtest_admin.post(
        "/admin/content_settings/contentsetting/preview/",
        {
            "name": "BOOK_RICH_DESCRIPTION",
            "value": "Book: {{book.title}}",
        },
    )
    assert resp.status_int == 200
    assert resp.json == {"html": "Book: Kateryna"}

    resp = webtest_admin.post(
        "/admin/content_settings/contentsetting/preview/",
        {
            "name": "BOOK_RICH_DESCRIPTION",
            "value": "Book: {{book.title with}}",
        },
    )
    assert resp.status_int == 200
    assert resp.json == {
        "error": "Could not parse the remainder: ' with' from 'book.title with'"
    }


def test_eval_noarg_validate():
    var = SimpleEvalNoArgs()

    var.validate_value("SETTINGS.STATIC_URL + 'test.png'")

    with pytest.raises(ValidationError):
        var.validate_value("SETTINGS.STATIC_url + 'test.png'")


def test_eval_noargs_call():
    var = SimpleEvalNoArgs(template_args_default={"base_url": None})

    value = "(base_url or SETTINGS.STATIC_URL) + 'test.png'"
    assert var.give_python(value) == "/static/test.png"
    assert var.give_python(value, "call")("/my/") == "/my/test.png"
    assert var.give_python(value, "call")(base_url="/my/") == "/my/test.png"


def test_exec_call_return_tuple():
    from decimal import Decimal

    var = SimpleExec(
        template_args_default={"value": Decimal("0.0")},
        template_static_data={"Decimal": Decimal},
        call_return=("result", "fee"),
    )

    value = """
fee = value * Decimal("0.1")
result = value - fee
    """
    assert var.give_python(value)(Decimal("100")) == {
        "fee": Decimal("10.0"),
        "result": Decimal("90.0"),
    }


def test_exec_call_return_dict():
    from decimal import Decimal

    var = SimpleExec(
        template_args_default={"value": Decimal("0.0")},
        template_static_data={"Decimal": Decimal},
        call_return={
            "result": Decimal("0.00"),
            "fee": Decimal("0.00"),
            "tax": Decimal("0.00"),
        },
    )

    value = """
fee = value * Decimal("0.1")
result = value - fee
    """
    assert var.give_python(value)(Decimal("100")) == {
        "fee": Decimal("10.0"),
        "result": Decimal("90.0"),
        "tax": Decimal("0.00"),
    }


def test_exec_call_return_lambda_dict():
    from decimal import Decimal

    var = SimpleExec(
        template_args_default={"value": Decimal("0.0")},
        template_static_data={"Decimal": Decimal},
        call_return=lambda: {
            "result": Decimal("0.00"),
            "fee": Decimal("0.00"),
            "tax": Decimal("0.00"),
        },
    )

    value = """
fee = value * Decimal("0.1")
result = value - fee
    """
    assert var.give_python(value)(Decimal("100")) == {
        "fee": Decimal("10.0"),
        "result": Decimal("90.0"),
        "tax": Decimal("0.00"),
    }


def test_exec_call_return_none():
    from decimal import Decimal

    var = SimpleExec(
        template_args_default={"value": Decimal("0.0")},
        template_static_data={"Decimal": Decimal},
    )

    value = """
fee = value * Decimal("0.1")
result = value - fee
    """
    globs = var.give_python(value)(Decimal("100"))
    assert len(globs) > 3
    assert globs["fee"] == Decimal("10.0")
    assert globs["result"] == Decimal("90.0")


def test_exec_no_call():
    var = SimpleExecNoCall()

    value = """
name = 'Alex'
nationality = 'Ukrainian'
    """
    globs = var.give_python(value)
    assert globs["name"] == "Alex"
    assert globs["nationality"] == "Ukrainian"


def test_exec_one_key_no_call():
    var = SimpleExecOneKeyNoCall(one_key_name="result")

    value = """
result="Name"
"""

    assert var.give_python(value) == "Name"
