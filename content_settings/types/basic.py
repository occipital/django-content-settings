from inspect import isclass
from functools import cached_property
from pprint import pformat

from django import forms

from content_settings.context_managers import context_defaults_kwargs
from content_settings.settings import CACHE_SPLITER
from content_settings.types import (
    PREVIEW_ALL,
    PREVIEW_HTML,
    PREVIEW_TEXT,
    PREVIEW_PYTHON,
)


class BaseSetting:
    pass


class SimpleString(BaseSetting):
    cls_field = forms.CharField
    widget = forms.TextInput
    widget_attrs = None
    fetch_permission = None
    update_permission = None
    help_format = None
    help = None
    value_required = False
    version = ""
    tags = None
    fetch_groups = None
    validators = ()
    empty_is_none = False
    admin_preview_as = PREVIEW_TEXT

    def __init__(self, default="", **kwargs):
        for k in kwargs.keys():
            assert self.can_assign(k), "Attribute {} not found".format(k)
        assert isinstance(default, str), "Default should be str"

        self.default = default
        kwargs = self.update_defaults_context(kwargs)
        self.init_assign_kwargs(kwargs)

        assert isinstance(self.version, str), "Version should be str"
        assert (
            CACHE_SPLITER not in self.version
        ), f"Version should not contain CACHE_SPLITER:{CACHE_SPLITER}"
        assert (
            self.admin_preview_as in PREVIEW_ALL
        ), f"admin_preview_as should be in {PREVIEW_ALL}"

    def init_assign_kwargs(self, kwargs):
        for k, v in kwargs.items():
            if not self.can_assign(k):
                raise ValueError("Attribute {} not found".format(k))
            if hasattr(self, "init__{}".format(k)):
                getattr(self, "init__{}".format(k))(v)
            else:
                setattr(self, k, v)

    def init__tags(self, tags):
        if not tags:
            return self.tags

        if isinstance(tags, str):
            tags = {tags}
        else:
            tags = set(tags)

        self.tags = tags if self.tags is None else self.tags | tags

    @cached_property
    def field(self):
        return self.get_field()

    def can_assign(self, name):
        return hasattr(self, name)

    def update_defaults_context(self, kwargs):
        # initiate default values
        context_defaults = {
            name: value
            for name, value in context_defaults_kwargs().items()
            if self.can_assign(name)
        }

        # update actual values
        return {
            name: value
            for name, value in context_defaults_kwargs(
                {
                    **context_defaults,
                    **kwargs,
                }
            ).items()
            if self.can_assign(name)
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

    def give_python_to_admin(self, value, name):
        return self.give_python(value)

    def get_admin_preview_html(self, value, name):
        return self.give_python_to_admin(value, name)

    def get_admin_preview_text(self, value, name):
        return self.give_python_to_admin(value, name)

    def get_admin_preview_python(self, value, name):
        return self.give_python_to_admin(value, name)

    def get_admin_preview_value(self, value, name):
        if self.admin_preview_as == PREVIEW_HTML:
            return str(self.get_admin_preview_html(value, name))

        if self.admin_preview_as == PREVIEW_TEXT:
            value = str(self.get_admin_preview_text(value, name))
        else:
            value = pformat(self.get_admin_preview_python(value, name))

        return "<pre>{}</pre>".format(
            value.replace("<", "&lt;")
            .replace(">", "&gt;")
            .replace("&", "&amp;")
            .replace('"', "&quot;")
        )

    def give(self, value):
        return value

    def give_python(self, value):
        return self.give(self.to_python(value))


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
    admin_preview_as = PREVIEW_PYTHON

    def to_python(self, value):
        return bool(super().to_python(value))


class SimpleDecimal(SimpleString):
    cls_field = forms.DecimalField
