from django.core.exceptions import ValidationError

from .basic import SimpleText, BaseSetting, PREVIEW_PYTHON


def f_empty(value):
    value = value.strip()
    if not value:
        return None
    return value


def f_comment(prefix):
    def _(value):
        if value.strip().startswith("#"):
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


class TypedStringsList(SimpleStringsList):
    line_type = None

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        assert self.line_type is not None, "line_type should be set"
        assert isinstance(
            self.line_type, BaseSetting
        ), "line_type should be BaseSetting"

    def validate_value(self, value):
        lines = value.split(self.split_lines)
        for num, line in enumerate(lines, 1):
            line = self.filter_line(line)
            if line is None:
                continue

            try:
                self.line_type.validate_value(line)
            except ValidationError as e:
                raise ValidationError(f"Line {num}: {e.message}")

        return super().validate_value(value)

    def gen_to_python(self, value):
        for line in super().gen_to_python(value):
            yield self.line_type.to_python(line)

    def get_help_format(self):
        yield from super().get_help_format()
        yield "Each line is "
        yield from self.line_type.get_help_format()

    def give(self, value):
        return [self.line_type.give(v) for v in value]
