import pytest

from django.core.exceptions import ValidationError

from content_settings.types.template import (
    DjangoTemplate,
    SimpleEval,
    required,
)
from content_settings.types.validators import call_validator

from tests.books.models import Book

pytestmark = [pytest.mark.django_db]


def test_django_template():
    var = DjangoTemplate(template_args_default={"title": "Undefined"})

    template = """
    <h1>{{ title }}</h1>
    """.strip()

    assert var.to_python(template)() == "<h1>Undefined</h1>"
    assert var.to_python(template)("Book Store") == "<h1>Book Store</h1>"
    assert var.to_python(template)("Book Store", "ignoring") == "<h1>Book Store</h1>"


def test_django_template_required():
    var = DjangoTemplate(template_args_default={"title": required})

    template = """
    <h1>{{ title }}</h1>
    """.strip()

    with pytest.raises(ValidationError):
        var.to_python(template)()


def test_django_template_with_validator():
    var = DjangoTemplate(
        template_args_default={"title": "Undefined"},
        validators=(call_validator("Book Store"),),
    )

    var.validate_value("<h1>{{ title }}</h1>")

    with pytest.raises(Exception):
        var.validate_value("<h1>{{ title ti }}</h1>")


def test_django_template_admin_preview():
    var = DjangoTemplate(
        template_args_default={"title": "Undefined"},
        validators=(call_validator("Book Store"),),
    )

    assert (
        var.get_admin_preview_value("<h1>{{ title }}</h1>", "TITLE")
        == "<h1>Book Store</h1>"
    )


def test_django_template_admin_preview_text():
    var = DjangoTemplate(
        template_args_default={"title": "Undefined"},
        preview_html=False,
        validators=(call_validator("Book Store"),),
    )

    assert (
        var.get_admin_preview_value("<h1>{{ title }}</h1>", "TITLE")
        == "<pre><h1>Book Store</h1></pre>"
    )


def test_django_template_admin_preview_not_found():
    var = DjangoTemplate(
        template_args_default={"title": "Undefined"},
    )

    assert (
        var.get_admin_preview_value("<h1>{{ title }}</h1>", "TITLE")
        == "No preview validators. Add at least one call_validator"
    )


def test_eval():
    var = SimpleEval(
        template_args_default={"first": 1, "second": 2},
    )

    assert var.to_python("first*2 + second")() == 4
    assert var.to_python("first*2 + second")(2) == 6


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
