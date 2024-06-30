"""
The most basic types for the content settings. SimpleString is used as the base for all other types.
"""

from __future__ import annotations

from inspect import isclass
from functools import cached_property
from pprint import pformat
from typing import Optional, Set, Tuple, Union, Any, Callable
from collections.abc import Iterable
from json import dumps

from django import forms
from django.core.serializers.json import DjangoJSONEncoder
from django.core.exceptions import ValidationError

from content_settings.settings import CACHE_SPLITER
from content_settings.types.lazy import LazyObject
from content_settings.types import PREVIEW, required, optional, pre, BaseSetting
from content_settings.types.mixins import HTMLMixin
from content_settings.permissions import none, staff
from content_settings.defaults.context import update_defaults


class SimpleString(BaseSetting):
    """
    A very basic class that returns the string value, the same as a given value.

    Attributes:

    - constant (bool): Whether the setting is constant (can not be changed).
    - cls_field (forms.CharField): The form field class to use for the setting.
    - widget (forms.Widget): The form widget to use for the cls_field.
    - widget_attrs (Optional[dict]): Optional attributes for the widget initiation.
    - fetch_permission (Callable): `permissions.none` by default. Permission required to fetch the setting in API.
    - update_permission (Callable): `permissions.staff` by default. Optional permission required to update the setting in Django Admin.
    - view_permission (Callable): `permissions.staff` by default. Optional permission required to view the setting in Django Admin.
    - view_history_permission (Callable): Optional permission required to see the hisotry of changes. `None` means the permission is taken from `view_permission`.
    - help_format (Optional[str]): Optional format string for the help text for the format (align to the type).
    - help (Optional[str]): Optional help text for the setting.
    - value_required (bool): Whether a value is required for the setting.
    - version (str): The version of the setting (using for caching).
    - tags (Optional[Iterable[str]]): Optional tags associated with the setting.
    - validators (Tuple[Callable]): Validators to apply to the setting value.
    - validators_raw (Tuple[Callable]): Validators to apply to the text value of the setting.
    - admin_preview_as (PREVIEW): The format to use for the admin preview.
    - suffixes (Tuple[str]): Suffixes that can be appended to the setting value.
    - user_defined_slug (str): it contains a slug from db If the setting is defined in DB only (should not be set in content_settings)
    - overwrite_user_defined (bool): Whether the setting can overwrite a user defined setting.
    - default (str): The default value for the setting.
    - on_change: Tuple[Callable] - list of functions to call when the setting is changed
    - on_change_commited: Tuple[Callable] - list of functions to call when the setting is changed and commited
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
    validators_raw: Tuple[Callable] = ()
    admin_preview_as: PREVIEW = PREVIEW.NONE
    suffixes: Tuple[str] = ()
    user_defined_slug: Optional[str] = None
    overwrite_user_defined: bool = False
    default: Union[str, required, optional] = ""
    json_encoder: type = DjangoJSONEncoder
    on_change: Tuple[Callable] = ()
    on_change_commited: Tuple[Callable] = ()

    def __init__(
        self, default: Optional[Union[str, required, optional]] = None, **kwargs
    ):
        """
        The init function accepts initial attributes for the content setting type.
        It can assing any attribute that is defined in the class. (The exception is help_text instead of help)

        All of the changes for type instance can only be done inside of __init__ method. The other methods should not change self object.
        """
        # optional support of help_text instead of help
        assert not (
            "help" in kwargs and "help_text" in kwargs
        ), "You cannot use both help and help_text"
        if "help" not in kwargs and "help_text" in kwargs:
            kwargs["help"] = kwargs.pop("help_text")

        for k in kwargs.keys():
            assert self.can_assign(k), "Attribute {} not found".format(k)

        if default is not None:
            self.default = default
        assert self.default in (required, optional) or isinstance(
            self.default, str
        ), "Default should be str (or required or optional for special cases)"

        self.init_assign_kwargs(update_defaults(self, kwargs))

        assert isinstance(self.version, str), "Version should be str"
        assert (
            CACHE_SPLITER not in self.version
        ), f"Version should not contain CACHE_SPLITER:{CACHE_SPLITER}"
        assert (
            self.get_admin_preview_as() in PREVIEW
        ), f"admin_preview_as should be one of {PREVIEW}"

    def init_assign_kwargs(self, kwargs):
        """
        Assign the attributes from the kwargs to the instance.

        Use init__{attribute_name} method if it exists, otherwise use setattr
        """
        for k, v in kwargs.items():
            if not self.can_assign(k):
                raise ValueError("Attribute {} not found".format(k))
            if hasattr(self, "init__{}".format(k)):
                getattr(self, "init__{}".format(k))(v)
            else:
                setattr(self, k, v)

    def init__tags(self, tags: Union[None, str, Iterable[str]]) -> None:
        """
        Assign the tags to the instance from kwargs.
        """
        if not tags:
            return

        if isinstance(tags, str):
            tags = {tags}
        else:
            tags = set(tags)

        self.tags = tags if self.tags is None else self.tags | tags

    def can_view(self, user):
        """
        Return True if the user has permission to view the setting in the django admin panel.

        Use view_permission attribute
        """
        return self.view_permission(user)

    def can_view_history(self, user):
        """
        Return True if the user has permission to view the setting changing history in the django admin panel.

        Use view_history_permission attribute, but if it is None, use can_view
        """
        return (
            self.can_view(user)
            if self.view_history_permission is None
            else self.view_history_permission(user)
        )

    def can_update(self, user):
        """
        Return True if the user has permission to update the setting in the django admin panel.

        Use update_permission attribute
        """
        return self.update_permission(user)

    def can_fetch(self, user):
        """
        Return True if the user has permission to fetch the setting value using API.

        Use fetch_permission attribute
        """
        return self.fetch_permission(user)

    def get_admin_preview_as(self) -> str:
        """
        Return the format (PREVIEW Enum) to use for the admin preview.

        Use admin_preview_as attribute
        """
        return self.admin_preview_as

    def get_on_change(self) -> Tuple[Callable]:
        """
        Return the list of functions to call when the setting is changed.

        Use on_change attribute
        """
        return self.on_change

    def get_on_change_commited(self) -> Tuple[Callable]:
        """
        Return the list of functions to call when the setting is changed and commited.
        Uses for syncing data or triggering emails.

        Use on_change_commited attribute
        """
        return self.on_change_commited

    @cached_property
    def field(self) -> forms.Field:
        """
        the form field
        """
        return self.get_field()

    def get_suffixes(self) -> Tuple:
        """
        Return the list of suffixes that can be used
        """
        return self.suffixes

    def can_suffix(self, suffix: Optional[str]) -> bool:
        """
        Return True if the suffix is valid for the setting.
        """
        return suffix is None or suffix in self.get_suffixes()

    def can_assign(self, name: str) -> bool:
        """
        Return True if the attribute can be assigned to the instance.
        """
        return hasattr(self, name)

    def get_help_format(self) -> Iterable[str]:
        """
        Generate help for the specific type.

        The help of the format goes after the help for the specific setting and expalins the format of the setting.
        """
        yield self.help_format

    def get_help(self) -> str:
        """
        Generate help for the specific setting (includes format help)
        """
        help = self.help
        help_format = "".join(self.get_help_format())

        if help and help_format:
            return f"{help}<br><br>{help_format}"

        return help or help_format

    def get_tags(self) -> Set[str]:
        """
        Return the tags associated with the setting.
        """
        tags = self.tags
        if tags is None:
            tags = set()
        return set(tags)

    def get_content_tags(self, name: str, value: str) -> Set[str]:
        """
        Generate tags based on current type and value.

        Uses CONTENT_SETTINGS_TAGS for generating, but overriding the method allows you to change the behavior for the specific type.
        """
        from content_settings.conf import gen_tags

        return gen_tags(name, self, value)

    def get_validators(self) -> Tuple[Callable[[Any], None]]:
        """
        Return the list of validators to apply to the setting python value.
        """
        return tuple(self.validators) + tuple(self.cls_field.default_validators)

    def get_validators_raw(self) -> Tuple[Callable]:
        """
        Return the list of validators to apply to the setting text value.
        """
        return tuple(self.validators_raw)

    def get_field(self) -> forms.Field:
        """
        Generate the form field for the setting. Which will be used in the django admin panel.
        """
        return self.cls_field(
            widget=self.get_widget(),
            validators=(self.validate_value,),
            required=self.value_required,
        )

    def get_widget(self) -> forms.Widget:
        """
        Generate the form widget for the setting. Which will be used in the django admin panel.
        """
        if isclass(self.widget) and self.widget_attrs is not None:
            return self.widget(attrs=self.widget_attrs)
        else:
            return self.widget

    def validate_raw_value(self, value: str) -> None:
        """
        Validate the text value of the setting.
        """
        for validator in self.get_validators_raw():
            validator(value)

    def validate_value(self, value: str) -> Any:
        """
        Full validation of the setting text value.
        """
        if self.value_required and not value:
            raise ValidationError("This field is required")
        self.validate_raw_value(value)
        val = self.to_python(value)
        self.validate(val)

    def validate(self, value: Any):
        """
        Validate the setting python value.
        """
        for validator in self.get_validators():
            validator(value)

    def to_python(self, value: str) -> Any:
        """
        Converts text value to python value.
        """
        return self.field.to_python(value)

    def json_view_value(self, value: Any, **kwargs) -> Any:
        """
        Converts the setting value to JSON.
        """
        return dumps(value, cls=self.json_encoder)

    def give_python_to_admin(self, value: str, name: str, **kwargs) -> Any:
        """
        Converts the setting text value to setting admin value that will be used for rendering admin preview.

        By default it uses to_python method, but it make sense to override it for some types, for example callable types,
        where you want to show the result of the call in the preview.
        """
        return self.to_python(value)

    def get_admin_preview_html(self, value: Any, name: str, **kwargs) -> Any:
        """
        Generate the admin preview for PREVIEW.HTML format.
        """
        return value

    def get_admin_preview_text(self, value: Any, name: str, **kwargs) -> Any:
        """
        Generate the admin preview for PREVIEW.TEXT format.
        """
        return value

    def get_admin_preview_python(self, value: Any, name: str, **kwargs) -> Any:
        """
        Generate the admin preview for PREVIEW.PYTHON format.
        """
        return value

    def get_admin_preview_value(self, value: str, *args, **kwargs) -> str:
        """
        Generate the admin preview for the setting based on the admin_preview_as attribute (or get_admin_preview_as method).

        Using text value of the setting.
        """
        if self.get_admin_preview_as() == PREVIEW.NONE:
            return ""

        value = self.give_python_to_admin(value, *args, **kwargs)

        return str(self.get_admin_preview_object(value, *args, **kwargs))

    def get_full_admin_preview_value(self, value: str, *args, **kwargs) -> str:
        """
        Generate data for json response for preview
        """
        try:
            self.validate_value(value)
        except Exception as e:
            return {
                "error": str(e),
            }

        return {
            "html": self.get_admin_preview_value(value, *args, **kwargs),
        }

    def get_admin_preview_object(self, value: Any, name: str, **kwargs) -> str:
        """
        Generate the admin preview for the setting based on the admin_preview_as attribute (or get_admin_preview_as method).

        Using admin value of the setting.
        """
        if self.get_admin_preview_as() == PREVIEW.HTML:
            return str(self.get_admin_preview_html(value, name, **kwargs))

        if self.get_admin_preview_as() == PREVIEW.TEXT:
            value = str(self.get_admin_preview_text(value, name, **kwargs))
        else:
            value = pformat(self.get_admin_preview_python(value, name, **kwargs))

        return pre(value)

    def lazy_give(self, l_func: Callable, suffix=None) -> LazyObject:
        """
        Return the LazyObject that will be used for the setting value.

        This value will be returned using lazy prefix in the content_settings.
        """
        return LazyObject(l_func)

    def give(self, value: Any, suffix: Optional[str] = None):
        """
        The will be returned as the content_settings attribute using python value of the setting.

        Suffix can be used.
        """
        return value

    def give_python(self, value: str, suffix=None) -> Any:
        return self.give(self.to_python(value), suffix)


class SimpleText(SimpleString):
    """
    Multiline text setting type.
    """

    widget: forms.Widget = forms.Textarea
    widget_attrs: dict = {"rows": 10, "cols": 80}


class SimpleTextPreview(SimpleText):
    """
    Multiline text setting type with preview. By default SimpleText and SimpleString don't have preview, but for showing preview in EachMixin, we need to have preview for each type.
    """

    admin_preview_as: PREVIEW = PREVIEW.TEXT


class SimpleHTML(HTMLMixin, SimpleText):
    """
    Multiline HTML setting type.
    """

    pass


class URLString(SimpleString):
    """
    URL setting type.
    """

    cls_field: forms.Field = forms.URLField
    widget: forms.Widget = forms.URLInput
    help_format: str = "URL"
    widget_attrs: dict = {"style": "max-width: 600px; width: 100%"}


class EmailString(SimpleString):
    """
    Email setting type.
    """

    cls_field: forms.Field = forms.EmailField
    widget: forms.Widget = forms.EmailInput
    help_format: str = "Email"
    widget_attrs: dict = {"style": "max-width: 600px; width: 100%"}


class SimpleInt(SimpleString):
    """
    Integer setting type.
    """

    admin_preview_as: PREVIEW = PREVIEW.PYTHON
    cls_field: forms.Field = forms.IntegerField
    help_format: str = "Any number"


class SimpleBool(SimpleString):
    """
    Boolean setting type.
    Attributes:
    - yeses (Tuple[str]): Accepted values for True.
    - noes (Tuple[str]): Accepted values for False.
    """

    admin_preview_as: PREVIEW = PREVIEW.PYTHON
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
    """
    Decimal setting type.
    """

    admin_preview_as: PREVIEW = PREVIEW.PYTHON
    cls_field: forms.Field = forms.DecimalField
    help_format: str = "Decimal number with floating point"


class SimplePassword(SimpleString):
    """
    Password setting type. It is not possible to fetch the value using API. In the admin panel, the value is hidden.
    """

    admin_preview_as: PREVIEW = PREVIEW.NONE
    widget_attrs: dict = {"type": "password"}
    fetch_permission: Callable = staticmethod(none)
