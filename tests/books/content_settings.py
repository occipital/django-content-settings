from content_settings.types.basic import (
    SimpleString,
    SimpleText,
    SimpleInt,
    SimpleBool,
    SimpleDecimal,
    SimpleHTML,
    PREVIEW,
    SimplePassword,
    URLString,
)
from content_settings.types.datetime import DateString
from content_settings.types.mixins import (
    mix,
    PositiveValidationMixin,
    DictSuffixesMixin,
    DictSuffixesPreviewMixin,
)
from content_settings.types.markup import SimpleCSV
from content_settings.types.template import DjangoModelTemplate, DjangoTemplateNoArgs
from content_settings.types.array import SplitTranslation
from content_settings import permissions
from content_settings.defaults.context import defaults
from content_settings.defaults.modifiers import add_tags

from .models import Book


class PublicSimpleString(SimpleString):
    fetch_permission = staticmethod(permissions.any)
    version = "3.0.0"


with defaults(add_tags({"general"})):

    TITLE = SimpleString(
        "Book Store",
        fetch_permission=permissions.any,
        overwrite_user_defined=True,
        help="The title of the book store",
    )

    DESCRIPTION = DjangoTemplateNoArgs(
        "{{CONTENT_SETTINGS.TITLE}} is the best book store in the world",
        fetch_permission=permissions.any,
        help="The description of the book store",
    )


BOOKS_ON_HOME_PAGE = mix(PositiveValidationMixin, SimpleInt)(
    "3", help="The number of books to show on the home page"
)

OPEN_DATE = DateString(
    "2023-01-01",
    fetch_permission=permissions.staff,
    help="The date the book store will open",
)

IS_OPEN = SimpleBool(
    "1",
)


IS_CLOSED = SimpleBool(
    "0",
    fetch_permission=permissions.any,
)

BOOKS = mix(DictSuffixesMixin, SimpleCSV)(
    """
Kateryna,1.2,1
The Will,200,0
The Poplar,12,1
The Night of Taras,12,1
""",
    csv_fields={
        "name": SimpleString(),
        "price": SimpleDecimal(),
        "is_available": SimpleBool(),
    },
    suffixes={
        "available_names": lambda all: [
            v.get("name") for v in all if v.get("is_available")
        ]
    },
    fetch_permission=permissions.any,
    update_permission=permissions.has_perm("books.can_edit_todo"),
)

BOOK_RICH_DESCRIPTION = DjangoModelTemplate(
    "<b>{{book.title}}</b><br><i>{{book.description}}</i>",
    model_queryset=Book.objects.all(),
    obj_name="book",
    admin_preview_as=PREVIEW.HTML,
    help="The description of the book",
)

AUTHOR = SimpleString(
    "Alexandr Lyabah",
    constant=True,
    fetch_permission=permissions.any,
)

COMPANY_DESCRIPTION = SplitTranslation(
    "The best Company",
    fetch_permission=permissions.any,
    help="The description of the company",
)

INTERESTING_TEXT = mix(DictSuffixesPreviewMixin, SimpleText)(
    "This is a long interesting text",
    suffixes={
        "trim": lambda text, max_length=10: (
            (text[: max_length - 3] + "...") if len(text) > max_length else text
        )
    },
    admin_preview_as=PREVIEW.TEXT,
    fetch_permission=permissions.any,
    help="The interesting text",
)

SIMPLE_HTML_FIELD = SimpleHTML(
    "<h1>Simple HTML</h1>",
    help="The simple html field",
)

AWESOME_PASS = SimplePassword(
    "", help="The password of the site", view_permission=permissions.superuser
)

REFFERAL_URL = URLString(
    "https://checkio.org",
    view_history_permission=permissions.superuser,
    help="url",
)
