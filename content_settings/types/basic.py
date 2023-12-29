from inspect import isclass
from pprint import pformat

from django.core.exceptions import ValidationError

from django import forms

from content_settings.context_managers import context_defaults_kwargs
from content_settings.settings import CACHE_SPLITER


class BaseSetting:
    pass


class SimpleString(BaseSetting):
    cls_field = forms.CharField
    widget = forms.TextInput
    widget_attrs = None
    fetch_permission = None
    update_permission = None  # TODO: permission for update/reset/delete setting
    help_format = None
    help = None
    value_required = False
    version = ""
    tags = None
    fetch_groups = None
    validators = ()
    empty_is_none = False

    def __init__(self, default="", **kwargs):
        kwargs = self.update_kwargs_context(kwargs)
        for k, v in kwargs.items():
            if not self.can_assign(k):
                raise ValueError("Attribute {} not found".format(k))
            setattr(self, k, v)

        self.default = default
        self.field = self.get_field()

        if self.tags:
            self.tags = {self.tags} if isinstance(self.tags, str) else set(self.tags)

        assert isinstance(self.default, str), "Default should be str"
        assert isinstance(self.version, str), "Version should be str"
        assert (
            CACHE_SPLITER not in self.version
        ), f"Version should not contain CACHE_SPLITER:{CACHE_SPLITER}"

    def can_assign(self, name):
        return hasattr(self, name)

    def update_kwargs_context(self, kwargs):
        context_defaults = {
            name: value
            for name, value in context_defaults_kwargs().items()
            if self.can_assign(name)
        }
        return {
            **context_defaults,
            **kwargs,
        }

    def get_help_format(self):
        return self.help_format

    def get_help(self):
        help_format = self.get_help_format()
        if help_format is not None and not isinstance(help_format, str):
            help_format = "".join(help_format)
        if help_format:
            return f"{self.help} <br><br> {help_format}"
        return self.help

    def get_tags(self):
        tags = self.tags
        if tags is None:
            tags = set()
        return set(tags)

    def get_validators(self):
        return self.validators

    def get_field(self):
        return self.cls_field(
            widget=self.get_widget(),
            validators=(self.validate_value,),
            required=self.value_required,
        )

    def get_widget(self):
        if isclass(self.widget) and self.widget_attrs is not None:
            return self.widget(attrs=self.widget_attrs)
        else:
            return self.widget

    def validate_value(self, value):
        val = self.to_python(value)
        for validator in self.get_validators():
            validator(val)
        return val

    def to_python(self, value):
        if self.empty_is_none and value.strip() == "":
            return None
        return self.field.to_python(value)

    def json_view_value(self, request, value):
        return value

    def get_admin_preview_value(self, value, name):
        return "<pre>{}</pre>".format(
            pformat(
                self.to_python(value),
            )
        )


class SimpleText(SimpleString):
    widget = forms.Textarea
    widget_attrs = {"rows": 10, "cols": 80}


class URLString(SimpleString):
    cls_field = forms.URLField
    widget = forms.URLInput
    widget_attrs = {"style": "max-width: 600px; width: 100%"}


class SimpleInt(SimpleString):
    cls_field = forms.IntegerField

    def get_help_format(self):
        yield "Any number"


class SimpleBool(SimpleInt):
    min_value = 0
    max_value = 1
    empty_is_none = True

    def to_python(self, value):
        return bool(super().to_python(value))


class SimpleDecimal(SimpleString):
    cls_field = forms.DecimalField
