from typing import Any, Optional

from django.core.exceptions import ValidationError

from .basic import (
    SimpleText,
    SimpleString,
    BaseSetting,
    PREVIEW_PYTHON,
    PREVIEW_TEXT,
    PREVIEW_NONE,
    PREVIEW_HTML,
)
from .mixins import AdminPreviewSuffixesMixin
from .each import EachMixin, Item


def f_empty(value):
    value = value.strip()
    if not value:
        return None
    return value


def f_comment(prefix):
    def _(value):
        if value.strip().startswith(prefix):
            return None
        return value

    return _


class SimpleStringsList(SimpleText):
    comment_starts_with = "#"
    filter_empty = True
    split_lines = "\n"
    filters = None
    admin_preview_as = PREVIEW_PYTHON

    def get_filters(self):
        if self.filters is not None:
            return self.filters

        filters = []
        if self.filter_empty:
            filters.append(f_empty)

        if self.comment_starts_with:
            filters.append(f_comment(self.comment_starts_with))

        return filters

    def get_help_format(self):
        yield "List of values with the following format:"
        yield "<ul>"
        if self.split_lines == "\n":
            yield "<li>each line is a new value</li>"
        else:
            yield f"<li>{self.split_lines} separates values</li>"
        yield "<li>strip spaces from the beginning and from the end of the value</li>"
        yield "<li>remove empty values</li>"
        if self.comment_starts_with:
            yield f"<li> use {self.comment_starts_with} to comment a line</li>"
        if self.filter_empty:
            yield "<li>empty values are removed</li>"
        yield "</ul>"

    def filter_line(self, line):
        for f in self.get_filters():
            line = f(line)
            if line is None:
                break
        return line

    def gen_to_python(self, value):
        lines = value.split(self.split_lines)
        for line in lines:
            line = self.filter_line(line)

            if line is not None:
                yield line

    def to_python(self, value):
        return list(self.gen_to_python(value))


class TypedStringsList(EachMixin, SimpleStringsList):
    line_type = SimpleString()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.each = Item(self.line_type)


NOT_FOUND_DEFAULT = "default"
NOT_FOUND_KEY_ERROR = "key_error"
NOT_FOUND_VALUE = "value"

SPLIT_SUFFIX_USE_OWN = "own"
SPLIT_SUFFIX_USE_PARENT = "parent"
SPLIT_SUFFIX_SPLIT_OWN = "split_own"
SPLIT_SUFFIX_SPLIT_PARENT = "split_parent"


