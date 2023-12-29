from content_settings.types.basic import (
    SimpleString,
    SimpleText,
    SimpleInt,
    SimpleBool,
    SimpleDecimal,
)
from content_settings.types.datetime import DateString
from content_settings.types.mixins import mix, PositiveValidationMixin
from content_settings.types.markup import SimpleCSV
from content_settings.types.template import DjangoModelTemplate, SimpleEval
from content_settings import permissions

from .models import Book

TITLE = SimpleString(
    "Book Store",
    fetch_permission=permissions.any,
    fetch_groups=["home", "home-detail"],
    help="The title of the book store",
)

DESCRIPTION = SimpleText(
    "The best book store in the world",
    fetch_groups="home-detail",
    fetch_permission=permissions.any,
    help="The description of the book store",
)

BOOKS_ON_HOME_PAGE = mix(PositiveValidationMixin, SimpleInt)(
    "3", help="The number of books to show on the home page"
)

OPEN_DATE = DateString(
    "2023-01-01",
    fetch_groups="home-detail",
    fetch_permission=permissions.staff,
    help="The date the book store will open",
)

IS_OPEN = SimpleBool(
    "1",
)

BOOKS = SimpleCSV(
    """
Kateryna,1.2,1
The Will,200,0
The Poplar,12,1
The Night of Taras,12,1
""",
    fields={
        "name": SimpleString(),
        "price": SimpleDecimal(),
        "is_available": SimpleBool(),
    },
    fetch_permission=permissions.any,
    update_permission=permissions.has_perm("books.can_edit_todo"),
)

BOOK_RICH_DESCRIPTION = DjangoModelTemplate(
    "<b>{{book.title}}</b><br><i>{{book.description}}</i>",
    model_queryset=Book.objects.all(),
    obj_name="book",
    help="The description of the book",
)
