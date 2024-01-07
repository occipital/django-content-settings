from datetime import datetime, time, timedelta
from django.core.exceptions import ValidationError
from django.utils import formats

from .basic import SimpleString, PREVIEW_PYTHON

TIMEDELTA_FORMATS = {
    "s": "seconds",
    "m": "minutes",
    "h": "hours",
    "d": "days",
    "w": "weeks",
}


def timedelta_format(text):
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


class DateTimeString(SimpleString):
    input_formats = formats.get_format_lazy("DATETIME_INPUT_FORMATS")
    empty_is_none = True
    admin_preview_as = PREVIEW_PYTHON

    def get_input_formats(self):
        if isinstance(self.input_formats, str):
            return [self.input_formats]
        return self.input_formats

    def get_help_format(self):
        return (
            "Use any of the following formats: <ul>"
            + "".join([f"<li>{l}</li>" for l in self.get_input_formats()])
            + "</ul>"
        )

    def to_python(self, value):
        value = super().to_python(value)
        if value is None:
            return None
        value = value.strip()

        for format in self.get_input_formats():
            try:
                return self.postprocess_datetime(self.strptime(value, format))
            except (ValueError, TypeError):
                continue
        raise ValidationError("Wrong Format")

    def postprocess_datetime(self, value):
        from django.forms.utils import from_current_timezone

        return from_current_timezone(value)

    def strptime(self, value, format):
        return datetime.strptime(value, format)


class DateString(DateTimeString):
    input_formats = formats.get_format_lazy("DATE_INPUT_FORMATS")

    def postprocess_datetime(self, value):
        return value.date()


class TimeString(DateTimeString):
    input_formats = formats.get_format_lazy("TIME_INPUT_FORMATS")

    def postprocess_datetime(self, value):
        return time(
            value.hour, value.minute, value.second, value.microsecond, fold=value.fold
        )


class SimpleTimedelta(SimpleString):
    admin_preview_as = PREVIEW_PYTHON

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
