from inspect import isclass
from functools import cached_property
from pprint import pformat
from typing import Optional, Set, Tuple, Union, Any, Callable
from collections.abc import Iterable

from django import forms

from content_settings.context_managers import context_defaults_kwargs
from content_settings.settings import CACHE_SPLITER
from content_settings.types.lazy import LazyObject
from content_settings.types import (
    PREVIEW_ALL,
    PREVIEW_HTML,
    PREVIEW_TEXT,
    PREVIEW_PYTHON,
    PREVIEW_NONE,
)


class BaseSetting:
    pass


class SimpleString(BaseSetting):
    """
     Attributes:
    - constant (bool): Whether the setting is constant (can not be changed).
    - cls_field (forms.CharField): The form field class to use for the setting.
    - widget (forms.Widget): The form widget to use for the cls_field.
    - widget_attrs (Optional[dict]): Optional attributes for the widget initiation.
    - fetch_permission (Optional[str]): Optional permission required to fetch the setting.
    - update_permission (Optional[str]): Optional permission required to update the setting.
    - help_format (Optional[str]): Optional format string for the help text for the format (align to the type).
    - help (Optional[str]): Optional help text for the setting.
    - value_required (bool): Whether a value is required for the setting.
    - version (str): The version of the setting (using for caching).
    - tags (Optional[Iterable[str]]): Optional tags associated with the setting.
    - validators (Tuple[Callable]): Validators to apply to the setting value.
    - empty_is_none (bool): Whether an empty value should be treated as None.
    - admin_preview_as (str): The format to use for the admin preview.
    - suffixes (Tuple[str]): Suffixes that can be appended to the setting value.
    - user_defined_slug (str): it contains a slug from db If the setting is defined in DB only (should not be set in content_settings)
    - overwrite_user_defined (bool): Whether the setting can overwrite a user defined setting.
    - default (str): The default value for the setting.
    """

    constant: bool = False
    cls_field: forms.CharField = forms.CharField
    widget: forms.Widget = forms.TextInput
    widget_attrs: Optional[dict] = None
    fetch_permission: Optional[str] = None
    update_permission: Optional[str] = None
    help_format: Optional[str] = None
    help: Optional[str] = None
    value_required: bool = False
    version: str = ""
    tags: Optional[Iterable[str]] = None
    validators: Tuple[Callable] = ()
    empty_is_none: bool = False
    admin_preview_as: str = PREVIEW_NONE
    suffixes: Tuple[str] = ()
    user_defined_slug: Optional[str] = None
    overwrite_user_defined: bool = False
    default: str = ""

    def __init__(self, default: Optional[str] = None, **kwargs):
        for k in kwargs.keys():
            assert self.can_assign(k), "Attribute {} not found".format(k)

        if default is not None:
            self.default = default
        assert isinstance(self.default, str), "Default should be str"

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

    def init__tags(self, tags: Union[None, str, Iterable[str]]) -> None:
        if not tags:
            return

        if isinstance(tags, str):
            tags = {tags}
        else:
            tags = set(tags)

        self.tags = tags if self.tags is None else self.tags | tags

    @cached_property
    def field(self) -> forms.Field:
        return self.get_field()

    def get_suffixes(self) -> Tuple:
        return self.suffixes

    def can_suffix(self, suffix: Optional[str]) -> bool:
        return suffix is None or suffix in self.get_suffixes()

    def can_assign(self, name: str) -> bool:
        return hasattr(self, name)

    def update_defaults_context(self, kwargs: dict) -> dict:
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

    def get_help_format(self) -> Optional[Union[str, Iterable[str]]]:
        return self.help_format

    def get_help(self) -> Optional[str]:
        help_format = self.get_help_format()
        if help_format is not None and not isinstance(help_format, str):
            help_format = "".join(help_format)
        if help_format:
            return f"{self.help} <br><br> {help_format}"
        return self.help

    def get_tags(self) -> Set[str]:
        tags = self.tags
        if tags is None:
            tags = set()
        return set(tags)

    def get_validators(self) -> Tuple[Callable]:
        return self.validators + tuple(self.cls_field.default_validators)

    def get_field(self) -> forms.Field:
        return self.cls_field(
            widget=self.get_widget(),
            validators=(self.validate_value,),
            required=self.value_required,
        )

    def get_widget(self) -> forms.Widget:
        if isclass(self.widget) and self.widget_attrs is not None:
            return self.widget(attrs=self.widget_attrs)
        else:
            return self.widget

    def validate_value(self, value: str) -> Any:
        val = self.to_python(value)
        for validator in self.get_validators():
            validator(val)
        return val

    def to_python(self, value: str) -> Any:
        if self.empty_is_none and value.strip() == "":
            return None
        return self.field.to_python(value)

    def json_view_value(self, request, value: Any) -> Any:
        return value

    def give_python_to_admin(self, value: str, name: str) -> Any:
        return self.to_python(value)

    def get_admin_preview_html(self, value: str, name: str) -> Any:
        return self.give_python_to_admin(value, name)

    def get_admin_preview_text(self, value: str, name: str) -> Any:
        return self.give_python_to_admin(value, name)

    def get_admin_preview_python(self, value: str, name: str) -> Any:
        return self.give_python_to_admin(value, name)

    def get_admin_preview_value(self, value: str, name: str) -> str:
        if self.admin_preview_as == PREVIEW_NONE:
            return ""

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

    def lazy_give(self, l_func: Callable, suffix=None) -> LazyObject:
        return LazyObject(l_func)

    def give(self, value, suffix: Optional[str] = None):
        return value

    def give_python(self, value: str, suffix=None) -> Any:
        return self.give(self.to_python(value), suffix)


class SimpleText(SimpleString):
    widget: forms.Widget = forms.Textarea
    widget_attrs: dict = {"rows": 10, "cols": 80}


class SimpleHTML(SimpleText):
    admin_preview_as: str = PREVIEW_HTML


class URLString(SimpleString):
    cls_field: forms.Field = forms.URLField
    widget: forms.Widget = forms.URLInput
    widget_attrs: dict = {"style": "max-width: 600px; width: 100%"}


class EmailString(SimpleString):
    cls_field: forms.Field = forms.EmailField
    widget: forms.Widget = forms.EmailInput
    widget_attrs: dict = {"style": "max-width: 600px; width: 100%"}


class SimpleInt(SimpleString):
    admin_preview_as: str = PREVIEW_PYTHON
    cls_field: forms.Field = forms.IntegerField

    def get_help_format(self):
        yield "Any number"


class SimpleBool(SimpleInt):
    admin_preview_as: str = PREVIEW_PYTHON
    min_value: int = 0
    max_value: int = 1
    empty_is_none: bool = True

    def to_python(self, value) -> bool:
        return bool(super().to_python(value))


class SimpleDecimal(SimpleString):
    admin_preview_as: str = PREVIEW_PYTHON
    cls_field: forms.Field = forms.DecimalField
