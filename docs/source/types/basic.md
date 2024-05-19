The most basic types for the content settings. SimpleString is used as the base for all other types.

# class SimpleString(BaseSetting) [source](https://github.com/occipital/django-content-settings/blob/master/content_settings/types/basic.py#L24)

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

## def __init__(self, default: Optional[Union[str, required, optional]] = None) [source](https://github.com/occipital/django-content-settings/blob/master/content_settings/types/basic.py#L78)

The init function accepts initial attributes for the content setting type.
It can assing any attribute that is defined in the class. (The exception is help_text instead of help)

All of the changes for type instance can only be done inside of __init__ method. The other methods should not change self object.

## def update_defaults_context(self, kwargs: dict) [source](https://github.com/occipital/django-content-settings/blob/master/content_settings/types/basic.py#L111)

Updates kwargs from the context_defaults_kwargs with the values that can be assigned to the instance.

## def init_assign_kwargs(self, kwargs) [source](https://github.com/occipital/django-content-settings/blob/master/content_settings/types/basic.py#L133)

Assign the attributes from the kwargs to the instance.

Use init__{attribute_name} method if it exists, otherwise use setattr

## def init__tags(self, tags: Union[None, str, Iterable[str]]) [source](https://github.com/occipital/django-content-settings/blob/master/content_settings/types/basic.py#L147)

Assign the tags to the instance from kwargs.

## def can_view(self, user) [source](https://github.com/occipital/django-content-settings/blob/master/content_settings/types/basic.py#L161)

Return True if the user has permission to view the setting in the django admin panel.

Use view_permission attribute

## def can_view_history(self, user) [source](https://github.com/occipital/django-content-settings/blob/master/content_settings/types/basic.py#L169)

Return True if the user has permission to view the setting changing history in the django admin panel.

Use view_history_permission attribute, but if it is None, use can_view

## def can_update(self, user) [source](https://github.com/occipital/django-content-settings/blob/master/content_settings/types/basic.py#L181)

Return True if the user has permission to update the setting in the django admin panel.

Use update_permission attribute

## def can_fetch(self, user) [source](https://github.com/occipital/django-content-settings/blob/master/content_settings/types/basic.py#L189)

Return True if the user has permission to fetch the setting value using API.

Use fetch_permission attribute

## def get_admin_preview_as(self) [source](https://github.com/occipital/django-content-settings/blob/master/content_settings/types/basic.py#L197)

Return the format (PREVIEW Enum) to use for the admin preview.

Use admin_preview_as attribute

## def get_on_change(self) [source](https://github.com/occipital/django-content-settings/blob/master/content_settings/types/basic.py#L205)

Return the list of functions to call when the setting is changed.

Use on_change attribute

## def get_on_change_commited(self) [source](https://github.com/occipital/django-content-settings/blob/master/content_settings/types/basic.py#L213)

Return the list of functions to call when the setting is changed and commited.
Uses for syncing data or triggering emails.

Use on_change_commited attribute

## def field(self) [source](https://github.com/occipital/django-content-settings/blob/master/content_settings/types/basic.py#L223)

the form field

## def get_suffixes(self) [source](https://github.com/occipital/django-content-settings/blob/master/content_settings/types/basic.py#L229)

Return the list of suffixes that can be used

## def can_suffix(self, suffix: Optional[str]) [source](https://github.com/occipital/django-content-settings/blob/master/content_settings/types/basic.py#L235)

Return True if the suffix is valid for the setting.

## def can_assign(self, name: str) [source](https://github.com/occipital/django-content-settings/blob/master/content_settings/types/basic.py#L241)

Return True if the attribute can be assigned to the instance.

## def get_help_format(self) [source](https://github.com/occipital/django-content-settings/blob/master/content_settings/types/basic.py#L247)

Generate help for the specific type.

The help of the format goes after the help for the specific setting and expalins the format of the setting.

## def get_help(self) [source](https://github.com/occipital/django-content-settings/blob/master/content_settings/types/basic.py#L255)

Generate help for the specific setting (includes format help)

## def get_tags(self) [source](https://github.com/occipital/django-content-settings/blob/master/content_settings/types/basic.py#L267)

Return the tags associated with the setting.

## def get_content_tags(self, name: str, value: str) [source](https://github.com/occipital/django-content-settings/blob/master/content_settings/types/basic.py#L276)

Generate tags based on current type and value.

Uses CONTENT_SETTINGS_TAGS for generating, but overriding the method allows you to change the behavior for the specific type.

## def get_validators(self) [source](https://github.com/occipital/django-content-settings/blob/master/content_settings/types/basic.py#L286)

Return the list of validators to apply to the setting python value.

## def get_validators_raw(self) [source](https://github.com/occipital/django-content-settings/blob/master/content_settings/types/basic.py#L292)

Return the list of validators to apply to the setting text value.

## def get_field(self) [source](https://github.com/occipital/django-content-settings/blob/master/content_settings/types/basic.py#L298)

Generate the form field for the setting. Which will be used in the django admin panel.

