# Module List

- [caching](#caching)
- [conf](#conf)
- [context_managers](#context_managers)
- [context_processors](#context_processors)
- [functools](#functools)
- [middlewares](#middlewares)
- [models](#models)
- [permissions](#permissions)
- [signals](#signals)
- [store](#store)
- [tags](#tags)
- [utils](#utils)
- [views](#views)
- [types.array](#typesarray)
- [types.basic](#typesbasic)
- [types.datetime](#typesdatetime)
- [types.each](#typeseach)
- [types.lazy](#typeslazy)
- [types.markup](#typesmarkup)
- [types.mixins](#typesmixins)
- [types.template](#typestemplate)
- [types.validators](#typesvalidators)
- [defaults.context](#defaultscontext)
- [defaults.filters](#defaultsfilters)
- [defaults.modifiers](#defaultsmodifiers)

` -> `Object`

### def get_call_tags()<sup>[source](https://github.com/occipital/django-content-settings/blob/master/content_settings/conf.py#L51)</sup>

returns list of functions from `CONTENT_SETTINGS_TAGS` setting that are used to generate tags for settings.
the result is cached in `CALL_TAGS` variable.

### def gen_tags(name: str, cs_type: BaseSetting, value: Any)<sup>[source](https://github.com/occipital/django-content-settings/blob/master/content_settings/conf.py#L73)</sup>

generate tags based on `CONTENT_SETTINGS_TAGS` setting.

### def register_prefix(name: str)<sup>[source](https://github.com/occipital/django-content-settings/blob/master/content_settings/conf.py#L83)</sup>

decorator for registration a new prefix

### def lazy_prefix(name: str, suffix: str)<sup>[source](https://github.com/occipital/django-content-settings/blob/master/content_settings/conf.py#L97)</sup>

lazy__ prefix that gives a lazy proxy object by the name of the setting.

### def type_prefix(name: str, suffix: str)<sup>[source](https://github.com/occipital/django-content-settings/blob/master/content_settings/conf.py#L105)</sup>

type__ prefix that return setting type by the name of the setting.

### def startswith_prefix(name: str, suffix: str)<sup>[source](https://github.com/occipital/django-content-settings/blob/master/content_settings/conf.py#L115)</sup>

startswith__ prefix that returns all settings as a dict (setting name: setting value) that start with the given name.

### def withtag_prefix(name: str, suffix: str)<sup>[source](https://github.com/occipital/django-content-settings/blob/master/content_settings/conf.py#L125)</sup>

withtag__ prefix that returns all settings as a dict (setting name: setting value) that have the given tag.

### def split_attr(value: str)<sup>[source](https://github.com/occipital/django-content-settings/blob/master/content_settings/conf.py#L167)</sup>

splits the name of the attr on 3 parts: prefix, name, suffix

* prefix should be registered by register_prefix
* name should be uppercase
* suffix can be any string, but not uppercase

### def get_str_tags(cs_name: str, cs_type: BaseSetting, value: Optional[str] = None)<sup>[source](https://github.com/occipital/django-content-settings/blob/master/content_settings/conf.py#L198)</sup>

    get tags as a text (joined by `
`) for specific setting type. name and value are used to generate content tags.

    from saving in DB.
    

### def set_initial_values_for_db(apply: bool = False)<sup>[source](https://github.com/occipital/django-content-settings/blob/master/content_settings/conf.py#L214)</sup>

sync settings with DB.
    * creates settings that are not in DB
    * updates settings that are in DB but have different attributes such as help text or tags
    * deletes settings that are in DB but are not in ALL

attribute `apply` is used to apply changes in DB immediately. Can be used in tests.

### class _Settings()<sup>[source](https://github.com/occipital/django-content-settings/blob/master/content_settings/conf.py#L318)</sup>

the main object that uses for getting settings for cache.

#### def __dir__(self)<sup>[source](https://github.com/occipital/django-content-settings/blob/master/content_settings/conf.py#L332)</sup>

dir() returns all settings names

#### def full_checksum(self)<sup>[source](https://github.com/occipital/django-content-settings/blob/master/content_settings/conf.py#L344)</sup>

the current checksum of the settings.

used for validation of settings weren't changed over time.

## context_managers

context managers for the content settings, but not all `defaults` context manager can be found in `content_settings.defaults.context.defaults`

### class content_settings_context(ContextDecorator)<sup>[source](https://github.com/occipital/django-content-settings/blob/master/content_settings/context_managers.py#L8)</sup>

context manager that overwrites settings in the context.

`**kwargs` for the context manager are the settings to overwrite, where key is a setting name and value is a raw value of the setting.

outside of the content_settings module can be used for testing.

`_raise_errors: bool = True` - if False, then ignore errors when applying value of the setting.

## context_processors

the module contains context processors for the django templates.

### def content_settings(request = None)<sup>[source](https://github.com/occipital/django-content-settings/blob/master/content_settings/context_processors.py#L8)</sup>

context processor for the django templates that provides content_settings object into template as CONTENT_SETTINGS. 

## functools

in the same way as python has functools, the module also has a few functions
to help with the function manipulation.

### def and_()<sup>[source](https://github.com/occipital/django-content-settings/blob/master/content_settings/functools.py#L7)</sup>

Returns a function that performs an 'and' operation on multiple functions.

### def or_()<sup>[source](https://github.com/occipital/django-content-settings/blob/master/content_settings/functools.py#L18)</sup>

Returns a function that performs an 'or' operation on multiple functions.

### def not_(func)<sup>[source](https://github.com/occipital/django-content-settings/blob/master/content_settings/functools.py#L29)</sup>

Returns a function that performs a 'not' operation on a function.

## middlewares

Available middlewares for the content settings.

### def preivew_on_site(get_response)<sup>[source](https://github.com/occipital/django-content-settings/blob/master/content_settings/middlewares.py#L9)</sup>

the middleware required for previewing the content settings on the site.

It checks content_settings.can_preview_on_site permission for the user and if the user has it, then the middleware will preview the content settings for the user.

## models

Django Models for the content settings.

### class ContentSetting(models.Model)<sup>[source](https://github.com/occipital/django-content-settings/blob/master/content_settings/models.py#L18)</sup>

The main model for the content settings. Is stores all of the raw values for the content settings.

#### def tags_set(self)<sup>[source](https://github.com/occipital/django-content-settings/blob/master/content_settings/models.py#L55)</sup>

tags field stores tags in a newline separated format. The property returns a set of tags.

### class HistoryContentSetting(models.Model)<sup>[source](https://github.com/occipital/django-content-settings/blob/master/content_settings/models.py#L68)</sup>

The model for the history of the content settings. Is used to store the history of changes for the content settings such as changed/added/removed.

The the generation of the history is done in two steps.
First step is to create a record when the setting is changed.
Second step is to assign other changing parameters such as by_user.

#### def update_last_record_for_name(cls, name: str, user: Optional[User] = None)<sup>[source](https://github.com/occipital/django-content-settings/blob/master/content_settings/models.py#L133)</sup>

Update the last record with the information about the source of the update.

#### def gen_unique_records(cls, name)<sup>[source](https://github.com/occipital/django-content-settings/blob/master/content_settings/models.py#L146)</sup>

The current issue is that sometimes the same setting is changed multiple times in a row.
This method is used to generate unique records for the history.

### class UserTagSetting(models.Model)<sup>[source](https://github.com/occipital/django-content-settings/blob/master/content_settings/models.py#L175)</sup>

User can assign personal tags to the settings for extending tags-filtering functionality.
The model contains those assignees.

The allowed tags to assign in Django Admin panel can be found in `CONTENT_SETTINGS_USER_TAGS` django setting.

### class UserPreview(models.Model)<sup>[source](https://github.com/occipital/django-content-settings/blob/master/content_settings/models.py#L203)</sup>

The user is allowed to preview settings before applying.

The model contains the information of which settings are currently previewing.

### class UserPreviewHistory(models.Model)<sup>[source](https://github.com/occipital/django-content-settings/blob/master/content_settings/models.py#L224)</sup>

Contains history of the user's preview settings. Because the settings can also change logic, so we want to keep the history of the settings for future investigations.

#### def user_record(cls, user: User, preview_setting: UserPreview, status: int = STATUS_CREATED)<sup>[source](https://github.com/occipital/django-content-settings/blob/master/content_settings/models.py#L250)</sup>

Making a record in the history of the user's preview settings.

## permissions

A list of functions that are used as values for type attributes such as `fetch_permission`, `view_permission`, `update_permission`, and `view_history_permission`.

### def any(user)<sup>[source](https://github.com/occipital/django-content-settings/blob/master/content_settings/permissions.py#L6)</sup>

Returns True for any user.

### def none(user)<sup>[source](https://github.com/occipital/django-content-settings/blob/master/content_settings/permissions.py#L13)</sup>

Returns False for any user.

### def authenticated(user)<sup>[source](https://github.com/occipital/django-content-settings/blob/master/content_settings/permissions.py#L20)</sup>

Returns True if the user is authenticated.

### def staff(user)<sup>[source](https://github.com/occipital/django-content-settings/blob/master/content_settings/permissions.py#L27)</sup>

Returns True if the user is active and a staff member.

### def superuser(user)<sup>[source](https://github.com/occipital/django-content-settings/blob/master/content_settings/permissions.py#L34)</sup>

Returns True if the user is active and a superuser.

### def has_perm(perm)<sup>[source](https://github.com/occipital/django-content-settings/blob/master/content_settings/permissions.py#L41)</sup>

Returns a function that checks if the user has a specific permission.

## signals

the module is used for connecting signals to the content settings.

### def do_update_stored_checksum()<sup>[source](https://github.com/occipital/django-content-settings/blob/master/content_settings/signals.py#L26)</sup>

update the stored checksum of the settings.

### def trigger_on_change(sender, instance, created)<sup>[source](https://github.com/occipital/django-content-settings/blob/master/content_settings/signals.py#L38)</sup>

Trigger on_change and on_change_commited for the content setting

## store

the module is used for collecting information.

the `APP_NAME_STORE` a dict `setting_name: app_name` is used to store the name of the app that uses the setting. Which later on can be used in `tags.app_name` to generate a tag with the name of the app.

### def add_app_name(cs_name: str, app_name: str)<sup>[source](https://github.com/occipital/django-content-settings/blob/master/content_settings/store.py#L10)</sup>

add the name of the app that uses the setting.

### def cs_has_app(cs_name: str)<sup>[source](https://github.com/occipital/django-content-settings/blob/master/content_settings/store.py#L17)</sup>

check if the setting has an app name.

### def get_app_name(cs_name: str)<sup>[source](https://github.com/occipital/django-content-settings/blob/master/content_settings/store.py#L24)</sup>

get the name of the app that uses the setting.

## tags

the functions that can be used for `CONTENT_SETTINGS_TAGS` and generate tags for the content settings based on setting name, type and value.

### def changed(name: str, cs_type: BaseSetting, value: str)<sup>[source](https://github.com/occipital/django-content-settings/blob/master/content_settings/tags.py#L10)</sup>

returns a tag `changed` if the value of the setting is different from the default value.

the name of the tag can be changed in `CONTENT_SETTINGS_TAG_CHANGED` django setting.

### def app_name(name: str, cs_type: BaseSetting, value: str)<sup>[source](https://github.com/occipital/django-content-settings/blob/master/content_settings/tags.py#L19)</sup>

returns a tag with the name of the app that uses the setting.

## utils

A set of available utilites

### def classes(setting_cls: Type[BaseSetting])<sup>[source](https://github.com/occipital/django-content-settings/blob/master/content_settings/utils.py#L10)</sup>

Returns an iterator of classes that are subclasses of the given class.

### def class_names(setting_cls: Type[BaseSetting])<sup>[source](https://github.com/occipital/django-content-settings/blob/master/content_settings/utils.py#L28)</sup>

Returns an iterator of tuple with module and class name that are subclasses of the given class.

## views

Those are the views can be used in the Integration with the Project.

## types.array

Types that convert a string into a list of values.

### class SimpleStringsList(SimpleText)<sup>[source](https://github.com/occipital/django-content-settings/blob/master/content_settings/types/array.py#L37)</sup>

    Split a text into a list of strings.

    * comment_starts_with (default: #): if not None, the lines that start with this string are removed
    * filter_empty (default: True): if True, empty lines are removed
    * split_lines (default: 
): the string that separates the lines
    * filters (default: None): a list of additional filters to apply to the lines.
    

#### def get_filters(self)<sup>[source](https://github.com/occipital/django-content-settings/blob/master/content_settings/types/array.py#L62)</sup>

Get the filters based on the current configuration.

* If filters is not None, it is returned.
* If filter_empty is True, f_empty is added to the filters.
* If comment_starts_with is not None, f_comment is added to the filters.

#### def gen_to_python(self, value: str)<sup>[source](https://github.com/occipital/django-content-settings/blob/master/content_settings/types/array.py#L121)</sup>

Converts a string value into a generator of filtered lines.

### def split_validator_in(values: List[str])<sup>[source](https://github.com/occipital/django-content-settings/blob/master/content_settings/types/array.py#L155)</sup>

Returns a validator function that checks if a given value is in the specified list of values.
It uses for SplitTextByFirstLine.split_key_validator.

### class SplitTextByFirstLine(SimpleText)<sup>[source](https://github.com/occipital/django-content-settings/blob/master/content_settings/types/array.py#L167)</sup>

Split text by the separator that can be found in the first line.
The result is a dictionary where the keys are the separators and the values are the text after the separator.

If your defaukt key is "EN", the first line can be "===== EN =====" to initialize the separator.
The next separator is initialized by the next line that starts with "=====", ends with "=====" and has a key in the middle.

It has the following new attributes:

* split_default_key: Optional[str] = None - the key which will be used for the first line
* split_default_chooser: Optional[Callable] = None - the function which will be used for chosing default value
* split_not_found - what should be done if the required key not found. `NOT_FOUND.DEFAULT` - return default value, `NOT_FOUND.KEY_ERROR` raise an exception and `NOT_FOUND.VALUE` return value from split_NOT_FOUND.VALUE
* split_not_found_value: Any = None - value that will be returned if the required key not found and split_not_found is `NOT_FOUND.VALUE`
* split_key_validator: Optional[Callable[[str], bool]] = None - function that validates a key. You can use a function `split_validator_in` for validator value
* split_key_validator_failed: str = SPLIT_FAIL.IGNORE - what should be done if the key is not valid. `SPLIT_FAIL.IGNORE` - just use line with unvalid key as value for the previous key. `SPLIT_FAIL.RAISE` - raise `ValidationError`

#### def split_value(self, value: str)<sup>[source](https://github.com/occipital/django-content-settings/blob/master/content_settings/types/array.py#L237)</sup>

The main function of the type. Split the value into a dictionary of values.

### class SplitByFirstLine(AdminPreviewSuffixesMixin, EachMixin, SplitTextByFirstLine)<sup>[source](https://github.com/occipital/django-content-settings/blob/master/content_settings/types/array.py#L288)</sup>

The same as SplitTextByFirstLine, but results are converted to the specified type.

split_type attribute is used to specify the type of the values. It can be a dict to specify the type for each key.

### class SplitTranslation(SplitByFirstLine)<sup>[source](https://github.com/occipital/django-content-settings/blob/master/content_settings/types/array.py#L324)</sup>

SplitByFirstLine where the default value will be chosen by the current language

## types.basic

The most basic types for the content settings. SimpleString is used as the base for all other types.

### class SimpleString(BaseSetting)<sup>[source](https://github.com/occipital/django-content-settings/blob/master/content_settings/types/basic.py#L26)</sup>

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

#### def __init__(self, default: Optional[Union[str, required, optional]] = None)<sup>[source](https://github.com/occipital/django-content-settings/blob/master/content_settings/types/basic.py#L80)</sup>

The init function accepts initial attributes for the content setting type.
It can assing any attribute that is defined in the class. (The exception is help_text instead of help)

All of the changes for type instance can only be done inside of __init__ method. The other methods should not change self object.

#### def init_assign_kwargs(self, kwargs)<sup>[source](https://github.com/occipital/django-content-settings/blob/master/content_settings/types/basic.py#L115)</sup>

Assign the attributes from the kwargs to the instance.

Use init__{attribute_name} method if it exists, otherwise use setattr

#### def init__tags(self, tags: Union[None, str, Iterable[str]])<sup>[source](https://github.com/occipital/django-content-settings/blob/master/content_settings/types/basic.py#L129)</sup>

Assign the tags to the instance from kwargs.

#### def can_view(self, user)<sup>[source](https://github.com/occipital/django-content-settings/blob/master/content_settings/types/basic.py#L143)</sup>

Return True if the user has permission to view the setting in the django admin panel.

Use view_permission attribute

#### def can_view_history(self, user)<sup>[source](https://github.com/occipital/django-content-settings/blob/master/content_settings/types/basic.py#L151)</sup>

Return True if the user has permission to view the setting changing history in the django admin panel.

Use view_history_permission attribute, but if it is None, use can_view

#### def can_update(self, user)<sup>[source](https://github.com/occipital/django-content-settings/blob/master/content_settings/types/basic.py#L163)</sup>

Return True if the user has permission to update the setting in the django admin panel.

Use update_permission attribute

#### def can_fetch(self, user)<sup>[source](https://github.com/occipital/django-content-settings/blob/master/content_settings/types/basic.py#L171)</sup>

Return True if the user has permission to fetch the setting value using API.

Use fetch_permission attribute

#### def get_admin_preview_as(self)<sup>[source](https://github.com/occipital/django-content-settings/blob/master/content_settings/types/basic.py#L179)</sup>

Return the format (PREVIEW Enum) to use for the admin preview.

Use admin_preview_as attribute

#### def get_on_change(self)<sup>[source](https://github.com/occipital/django-content-settings/blob/master/content_settings/types/basic.py#L187)</sup>

Return the list of functions to call when the setting is changed.

Use on_change attribute

#### def get_on_change_commited(self)<sup>[source](https://github.com/occipital/django-content-settings/blob/master/content_settings/types/basic.py#L195)</sup>

Return the list of functions to call when the setting is changed and commited.
Uses for syncing data or triggering emails.

Use on_change_commited attribute

#### def field(self)<sup>[source](https://github.com/occipital/django-content-settings/blob/master/content_settings/types/basic.py#L205)</sup>

the form field

#### def get_suffixes(self)<sup>[source](https://github.com/occipital/django-content-settings/blob/master/content_settings/types/basic.py#L211)</sup>

Return the list of suffixes that can be used

#### def can_suffix(self, suffix: Optional[str])<sup>[source](https://github.com/occipital/django-content-settings/blob/master/content_settings/types/basic.py#L217)</sup>

Return True if the suffix is valid for the setting.

#### def can_assign(self, name: str)<sup>[source](https://github.com/occipital/django-content-settings/blob/master/content_settings/types/basic.py#L223)</sup>

Return True if the attribute can be assigned to the instance.

#### def get_help_format(self)<sup>[source](https://github.com/occipital/django-content-settings/blob/master/content_settings/types/basic.py#L229)</sup>

Generate help for the specific type.

The help of the format goes after the help for the specific setting and expalins the format of the setting.

#### def get_help(self)<sup>[source](https://github.com/occipital/django-content-settings/blob/master/content_settings/types/basic.py#L237)</sup>

Generate help for the specific setting (includes format help)

#### def get_tags(self)<sup>[source](https://github.com/occipital/django-content-settings/blob/master/content_settings/types/basic.py#L249)</sup>

Return the tags associated with the setting.

#### def get_content_tags(self, name: str, value: str)<sup>[source](https://github.com/occipital/django-content-settings/blob/master/content_settings/types/basic.py#L258)</sup>

Generate tags based on current type and value.

Uses CONTENT_SETTINGS_TAGS for generating, but overriding the method allows you to change the behavior for the specific type.

#### def get_validators(self)<sup>[source](https://github.com/occipital/django-content-settings/blob/master/content_settings/types/basic.py#L268)</sup>

Return the list of validators to apply to the setting python value.

#### def get_validators_raw(self)<sup>[source](https://github.com/occipital/django-content-settings/blob/master/content_settings/types/basic.py#L274)</sup>

Return the list of validators to apply to the setting text value.

#### def get_field(self)<sup>[source](https://github.com/occipital/django-content-settings/blob/master/content_settings/types/basic.py#L280)</sup>

Generate the form field for the setting. Which will be used in the django admin panel.

#### def get_widget(self)<sup>[source](https://github.com/occipital/django-content-settings/blob/master/content_settings/types/basic.py#L290)</sup>

Generate the form widget for the setting. Which will be used in the django admin panel.

#### def validate_raw_value(self, value: str)<sup>[source](https://github.com/occipital/django-content-settings/blob/master/content_settings/types/basic.py#L299)</sup>

Validate the text value of the setting.

#### def validate_value(self, value: str)<sup>[source](https://github.com/occipital/django-content-settings/blob/master/content_settings/types/basic.py#L306)</sup>

Full validation of the setting text value.

#### def validate(self, value: Any)<sup>[source](https://github.com/occipital/django-content-settings/blob/master/content_settings/types/basic.py#L316)</sup>

Validate the setting python value.

#### def to_python(self, value: str)<sup>[source](https://github.com/occipital/django-content-settings/blob/master/content_settings/types/basic.py#L323)</sup>

Converts text value to python value.

#### def json_view_value(self, value: Any)<sup>[source](https://github.com/occipital/django-content-settings/blob/master/content_settings/types/basic.py#L329)</sup>

Converts the setting value to JSON.

#### def give_python_to_admin(self, value: str, name: str)<sup>[source](https://github.com/occipital/django-content-settings/blob/master/content_settings/types/basic.py#L335)</sup>

Converts the setting text value to setting admin value that will be used for rendering admin preview.

By default it uses to_python method, but it make sense to override it for some types, for example callable types,
where you want to show the result of the call in the preview.

#### def get_admin_preview_html(self, value: Any, name: str)<sup>[source](https://github.com/occipital/django-content-settings/blob/master/content_settings/types/basic.py#L344)</sup>

Generate the admin preview for PREVIEW.HTML format.

#### def get_admin_preview_text(self, value: Any, name: str)<sup>[source](https://github.com/occipital/django-content-settings/blob/master/content_settings/types/basic.py#L350)</sup>

Generate the admin preview for PREVIEW.TEXT format.

#### def get_admin_preview_python(self, value: Any, name: str)<sup>[source](https://github.com/occipital/django-content-settings/blob/master/content_settings/types/basic.py#L356)</sup>

Generate the admin preview for PREVIEW.PYTHON format.

#### def get_admin_preview_value(self, value: str)<sup>[source](https://github.com/occipital/django-content-settings/blob/master/content_settings/types/basic.py#L362)</sup>

Generate the admin preview for the setting based on the admin_preview_as attribute (or get_admin_preview_as method).

Using text value of the setting.

#### def get_full_admin_preview_value(self, value: str)<sup>[source](https://github.com/occipital/django-content-settings/blob/master/content_settings/types/basic.py#L375)</sup>

Generate data for json response for preview

#### def get_admin_preview_object(self, value: Any, name: str)<sup>[source](https://github.com/occipital/django-content-settings/blob/master/content_settings/types/basic.py#L390)</sup>

Generate the admin preview for the setting based on the admin_preview_as attribute (or get_admin_preview_as method).

Using admin value of the setting.

#### def lazy_give(self, l_func: Callable, suffix = None)<sup>[source](https://github.com/occipital/django-content-settings/blob/master/content_settings/types/basic.py#L406)</sup>

Return the LazyObject that will be used for the setting value.

This value will be returned using lazy prefix in the content_settings.

#### def give(self, value: Any, suffix: Optional[str] = None)<sup>[source](https://github.com/occipital/django-content-settings/blob/master/content_settings/types/basic.py#L414)</sup>

The will be returned as the content_settings attribute using python value of the setting.

Suffix can be used.

### class SimpleText(SimpleString)<sup>[source](https://github.com/occipital/django-content-settings/blob/master/content_settings/types/basic.py#L426)</sup>

Multiline text setting type.

### class SimpleTextPreview(SimpleText)<sup>[source](https://github.com/occipital/django-content-settings/blob/master/content_settings/types/basic.py#L435)</sup>

Multiline text setting type with preview. By default SimpleText and SimpleString don't have preview, but for showing preview in EachMixin, we need to have preview for each type.

### class SimpleHTML(HTMLMixin, SimpleText)<sup>[source](https://github.com/occipital/django-content-settings/blob/master/content_settings/types/basic.py#L443)</sup>

Multiline HTML setting type.

### class URLString(SimpleString)<sup>[source](https://github.com/occipital/django-content-settings/blob/master/content_settings/types/basic.py#L451)</sup>

URL setting type.

### class EmailString(SimpleString)<sup>[source](https://github.com/occipital/django-content-settings/blob/master/content_settings/types/basic.py#L462)</sup>

Email setting type.

### class SimpleInt(SimpleString)<sup>[source](https://github.com/occipital/django-content-settings/blob/master/content_settings/types/basic.py#L473)</sup>

Integer setting type.

### class SimpleBool(SimpleString)<sup>[source](https://github.com/occipital/django-content-settings/blob/master/content_settings/types/basic.py#L483)</sup>

Boolean setting type.
Attributes:
- yeses (Tuple[str]): Accepted values for True.
- noes (Tuple[str]): Accepted values for False.

### class SimpleDecimal(SimpleString)<sup>[source](https://github.com/occipital/django-content-settings/blob/master/content_settings/types/basic.py#L518)</sup>

Decimal setting type.

### class SimplePassword(SimpleString)<sup>[source](https://github.com/occipital/django-content-settings/blob/master/content_settings/types/basic.py#L528)</sup>

Password setting type. It is not possible to fetch the value using API. In the admin panel, the value is hidden.

## types.datetime

Types that convert a string into a datetime, date, time or timedelta object.

### def timedelta_format(text: str)<sup>[source](https://github.com/occipital/django-content-settings/blob/master/content_settings/types/datetime.py#L25)</sup>

Convert a string into a timedelta object using format from `TIMEDELTA_FORMATS`.
For example:
- `1d` - one day
- `1d 3h` - one day and three hours

### class ProcessInputFormats(EmptyNoneMixin, SimpleString)<sup>[source](https://github.com/occipital/django-content-settings/blob/master/content_settings/types/datetime.py#L47)</sup>

Base class for converting a string into a datetime, date or time object. (Teachnically can be used for other fields with predefined formats by overriding `postprocess_input_format` method.)

It uses the `input_formats_field` from the Meta class to get the filed with formats.

We want to use different field for different formats as we want to be able to override specific format in using `CONTENT_SETTINGS_CONTEXT`

#### def postprocess_input_format(self, value: Any, format: Any)<sup>[source](https://github.com/occipital/django-content-settings/blob/master/content_settings/types/datetime.py#L61)</sup>

converts a given value using a given format

### class DateTimeString(ProcessInputFormats)<sup>[source](https://github.com/occipital/django-content-settings/blob/master/content_settings/types/datetime.py#L101)</sup>

Converts into a datetime object.

Attributes:

- `datetime_formats` - list (or a single string) of formats to use for conversion. As a default it uses `DATETIME_INPUT_FORMATS` from `django.conf.settings`

### class DateString(ProcessInputFormats)<sup>[source](https://github.com/occipital/django-content-settings/blob/master/content_settings/types/datetime.py#L121)</sup>

Converts into a date object.

Attributes:

- `date_formats` - list (or a single string) of formats to use for conversion. As a default it uses `DATE_INPUT_FORMATS` from `django.conf.settings`

### class TimeString(DateTimeString)<sup>[source](https://github.com/occipital/django-content-settings/blob/master/content_settings/types/datetime.py#L139)</sup>

Converts into a time object.

Attributes:

- `time_formats` - list (or a single string) of formats to use for conversion. As a default it uses `TIME_INPUT_FORMATS` from `django.conf.settings`

### class SimpleTimedelta(SimpleString)<sup>[source](https://github.com/occipital/django-content-settings/blob/master/content_settings/types/datetime.py#L160)</sup>

Converts into a timedelta object.

## types.each

EachMixin is the main mixin of the module, which allows types to have subtypes, that check, preview and converts the structure of the value.

For example `array.TypedStringsList`

### class Item(BaseEach)<sup>[source](https://github.com/occipital/django-content-settings/blob/master/content_settings/types/each.py#L49)</sup>

Converts each element of the array into a specific type `cs_type`

### class Keys(BaseEach)<sup>[source](https://github.com/occipital/django-content-settings/blob/master/content_settings/types/each.py#L117)</sup>

Converts values of the specific keys into specific types `cs_types`

### class Values(BaseEach)<sup>[source](https://github.com/occipital/django-content-settings/blob/master/content_settings/types/each.py#L215)</sup>

Converts each value of the given dict into `cs_type`

### class EachMixin()<sup>[source](https://github.com/occipital/django-content-settings/blob/master/content_settings/types/each.py#L284)</sup>

Attributes:

- `each` - the type of the subvalues.
- `each_suffix_use` - how to use the suffixes. Can be `USE_OWN`, `USE_PARENT`, `SPLIT_OWN`, `SPLIT_PARENT`
- `each_suffix_splitter` - the string that separates the suffixes. Applicable only when `each_suffix_use` is `SPLIT_OWN` or `SPLIT_PARENT`

## types.lazy

Classes that uses for lazy loading of objects.

Check `BaseString.lazy_give` and `conf.lazy_prefix`

## types.markup

The module contains types of different formats such as JSON, YAML, CSV, and so on.

### class SimpleYAML(SimpleText)<sup>[source](https://github.com/occipital/django-content-settings/blob/master/content_settings/types/markup.py#L17)</sup>

YAML content settings type. Requires yaml module.

### class SimpleJSON(EmptyNoneMixin, SimpleText)<sup>[source](https://github.com/occipital/django-content-settings/blob/master/content_settings/types/markup.py#L60)</sup>

JSON content settings type.

### class SimpleRawCSV(SimpleText)<sup>[source](https://github.com/occipital/django-content-settings/blob/master/content_settings/types/markup.py#L88)</sup>

Type that converts simple CSV to list of lists.

### class SimpleCSV(EachMixin, SimpleRawCSV)<sup>[source](https://github.com/occipital/django-content-settings/blob/master/content_settings/types/markup.py#L136)</sup>

Type that converts simple CSV to list of dictionaries.

Attributes:

- `csv_fields` (dict, tuple or list): defines the structure of the CSV. The structure definition used by `EachMixin`
- `csv_fields_list_type` (BaseSetting): the type of the list elements in the `csv_fields` if it is not dict.

Examples:

```python
SimpleCSV(csv_fields=["name", "price"])
SimpleCSV(csv_fields={"name": SimpleString(), "price": SimpleDecimal()})
SimpleCSV(csv_fields=["name", "price"], csv_fields_list_type=SimpleString())
```

## types.mixins



### def mix()<sup>[source](https://github.com/occipital/django-content-settings/blob/master/content_settings/types/mixins.py#L15)</sup>

Returns a mix of types. Mixins should go first and the last one should be the main type.

Example:
mix(HTMLMixin, SimpleInt)

### class MinMaxValidationMixin()<sup>[source](https://github.com/occipital/django-content-settings/blob/master/content_settings/types/mixins.py#L25)</sup>

Mixin that validates that value is between min_value and max_value.

Attributes:
min_value: Minimum value. If None, then no minimum value.
max_value: Maximum value. If None, then no maximum value.

### class EmptyNoneMixin()<sup>[source](https://github.com/occipital/django-content-settings/blob/master/content_settings/types/mixins.py#L66)</sup>

Mixin for types that returns None if value is empty string.

### class HTMLMixin()<sup>[source](https://github.com/occipital/django-content-settings/blob/master/content_settings/types/mixins.py#L79)</sup>

Mixin for types that should be displayed in HTML format.
And also returned content should be marked as safe.

### class PositiveValidationMixin(MinMaxValidationMixin)<sup>[source](https://github.com/occipital/django-content-settings/blob/master/content_settings/types/mixins.py#L96)</sup>

Mixin that validates that value is positive.

### class CallToPythonMixin()<sup>[source](https://github.com/occipital/django-content-settings/blob/master/content_settings/types/mixins.py#L104)</sup>

Mixin for callable types, or types that should be called to get the value.

### class GiveCallMixin()<sup>[source](https://github.com/occipital/django-content-settings/blob/master/content_settings/types/mixins.py#L184)</sup>

Mixin for callable types, but result of the call without artuments should be returned.

If suffix is "call" then callable should be returned.

### class MakeCallMixin()<sup>[source](https://github.com/occipital/django-content-settings/blob/master/content_settings/types/mixins.py#L211)</sup>

Mixin for non-callable python objects will be returned as callable given.

Can be usefull when you change callable types to a simple type but don't want to change the code that uses that type.

### class DictSuffixesMixin()<sup>[source](https://github.com/occipital/django-content-settings/blob/master/content_settings/types/mixins.py#L228)</sup>

Mixin that adds suffixes to the type using dictionary of functions.

### class AdminPreviewMenuMixin()<sup>[source](https://github.com/occipital/django-content-settings/blob/master/content_settings/types/mixins.py#L241)</sup>

Mixin that adds a menu to the admin preview.

### class AdminPreviewSuffixesMixin(AdminSuffixesMixinPreview, AdminPreviewMenuMixin)<sup>[source](https://github.com/occipital/django-content-settings/blob/master/content_settings/types/mixins.py#L308)</sup>

Mixin shows links to preview different suffixes of the value in the admin preview.

### class AdminActionsMixinPreview()<sup>[source](https://github.com/occipital/django-content-settings/blob/master/content_settings/types/mixins.py#L338)</sup>

Mixin that adds actions to the admin preview.

## types.template

One of the most complicated module contains callable types. The Python object for those types usually needs to be called.

The complexity of the module also illustrates the flexibility of types.

The module is called a "template" because the setting's raw value is a template that will be used to generate a real value.

See `CallToPythonMixin`

### class StaticDataMixin()<sup>[source](https://github.com/occipital/django-content-settings/blob/master/content_settings/types/template.py#L32)</sup>

Adds static data to the context, such as SETTINGS or/and CONTENT_SETTINGS.

Attributes:

- `template_static_includes` - tuple of `STATIC_INCLUDES` that should be included in the context. Default: `(STATIC_INCLUDES.CONTENT_SETTINGS, STATIC_INCLUDES.SETTINGS)`. If `STATIC_INCLUDES.SETTINGS` is included, `django.conf.settings` will be added to the context. If `STATIC_INCLUDES.CONTENT_SETTINGS` is included, `content_settings.conf.content_settings` will be added to the context.
- `template_static_data` - static data that should be added to the context (on top of what will be added by `template_static_includes`). It can be a dictionary or a callable that returns a dictionary. Default: `None`.

### class SimpleCallTemplate(CallToPythonMixin, StaticDataMixin, SimpleText)<sup>[source](https://github.com/occipital/django-content-settings/blob/master/content_settings/types/template.py#L74)</sup>

Base class for templates that can be called.

#### def prepate_input_to_dict(self)<sup>[source](https://github.com/occipital/django-content-settings/blob/master/content_settings/types/template.py#L126)</sup>

prepares an inpit dictuonary for the call based on the given arguments and kwargs

### class DjangoTemplate(SimpleCallTemplate)<sup>[source](https://github.com/occipital/django-content-settings/blob/master/content_settings/types/template.py#L152)</sup>

The setting of that type generates value based on the Django Template in the raw value.

### class DjangoTemplateNoArgs(GiveCallMixin, DjangoTemplate)<sup>[source](https://github.com/occipital/django-content-settings/blob/master/content_settings/types/template.py#L188)</sup>

Same as `DjangoTemplate` but the setting value is not callablle, but already rendered value.

### class DjangoTemplateHTML(HTMLMixin, DjangoTemplateNoArgs)<sup>[source](https://github.com/occipital/django-content-settings/blob/master/content_settings/types/template.py#L196)</sup>

Same as `DjangoTemplateNoArgs` but the rendered value is marked as safe.

### class DjangoModelTemplateMixin()<sup>[source](https://github.com/occipital/django-content-settings/blob/master/content_settings/types/template.py#L204)</sup>

Mixing that uses one argument for the template from the model queryset.

Attributes:

- `model_queryset` - QuerySet or a callable that returns a Model Object. For QuerySet, the first object will be used. For callable, the object returned by the callable will be used. The generated object will be used as validator and for preview.
- `obj_name` - name of the object in the template. Default: "object".

#### def get_first_call_validator(self)<sup>[source](https://github.com/occipital/django-content-settings/blob/master/content_settings/types/template.py#L223)</sup>

generates the first validator based of model_queryset, which will be used for validation and for preview.

### class DjangoModelTemplate(DjangoModelTemplateMixin, DjangoTemplate)<sup>[source](https://github.com/occipital/django-content-settings/blob/master/content_settings/types/template.py#L247)</sup>

Django Template that uses one argument as a model object.

### class DjangoModelTemplateHTML(DjangoModelTemplate)<sup>[source](https://github.com/occipital/django-content-settings/blob/master/content_settings/types/template.py#L255)</sup>

Same as `DjangoModelTemplate` but the rendered value is marked as safe.

### class SimpleEval(SimpleCallTemplate)<sup>[source](https://github.com/occipital/django-content-settings/blob/master/content_settings/types/template.py#L267)</sup>

Template that evaluates the Python code (using `eval` function).

By default, `update_permission` is set to `superuser`.

### class DjangoModelEval(DjangoModelTemplateMixin, SimpleEval)<sup>[source](https://github.com/occipital/django-content-settings/blob/master/content_settings/types/template.py#L295)</sup>

Same as `SimpleEval` but uses one value as a model object.

### class SimpleEvalNoArgs(GiveCallMixin, SimpleEval)<sup>[source](https://github.com/occipital/django-content-settings/blob/master/content_settings/types/template.py#L303)</sup>

Same as `SimpleEval` but the setting value is not callable, but already evaluated.

### class SimpleExec(SimpleCallTemplate)<sup>[source](https://github.com/occipital/django-content-settings/blob/master/content_settings/types/template.py#L311)</sup>

Template that executes the Python code (using `exec` function).

By default, `update_permission` is set to `superuser`.

Attributes:

- `call_return` - dictates what will be returned as a setting value.
    - If `None`, the whole context will be returned.
    - If a dictionary, only the keys from the dictionary will be returned. The values will be used as defaults.
    - If a callable, the callable will be called and the return value will be used as a dictionary.
    - If an iterable, the iterable will be used as keys for the return dictionary. The values will be `None` by default.
- `allow_import` - allows importing modules. Default: `False`.

### class DjangoModelExec(DjangoModelTemplateMixin, SimpleExec)<sup>[source](https://github.com/occipital/django-content-settings/blob/master/content_settings/types/template.py#L377)</sup>

Same as `SimpleExec` but uses one value as a model object.

### class SimpleExecNoArgs(GiveCallMixin, SimpleExec)<sup>[source](https://github.com/occipital/django-content-settings/blob/master/content_settings/types/template.py#L385)</sup>

Same as `SimpleExec` but the setting value is not callable, but already executed.

### class SimpleExecNoCall(StaticDataMixin, SimpleText)<sup>[source](https://github.com/occipital/django-content-settings/blob/master/content_settings/types/template.py#L393)</sup>

Same as `SimpleExec` but the setting value is not callable, but already executed.

The class is not inherited from `SimpleCallTemplate`, and technically can be a part of markdown module.

### class GiveOneKeyMixin()<sup>[source](https://github.com/occipital/django-content-settings/blob/master/content_settings/types/template.py#L439)</sup>

Mixin that returns only one key from the result dict.

Attributes:

- `one_key_name` - name of the key that will be returned. Default: "result".

### class SimpleExecOneKey(GiveOneKeyMixin, SimpleExec)<sup>[source](https://github.com/occipital/django-content-settings/blob/master/content_settings/types/template.py#L460)</sup>

Same as `SimpleExec` but returns only one key (from attribute `one_key_name`) from the result dict.

### class SimpleExecOneKeyNoCall(GiveOneKeyMixin, SimpleExecNoCall)<sup>[source](https://github.com/occipital/django-content-settings/blob/master/content_settings/types/template.py#L468)</sup>

Same as `SimpleExecNoCall` but returns only one key (from attribute `one_key_name`) from the result dict.

## types.validators

A list of functions that are used as values for validators attribute of a type.

### class call_validator()<sup>[source](https://github.com/occipital/django-content-settings/blob/master/content_settings/types/validators.py#L9)</sup>

create a valiator that calls the function with the given args and kwargs.

### class gen_call_validator(call_validator)<sup>[source](https://github.com/occipital/django-content-settings/blob/master/content_settings/types/validators.py#L42)</sup>

Same as call_validator, but the args and kwargs are generated by a given function.

Create a valiator that calls the function that generates the args and kwargs, that will be used for the call.

The function will be regenerated every time when the validator is called.

The reason of having one is when you are not able to get possible args at the time of the creation of the validator.

### class gen_args_call_validator(gen_call_validator)<sup>[source](https://github.com/occipital/django-content-settings/blob/master/content_settings/types/validators.py#L89)</sup>

Same as gen_call_validator, but only generates the list for args.

### class gen_signle_arg_call_validator(gen_call_validator)<sup>[source](https://github.com/occipital/django-content-settings/blob/master/content_settings/types/validators.py#L98)</sup>

Same as gen_call_validator, but only generates one arg.

### class gen_kwargs_call_validator(gen_call_validator)<sup>[source](https://github.com/occipital/django-content-settings/blob/master/content_settings/types/validators.py#L107)</sup>

Same as gen_call_validator, but only generates the dict for kwargs.

## defaults.context



### def defaults()<sup>[source](https://github.com/occipital/django-content-settings/blob/master/content_settings/defaults/context.py#L16)</sup>

Context manager for setting defaults.

### def default_tags(tags: Set[str])<sup>[source](https://github.com/occipital/django-content-settings/blob/master/content_settings/defaults/context.py#L28)</sup>

defaults context for setting default tags.

### def default_help_prefix(prefix: str)<sup>[source](https://github.com/occipital/django-content-settings/blob/master/content_settings/defaults/context.py#L37)</sup>

defaults context for setting default help prefix.

### def default_help_suffix(suffix: str)<sup>[source](https://github.com/occipital/django-content-settings/blob/master/content_settings/defaults/context.py#L46)</sup>

defaults context for setting default help suffix.

### def defaults_modifiers(setting: BaseSetting)<sup>[source](https://github.com/occipital/django-content-settings/blob/master/content_settings/defaults/context.py#L54)</sup>

Generator for all modifiers for the given setting.

### def update_defaults(setting: BaseSetting, kwargs: Dict[str, Any])<sup>[source](https://github.com/occipital/django-content-settings/blob/master/content_settings/defaults/context.py#L64)</sup>

Update paramas of the setting type by applying all of the modifiers from the defaults context.

## defaults.filters

Functions that can be used as filters for the `DEFAULTS` setting.

Each function has a single attribute *settings type* and should return a boolean.

### def any_name(cls: Type[BaseSetting])<sup>[source](https://github.com/occipital/django-content-settings/blob/master/content_settings/defaults/filters.py#L15)</sup>

Allow all settings.

### def name_exact(name: str)<sup>[source](https://github.com/occipital/django-content-settings/blob/master/content_settings/defaults/filters.py#L22)</sup>

Allow only settings with the exact type name or parent type name.

Args:
    name (str): The exact name to match.

### def full_name_exact(name: str)<sup>[source](https://github.com/occipital/django-content-settings/blob/master/content_settings/defaults/filters.py#L36)</sup>

Allow only settings with the exact full type name or parent type name. The name includes module name.

Args:
    name (str): The exact full name to match, including the module.

## defaults.modifiers

Modifiers are functions that take kwargs and return updates for that dict.

Modifiers are using in `DEFAULTS` second element of the tuple and as `defaults` arguments.

### class NotSet()<sup>[source](https://github.com/occipital/django-content-settings/blob/master/content_settings/defaults/modifiers.py#L12)</sup>

A reference to say that the value is not set. (Using None is not possible)

### class SkipSet(Exception)<sup>[source](https://github.com/occipital/django-content-settings/blob/master/content_settings/defaults/modifiers.py#L20)</sup>

For unite modifiers, to skip setting the value.

### def set_if_missing()<sup>[source](https://github.com/occipital/django-content-settings/blob/master/content_settings/defaults/modifiers.py#L26)</sup>

Set key-value pairs in the updates dictionary if they are not already set in kwargs. This modifier is used for all `**kwargs` attributes for `defaults` context.

Args:
    **params: Arbitrary keyword arguments representing key-value pairs to set.

### class unite(object)<sup>[source](https://github.com/occipital/django-content-settings/blob/master/content_settings/defaults/modifiers.py#L38)</sup>

unite is a base class for modifiers that unites kwargs passed in arguments with kwargs already collected and kwargs passed in the definition of the settings type.

All child classes should implement `process` method.

Args:
    **kwargs: Arbitrary keyword arguments representing key-value pairs to unite.

#### def __call__(self, updates: Dict[str, Any], kwargs: Dict[str, Any])<sup>[source](https://github.com/occipital/django-content-settings/blob/master/content_settings/defaults/modifiers.py#L51)</sup>

Unites the provided updates and kwargs dictionaries with the parameters.

Args:
    updates: The dictionary with already collected kwargs from default context.
    kwargs: The kwargs passed in the definition of the settings type.

Returns:
    A dictionary with united key-value pairs.

#### def process(self, value: Any, up: Any, kw: Any)<sup>[source](https://github.com/occipital/django-content-settings/blob/master/content_settings/defaults/modifiers.py#L74)</sup>

Returns value for the update dictionary.

Args:
    value: The value from the parameter of the modifier.
    up: The current value in the update dictionary.
    kw: The current value in the settings kwargs.

Returns:
    The processed value to be set in the update dictionary.

### class unite_empty_not_set(unite)<sup>[source](https://github.com/occipital/django-content-settings/blob/master/content_settings/defaults/modifiers.py#L89)</sup>

unite, that is used for removing elements from the object. For example - making a smaller set or removing text from a string.

It adds an additional parameter `_empty_not_set: bool = True` that answers the question - should we remove value from updates if it is empty.

Args:
    _empty_not_set: A boolean indicating whether to remove empty values from updates.
    **kwargs: Arbitrary keyword arguments representing key-value pairs to unite.

#### def __call__(self)<sup>[source](https://github.com/occipital/django-content-settings/blob/master/content_settings/defaults/modifiers.py#L106)</sup>

Unites the provided updates and kwargs dictionaries with the parameters, removing empty values if specified.

Args:
    *args: Positional arguments.
    **kwargs: Keyword arguments.

Returns:
    A dictionary with united key-value pairs, with empty values removed if specified.

### class unite_set_add(unite)<sup>[source](https://github.com/occipital/django-content-settings/blob/master/content_settings/defaults/modifiers.py#L123)</sup>

unite that modifies a set by adding new values in it.

### class unite_set_remove(unite_empty_not_set)<sup>[source](https://github.com/occipital/django-content-settings/blob/master/content_settings/defaults/modifiers.py#L138)</sup>

unite that modifies a set by removing given values.

### def add_tags(tags: Iterable[str])<sup>[source](https://github.com/occipital/django-content-settings/blob/master/content_settings/defaults/modifiers.py#L153)</sup>

add tags to the setting

### def remove_tags(tags: Iterable[str])<sup>[source](https://github.com/occipital/django-content-settings/blob/master/content_settings/defaults/modifiers.py#L160)</sup>

Removes tags from the update context.

### def add_tag(tag: str)<sup>[source](https://github.com/occipital/django-content-settings/blob/master/content_settings/defaults/modifiers.py#L167)</sup>

same as `add_tags` but only one.

### def remove_tag(tag: str)<sup>[source](https://github.com/occipital/django-content-settings/blob/master/content_settings/defaults/modifiers.py#L174)</sup>

same as `remove_tags` but only one.

### class unite_str(unite)<sup>[source](https://github.com/occipital/django-content-settings/blob/master/content_settings/defaults/modifiers.py#L181)</sup>

unite that modifies a string by formatting it.

Args:
    _format: A string to format the value use `{new_value}` as a placeholder for the passed value in kwargs and `{old_value}` as a placeholder for the value in the update context.
    **kwargs: Arbitrary keyword arguments.

### def help_prefix(prefix: str)<sup>[source](https://github.com/occipital/django-content-settings/blob/master/content_settings/defaults/modifiers.py#L205)</sup>

add prefix to help

### def help_suffix(suffix: str)<sup>[source](https://github.com/occipital/django-content-settings/blob/master/content_settings/defaults/modifiers.py#L212)</sup>

add suffix to help