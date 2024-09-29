"""
Types that convert a string into a list of values.
"""

from typing import Optional, List, Callable, Generator, Iterable

from django.utils.translation import gettext as _

from .basic import (
    SimpleText,
    SimpleString,
    PREVIEW,
)
from .each import EachMixin, Item


def f_empty(value: str) -> Optional[str]:
    value = value.strip()
    if not value:
        return None
    return value


def f_comment(prefix: str) -> Callable[[str], Optional[str]]:
    def _(value: str) -> Optional[str]:
        if value.strip().startswith(prefix):
            return None
        return value

    return _


class SimpleStringsList(SimpleText):
    """
    Split a text into a list of strings.

    * comment_starts_with (default: #): if not None, the lines that start with this string are removed
    * filter_empty (default: True): if True, empty lines are removed
    * split_lines (default: \n): the string that separates the lines
    * filters (default: None): a list of additional filters to apply to the lines.
    """

    comment_starts_with: Optional[str] = "#"
    filter_empty: bool = True
    split_lines: str = "\n"
    filters: Optional[Iterable[Callable]] = None
    admin_preview_as: PREVIEW = PREVIEW.PYTHON

    def __init__(self, *args, **kwargs) -> None:
        from collections.abc import Iterable

        super().__init__(*args, **kwargs)
        assert isinstance(self.comment_starts_with, (str, type(None)))
        assert isinstance(self.filter_empty, bool)
        assert isinstance(self.split_lines, str)
        assert isinstance(self.filters, (Iterable, type(None)))

    def get_filters(self):
        """
        Get the filters based on the current configuration.

        * If filters is not None, it is returned.
        * If filter_empty is True, f_empty is added to the filters.
        * If comment_starts_with is not None, f_comment is added to the filters.
        """
        if self.filters is not None:
            filters = [*self.filters]
        else:
            filters = []

        if self.filter_empty:
            filters.append(f_empty)

        if self.comment_starts_with:
            filters.append(f_comment(self.comment_starts_with))

        return filters

    def get_help_format(self) -> Generator[str, None, None]:
        yield _("List of values with the following format:")
        yield "<ul>"
        if self.split_lines == "\n":
            yield "<li>"
            yield _("each line is a new value")
            yield "</li>"
        else:
            yield "<li>"
            yield _("%(split_lines)s separates values") % {
                "split_lines": self.split_lines
            }
            yield "</li>"
        yield "<li>"
        yield _("strip spaces from the beginning and from the end of the value")
        yield "</li>"
        yield "<li>"
        yield _("remove empty values")
        yield "</li>"
        if self.comment_starts_with:
            yield "<li>"
            yield _("use %(comment_starts_with)s to comment a line") % {
                "comment_starts_with": self.comment_starts_with
            }
            yield "</li>"
        if self.filter_empty:
            yield "<li>"
            yield _("empty values are removed")
            yield "</li>"
        yield "</ul>"

    def filter_line(self, line: str) -> str:
        for f in self.get_filters():
            line = f(line)
            if line is None:
                break
        return line

    def gen_to_python(self, value: str) -> Generator[str, None, None]:
        """
        Converts a string value into a generator of filtered lines.
        """
        lines = value.split(self.split_lines)
        for line in lines:
            line = self.filter_line(line)

            if line is not None:
                yield line

    def to_python(self, value: str) -> List[str]:
        return list(self.gen_to_python(value))


class TypedStringsList(EachMixin, SimpleStringsList):
    line_type = SimpleString()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.each = Item(self.line_type)