## def get_widget(self) [source](https://github.com/occipital/django-content-settings/blob/master/content_settings/types/basic.py#L308)

Generate the form widget for the setting. Which will be used in the django admin panel.

## def validate_raw_value(self, value: str) [source](https://github.com/occipital/django-content-settings/blob/master/content_settings/types/basic.py#L317)

Validate the text value of the setting.

## def validate_value(self, value: str) [source](https://github.com/occipital/django-content-settings/blob/master/content_settings/types/basic.py#L324)

Full validation of the setting text value.

## def validate(self, value: Any) [source](https://github.com/occipital/django-content-settings/blob/master/content_settings/types/basic.py#L334)

Validate the setting python value.

## def to_python(self, value: str) [source](https://github.com/occipital/django-content-settings/blob/master/content_settings/types/basic.py#L341)

Converts text value to python value.

## def json_view_value(self, value: Any) [source](https://github.com/occipital/django-content-settings/blob/master/content_settings/types/basic.py#L347)

Converts the setting value to JSON.

## def give_python_to_admin(self, value: str, name: str) [source](https://github.com/occipital/django-content-settings/blob/master/content_settings/types/basic.py#L353)

Converts the setting text value to setting admin value that will be used for rendering admin preview.

By default it uses to_python method, but it make sense to override it for some types, for example callable types,
where you want to show the result of the call in the preview.

## def get_admin_preview_html(self, value: Any, name: str) [source](https://github.com/occipital/django-content-settings/blob/master/content_settings/types/basic.py#L362)

Generate the admin preview for PREVIEW.HTML format.

## def get_admin_preview_text(self, value: Any, name: str) [source](https://github.com/occipital/django-content-settings/blob/master/content_settings/types/basic.py#L368)

Generate the admin preview for PREVIEW.TEXT format.

## def get_admin_preview_python(self, value: Any, name: str) [source](https://github.com/occipital/django-content-settings/blob/master/content_settings/types/basic.py#L374)

Generate the admin preview for PREVIEW.PYTHON format.

## def get_admin_preview_value(self, value: str) [source](https://github.com/occipital/django-content-settings/blob/master/content_settings/types/basic.py#L380)

Generate the admin preview for the setting based on the admin_preview_as attribute (or get_admin_preview_as method).

Using text value of the setting.

## def get_full_admin_preview_value(self, value: str) [source](https://github.com/occipital/django-content-settings/blob/master/content_settings/types/basic.py#L393)

Generate data for json response for preview

## def get_admin_preview_object(self, value: Any, name: str) [source](https://github.com/occipital/django-content-settings/blob/master/content_settings/types/basic.py#L408)

Generate the admin preview for the setting based on the admin_preview_as attribute (or get_admin_preview_as method).

Using admin value of the setting.

## def lazy_give(self, l_func: Callable, suffix = None) [source](https://github.com/occipital/django-content-settings/blob/master/content_settings/types/basic.py#L424)

Return the LazyObject that will be used for the setting value.

This value will be returned using lazy prefix in the content_settings.

## def give(self, value: Any, suffix: Optional[str] = None) [source](https://github.com/occipital/django-content-settings/blob/master/content_settings/types/basic.py#L432)

The will be returned as the content_settings attribute using python value of the setting.

Suffix can be used.

# class SimpleText(SimpleString) [source](https://github.com/occipital/django-content-settings/blob/master/content_settings/types/basic.py#L444)

Multiline text setting type.

# class SimpleTextPreview(SimpleText) [source](https://github.com/occipital/django-content-settings/blob/master/content_settings/types/basic.py#L453)

Multiline text setting type with preview. By default SimpleText and SimpleString don't have preview, but for showing preview in EachMixin, we need to have preview for each type.

# class SimpleHTML(HTMLMixin, SimpleText) [source](https://github.com/occipital/django-content-settings/blob/master/content_settings/types/basic.py#L461)

Multiline HTML setting type.

# class URLString(SimpleString) [source](https://github.com/occipital/django-content-settings/blob/master/content_settings/types/basic.py#L469)

URL setting type.

# class EmailString(SimpleString) [source](https://github.com/occipital/django-content-settings/blob/master/content_settings/types/basic.py#L480)

Email setting type.

# class SimpleInt(SimpleString) [source](https://github.com/occipital/django-content-settings/blob/master/content_settings/types/basic.py#L491)

Integer setting type.

# class SimpleBool(SimpleString) [source](https://github.com/occipital/django-content-settings/blob/master/content_settings/types/basic.py#L501)

Boolean setting type.
Attributes:
- yeses (Tuple[str]): Accepted values for True.
- noes (Tuple[str]): Accepted values for False.

# class SimpleDecimal(SimpleString) [source](https://github.com/occipital/django-content-settings/blob/master/content_settings/types/basic.py#L536)

Decimal setting type.

# class SimplePassword(SimpleString) [source](https://github.com/occipital/django-content-settings/blob/master/content_settings/types/basic.py#L546)

Password setting type. It is not possible to fetch the value using API. In the admin panel, the value is hidden.