Types that convert a string into a datetime, date, time or timedelta object.

# def timedelta_format(text: str) [source](https://github.com/occipital/django-content-settings/blob/master/content_settings/types/datetime.py#L24)

Convert a string into a timedelta object using format from `TIMEDELTA_FORMATS`.
For example:
- `1d` - one day
- `1d 3h` - one day and three hours

# class ProcessInputFormats(EmptyNoneMixin, SimpleString) [source](https://github.com/occipital/django-content-settings/blob/master/content_settings/types/datetime.py#L44)

Base class for converting a string into a datetime, date or time object. (Teachnically can be used for other fields with predefined formats by overriding `postprocess_input_format` method.)

It uses the `input_formats_field` from the Meta class to get the filed with formats.

We want to use different field for different formats as we want to be able to override specific format in using `CONTENT_SETTINGS_CONTEXT`

## def postprocess_input_format(self, value: Any, format: Any) [source](https://github.com/occipital/django-content-settings/blob/master/content_settings/types/datetime.py#L58)

converts a given value using a given format

# class DateTimeString(ProcessInputFormats) [source](https://github.com/occipital/django-content-settings/blob/master/content_settings/types/datetime.py#L97)

Converts into a datetime object.

Attributes:

- `datetime_formats` - list (or a single string) of formats to use for conversion. As a default it uses `DATETIME_INPUT_FORMATS` from `django.conf.settings`

# class DateString(ProcessInputFormats) [source](https://github.com/occipital/django-content-settings/blob/master/content_settings/types/datetime.py#L117)

Converts into a date object.

Attributes:

- `date_formats` - list (or a single string) of formats to use for conversion. As a default it uses `DATE_INPUT_FORMATS` from `django.conf.settings`

# class TimeString(DateTimeString) [source](https://github.com/occipital/django-content-settings/blob/master/content_settings/types/datetime.py#L135)

Converts into a time object.

Attributes:

- `time_formats` - list (or a single string) of formats to use for conversion. As a default it uses `TIME_INPUT_FORMATS` from `django.conf.settings`

# class SimpleTimedelta(SimpleString) [source](https://github.com/occipital/django-content-settings/blob/master/content_settings/types/datetime.py#L156)

Converts into a timedelta object.