class SplitByFirstLine(AdminPreviewSuffixesMixin, SimpleText):
    split_type = SimpleText()
    split_values = None
    split_default_key = None
    split_default_chooser = None
    split_not_found = NOT_FOUND_DEFAULT
    split_not_found_value = None
    split_key_validator = None
    split_suffix = SPLIT_SUFFIX_USE_OWN
    split_suffix_value = None
    admin_preview_as = PREVIEW_HTML

    def get_split_default_key(self):
        return self.split_default_key

    def split_default_choose(self, value):
        if self.split_default_chooser is None:
            return self.get_split_default_key()
        else:
            return self.split_default_chooser(value)

    def get_split_not_found(self):
        return self.split_not_found

    def get_split_not_found_value(self):
        return self.split_not_found_value

    def get_split_key_validator(self):
        return self.split_key_validator

    def get_split_suffix(self):
        return self.split_suffix

    def get_split_suffix_value(self):
        return self.split_suffix_value

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        assert (
            self.get_split_default_key()
        ), "split_default_key should be set and it should not be empty"
        assert isinstance(
            self.get_split_default_key(), str
        ), "split_default_key should be str"

        assert self.split_default_chooser is None or callable(
            self.split_default_chooser
        ), "split_default_chooser should be callable or None"
        assert self.get_split_key_validator() is None or callable(
            self.get_split_key_validator()
        ), "split_key_validator should be callable or None"
        assert self.get_split_not_found() in (
            NOT_FOUND_DEFAULT,
            NOT_FOUND_KEY_ERROR,
            NOT_FOUND_VALUE,
        ), "split_not_found should be one of NOT_FOUND_DEFAULT, NOT_FOUND_KEY_ERROR, NOT_FOUND_VALUE"
        assert self.get_split_suffix_value() is not None or self.get_split_suffix() in (
            SPLIT_SUFFIX_USE_OWN,
            SPLIT_SUFFIX_USE_PARENT,
        ), "split_suffix should be one of SPLIT_SUFFIX_USE_OWN, SPLIT_SUFFIX_SPLIT_PARENT or split_suffix_value should be set"
        assert self.get_split_suffix_value() is None or isinstance(
            self.get_split_suffix_value(), str
        ), "split_suffix_value should be str or None"
        assert self.get_split_suffix() in (
            SPLIT_SUFFIX_USE_OWN,
            SPLIT_SUFFIX_USE_PARENT,
            SPLIT_SUFFIX_SPLIT_OWN,
            SPLIT_SUFFIX_SPLIT_PARENT,
        ), "split_suffix should be one of SPLIT_SUFFIX_USE_OWN, SPLIT_SUFFIX_USE_PARENT, SPLIT_SUFFIX_SPLIT_OWN, SPLIT_SUFFIX_SPLIT_PARENT, SPLIT_SUFFIX_SPLIT_FUNCTION"
        assert self.split_values is None or callable(
            self.split_values
        ), "split_values should be callable or None"

    def split_value(self, value):
        if self.split_values is not None:
            return self.split_values(value)
        lines = value.split("\n")
        if (
            self.get_split_default_key() not in lines[0]
            or lines[0].count(self.get_split_default_key()) > 1
        ):
            return {self.get_split_default_key(): value}

        before, after = lines[0].split(self.get_split_default_key())
        ret = {self.get_split_default_key(): []}
        cur_iter = ret[self.get_split_default_key()]
        for line in lines[1:]:
            if line.startswith(before) and line.endswith(after):
                cur_iter = ret[line[len(before) : len(line) - len(after)]] = []
                continue

            cur_iter.append(line)

        return {k: "\n".join(v) for k, v in ret.items()}

    def get_admin_preview_suffixes_default(self):
        return self.get_split_default_key()

    def get_admin_preview_suffixes(self, value: str, name: str, **kwargs):
        keys = list(value.keys())
        keys.remove(self.get_split_default_key())
        return tuple(keys)

    def to_python(self, value):
        values = self.split_value(value)
        ret = {}
        for k, v in values.items():
            try:
                ret[k] = self.split_type.to_python(v)
            except ValidationError as e:
                if k == self.get_split_default_key():
                    raise
                raise ValidationError(f"{k}: {e}")
        return ret

    def give_siffixes(self, value):
        if value is None:
            return None, None

        if self.get_split_suffix() == SPLIT_SUFFIX_USE_OWN:
            return value.upper(), None

        if self.get_split_suffix() == SPLIT_SUFFIX_USE_PARENT:
            return None, value

        if self.get_split_suffix_value() not in value:
            if self.get_split_suffix() == SPLIT_SUFFIX_SPLIT_OWN:
                return value.upper(), None
            else:
                return None, value

        suffix, parent_suffix = value.split(self.get_split_suffix_value(), 1)
        suffix = suffix.upper()
        return suffix, parent_suffix

    def give(self, value, suffix=None):
        key, parent_suffix = self.give_siffixes(suffix)
        if key is None:
            key = self.split_default_choose(value)

        try:
            ret_val = value[key]
        except KeyError:
            if self.get_split_not_found() == NOT_FOUND_KEY_ERROR:
                raise
            elif self.get_split_not_found() == NOT_FOUND_DEFAULT:
                ret_val = value[self.get_split_default_key()]
            elif self.get_split_not_found() == NOT_FOUND_VALUE:
                ret_val = self.get_split_not_found_value()

        return self.split_type.give(ret_val, parent_suffix)

    def validate_raw_value(self, value):
        values = self.split_value(value)

        for k, v in values.items():
            try:
                self.split_type.validate_value(v)
            except Exception as e:
                if k == self.get_split_default_key():
                    raise
                raise ValidationError(f"{k}: {e}")

    def validate(self, values):
        if self.get_split_key_validator() is not None:
            for k in values.keys():
                self.get_split_key_validator()(k)

    def get_help_format(self):
        yield from super().get_help_format()
        yield from self.split_type.get_help_format()


class SplitTranslation(SplitByFirstLine):
    split_default_key = "EN"
    split_not_found = NOT_FOUND_DEFAULT

    def get_help_format(self):
        yield "Translated Text. "
        yield "The first line can initialize the translation splitter. "
        yield f"The initial language is {self.split_default_key}. "
        yield f"The first line can be '===== {self.split_default_key} ====='. "
        yield "The format for the value inside the translation is: "
        yield from self.split_type.get_help_format()

    def split_default_choose(self, value):
        from django.utils.translation import get_language

        return get_language().upper().replace("-", "_")

    def get_admin_preview_under_menu_object(self, value, *args, **kwargs):
        suffix = kwargs.pop("suffix", None)
        return self.split_type.get_admin_preview_object(
            self.give(value, suffix), *args, **kwargs
        )
