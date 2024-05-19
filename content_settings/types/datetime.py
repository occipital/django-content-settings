"""
Types that convert a string into a datetime, date, time or timedelta object.
"""

from typing import Any, List, Tuple, Union

from datetime import datetime, time, timedelta
from django.core.exceptions import ValidationError
from django.utils import formats as django_formats
from django.forms.utils import from_current_timezone

from .basic import SimpleString, PREVIEW
from .mixins import EmptyNoneMixin

TIMEDELTA_FORMATS = {
    "s": "seconds",
    "m": "minutes",
    "h": "hours",
    "d": "days",
    "w": "weeks",
}


def timedelta_format(text: str) -> timedelta:
    """
    Convert a string into a timedelta object using format from `TIMEDELTA_FORMATS`.
    For example:
    - `1d` - one day
    - `1d 3h` - one day and three hours
    """
    text = text.strip()
    delta_kwargs = {}
    for el in text.split():
        try:
            val = int(el[:-1])
            val_key = el[-1]
            delta_kwargs[TIMEDELTA_FORMATS[val_key]] = val
        except Exception as e:
            raise ValidationError(f"wrong format for {el}: {e}")

    return timedelta(**delta_kwargs)


class ProcessInputFormats(EmptyNoneMixin, SimpleString):
    """
    Base class for converting a string into a datetime, date or time object. (Teachnically can be used for other fields with predefined formats by overriding `postprocess_input_format` method.)

    It uses the `input_formats_field` from the Meta class to get the filed with formats.

    We want to use different field for different formats as we want to be able to override specific format in using `CONTENT_SETTINGS_CONTEXT`
    """

    admin_preview_as = PREVIEW.PYTHON

    class Meta:
        input_formats_field = None

    def postprocess_input_format(self, value: Any, format: Any) -> Any:
        """
        converts a given value using a given format
        """
        raise NotImplementedError

    def get_input_formats(self):
        assert (
            self.Meta.input_formats_field
        ), "You must define input_formats_field in Meta class"

        formats = getattr(self, self.Meta.input_formats_field)
        if isinstance(formats, (list, tuple)):
            return formats
        return [formats]

    def get_help_format(self):
        yield (
            "Use any of the following formats: <ul>"
            + "".join([f"<li>{l}</li>" for l in self.get_input_formats()])
            + "</ul>"
        )

    def to_python(self, value):
        value = super().to_python(value)
        if value is None:
            return None

        for format in self.get_input_formats():
            try:
                return self.postprocess_input_format(value, format)
            except (ValueError, TypeError):
                continue
        raise ValidationError("Wrong Format")


TFormats = Union[List[str], Tuple[str, ...], str]


class DateTimeString(ProcessInputFormats):
    """
    Converts into a datetime object.

    Attributes:

    - `datetime_formats` - list (or a single string) of formats to use for conversion. As a default it uses `DATETIME_INPUT_FORMATS` from `django.conf.settings`
    """

    datetime_formats: TFormats = list(
        django_formats.get_format_lazy("DATETIME_INPUT_FORMATS")
    )

    class Meta:
        input_formats_field = "datetime_formats"

    def postprocess_input_format(self, value, format):
        return from_current_timezone(datetime.strptime(value.strip(), format))


class DateString(ProcessInputFormats):
    """
    Converts into a date object.

    Attributes:

    - `date_formats` - list (or a single string) of formats to use for conversion. As a default it uses `DATE_INPUT_FORMATS` from `django.conf.settings`
    """

    date_formats: TFormats = list(django_formats.get_format_lazy("DATE_INPUT_FORMATS"))

    class Meta:
        input_formats_field = "date_formats"

    def postprocess_input_format(self, value, format):
        return datetime.strptime(value.strip(), format).date()


class TimeString(DateTimeString):
    """
    Converts into a time object.

    Attributes:

    - `time_formats` - list (or a single string) of formats to use for conversion. As a default it uses `TIME_INPUT_FORMATS` from `django.conf.settings`
    """

    time_formats: TFormats = list(django_formats.get_format_lazy("TIME_INPUT_FORMATS"))

    class Meta:
        input_formats_field = "time_formats"

    def postprocess_input_format(self, value, format):
        value = datetime.strptime(value.strip(), format)
        return time(
            value.hour, value.minute, value.second, value.microsecond, fold=value.fold
        )


class SimpleTimedelta(SimpleString):
    """
    Converts into a timedelta object.
    """

    admin_preview_as = PREVIEW.PYTHON

    def get_help_format(self):
        yield "Time Delta Format"
        yield "<ul>"
        for name, value in TIMEDELTA_FORMATS.items():
            yield f"<li>{name} - {value}</li>"
        yield "</ul>"

        yield """
            Examples:
            <ul>
                <li>1d - in one day</li>
                <li>1d 3h - in one day and 3 hours</li>
            </ul>
        """

    def to_python(self, value):
        return timedelta_format(super().to_python(value))
