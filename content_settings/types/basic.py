from inspect import isclass
from functools import cached_property
from pprint import pformat
from typing import Optional, Set, Tuple, Union, Any, Callable
from collections.abc import Iterable
from json import dumps

from django import forms
from django.core.serializers.json import DjangoJSONEncoder
from django.core.exceptions import ValidationError

from content_settings.context_managers import context_defaults_kwargs
from content_settings.settings import CACHE_SPLITER
from content_settings.types.lazy import LazyObject
from content_settings.types import (
    PREVIEW_ALL,
    PREVIEW_HTML,
    PREVIEW_TEXT,
    PREVIEW_PYTHON,
    PREVIEW_NONE,
    required,
    optional,
)
from content_settings.types.mixins import HTMLMixin
from content_settings.permissions import none, staff


class BaseSetting:
    pass


class SimpleString(BaseSetting):
    """
     Attributes:
    - constant (bool): Whether the setting is constant (can not be changed).
    - cls_field (forms.CharField): The form field class to use for the setting.
    - widget (forms.Widget): The form widget to use for the cls_field.
    - widget_attrs (Optional[dict]): Optional attributes for the widget initiation.
    - fetch_permission (Callable): Optional permission required to fetch the setting.
    - update_permission (Callable): Optional permission required to update the setting.
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
    fetch_permission: Callable = staticmethod(none)
    update_permission: Callable = staticmethod(staff)
    view_permission: Callable = staticmethod(staff)
    view_history_permission: Optional[Callable] = None
    help_format: str = "string"
    help: str = ""
    value_required: bool = False
    version: str = ""
    tags: Optional[Iterable[str]] = None
    validators: Tuple[Callable] = ()
    empty_is_none: bool = False
    admin_preview_as: str = PREVIEW_NONE
    suffixes: Tuple[str] = ()
    user_defined_slug: Optional[str] = None
    overwrite_user_defined: bool = False
    default: Union[str, required, optional] = ""
    json_encoder = DjangoJSONEncoder

    def __init__(
        self, default: Optional[Union[str, required, optional]] = None, **kwargs
    ):
        for k in kwargs.keys():
            assert self.can_assign(k), "Attribute {} not found".format(k)

        if default is not None:
            self.default = default
        assert self.default in (required, optional) or isinstance(
            self.default, str
        ), "Default should be str (or required or optional for special cases)"

        kwargs = self.update_defaults_context(kwargs)
        self.init_assign_kwargs(kwargs)

        assert isinstance(self.version, str), "Version should be str"
        assert (
            CACHE_SPLITER not in self.version
        ), f"Version should not contain CACHE_SPLITER:{CACHE_SPLITER}"
        assert (
            self.get_admin_preview_as() in PREVIEW_ALL
        ), f"admin_preview_as should be in {PREVIEW_ALL}"

    def can_view(self, user):
        return self.view_permission(user)

    def can_view_history(self, user):
        return (
            self.can_view(user)
            if self.view_history_permission is None
            else self.view_history_permission(user)
        )

    def can_update(self, user):
        return self.update_permission(user)

    def can_fetch(self, user):
        return self.fetch_permission(user)

    def get_admin_preview_as(self) -> str:
        return self.admin_preview_as

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

    def get_help_format(self) -> Iterable[str]:
        yield self.help_format

    def get_help(self) -> str:
        help = self.help
        help_format = "".join(self.get_help_format())

        if help and help_format:
            return f"{help}<br><br>{help_format}"

        return help or help_format

    def get_tags(self) -> Set[str]:
        tags = self.tags
        if tags is None:
            tags = set()
        return set(tags)

    def get_content_tags(self, value: str) -> Set[str]:
        from content_settings.conf import gen_tags

        return gen_tags(self, value)

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

    def validate_raw_value(self, value: str) -> None:
        pass

    def validate_value(self, value: str) -> Any:
        self.validate_raw_value(value)
        val = self.to_python(value)
        self.validate(val)

    def validate(self, value):
        for validator in self.get_validators():
            validator(value)

    def to_python(self, value: str) -> Any:
        if self.empty_is_none and value.strip() == "":
            return None
        return self.field.to_python(value)

    def json_view_value(self, value: Any, **kwargs) -> Any:
        return dumps(value, cls=self.json_encoder)

    def give_python_to_admin(self, value: str, name: str, **kwargs) -> Any:
        return self.to_python(value)

    def get_admin_preview_html(self, value: Any, name: str, **kwargs) -> Any:
        return value

    def get_admin_preview_text(self, value: Any, name: str, **kwargs) -> Any:
        return value

    def get_admin_preview_python(self, value: Any, name: str, **kwargs) -> Any:
        return value

    def get_admin_preview_value(self, value: str, *args, **kwargs) -> str:
        if self.get_admin_preview_as() == PREVIEW_NONE:
            return ""

        value = self.give_python_to_admin(value, *args, **kwargs)

        return str(self.get_admin_preview_object(value, *args, **kwargs))

    def get_admin_preview_object(self, value: str, name: str, **kwargs) -> str:
        if self.get_admin_preview_as() == PREVIEW_HTML:
            return str(self.get_admin_preview_html(value, name, **kwargs))

        if self.get_admin_preview_as() == PREVIEW_TEXT:
            value = str(self.get_admin_preview_text(value, name, **kwargs))
        else:
            value = pformat(self.get_admin_preview_python(value, name, **kwargs))

        return "<pre>{}</pre>".format(value.replace("<", "&lt;"))

    def lazy_give(self, l_func: Callable, suffix=None) -> LazyObject:
        return LazyObject(l_func)

    def give(self, value, suffix: Optional[str] = None):
        return value

    def give_python(self, value: str, suffix=None) -> Any:
        return self.give(self.to_python(value), suffix)


class SimpleText(SimpleString):
    widget: forms.Widget = forms.Textarea
    widget_attrs: dict = {"rows": 10, "cols": 80}


class SimpleHTML(HTMLMixin, SimpleText):
    pass


class URLString(SimpleString):
    cls_field: forms.Field = forms.URLField
    widget: forms.Widget = forms.URLInput
    help_format: str = "URL"
    widget_attrs: dict = {"style": "max-width: 600px; width: 100%"}


class EmailString(SimpleString):
    cls_field: forms.Field = forms.EmailField
    widget: forms.Widget = forms.EmailInput
    help_format: str = "Email"
    widget_attrs: dict = {"style": "max-width: 600px; width: 100%"}


class SimpleInt(SimpleString):
    admin_preview_as: str = PREVIEW_PYTHON
    cls_field: forms.Field = forms.IntegerField
    help_format: str = "Any number"


class SimpleBool(SimpleString):
    admin_preview_as: str = PREVIEW_PYTHON
    yeses: Tuple[str] = ("yes", "true", "1", "+", "ok")
    noes: Tuple[str] = ("no", "not", "false", "0", "-", "")

    def to_python(self, value) -> bool:
        value = value.lower().strip()
        if value in self.yeses:
            return True
        if value in self.noes:
            return False
        return None

    @property
    def explained_accepted_values(self):
        return [f"'{v}'" if v else "empty" for v in self.yeses + self.noes]

    def validate(self, value):
        if value is None:
            raise ValidationError(
                f"Value cannot be {', '.join(self.explained_accepted_values)} only"
            )

    def get_help_format(self):
        yield "boolean (True/False) value. "
        yield f"Accepted values: {', '.join(self.explained_accepted_values)}"


class SimpleDecimal(SimpleString):
    admin_preview_as: str = PREVIEW_PYTHON
    cls_field: forms.Field = forms.DecimalField
    help_format: str = "Decimal number with floating point"


class SimplePassword(SimpleString):
    admin_preview_as: str = PREVIEW_NONE
    widget_attrs: dict = {"type": "password"}
