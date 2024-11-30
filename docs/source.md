# Module List

- [cache_triggers](#cache_triggers)
- [caching](#caching)
- [conf](#conf)
- [context_managers](#context_managers)
- [context_processors](#context_processors)
- [export](#export)
- [functools](#functools)
- [middlewares](#middlewares)
- [migrate](#migrate)
- [models](#models)
- [permissions](#permissions)
- [store](#store)
- [tags](#tags)
- [utils](#utils)
- [views](#views)
- [widgets](#widgets)
- [templatetags.content_settings_extras](#templatetagscontent_settings_extras)
- [types.array](#typesarray)
- [types.basic](#typesbasic)
- [types.datetime](#typesdatetime)
- [types.each](#typeseach)
- [types.lazy](#typeslazy)
- [types.markup](#typesmarkup)
- [types.mixins](#typesmixins)
- [types.template](#typestemplate)
- [types.validators](#typesvalidators)
- [defaults.collections](#defaultscollections)
- [defaults.context](#defaultscontext)
- [defaults.filters](#defaultsfilters)
- [defaults.modifiers](#defaultsmodifiers)



## cache_triggers



# Cache Trigger is a backend to sending a signal of when py object(s) should be updated

### class VersionChecksum(BaseCacheTrigger)<sup>[source](https://github.com/occipital/django-content-settings/blob/master/content_settings/cache_triggers.py#L67)</sup>

Arguments:
    * cache_backend (str, default="default"): cache backend name
    * cache_timeout (int, default=60 * 60 * 24): cache timeout
    * spliter (str, default="::"): spliter for the checksum
    * key_prefix (str, default="CS_CHECKSUM_"): key prefix for the checksum

The algorithm:

    * during the first run, the checksum is calculated for all the values from the DB and saved to the cache backend
    * the cache key is calculated based on the current versions of all of the settings.
    * if the DB values are changed it saves the new checksum under the same cache key (so only instances with the same configuration will see the change)
    * if the checksum is changed comparing to the checksum in the local storage

#### def hash_value(self, value: str)<sup>[source](https://github.com/occipital/django-content-settings/blob/master/content_settings/cache_triggers.py#L90)</sup>

generate md5 hash for a string

#### def dict_checksum(self, values: Dict[str, Any])<sup>[source](https://github.com/occipital/django-content-settings/blob/master/content_settings/cache_triggers.py#L96)</sup>

generate md5 hash for a dict with keys and values as strings

#### def cache_key(self)<sup>[source](https://github.com/occipital/django-content-settings/blob/master/content_settings/cache_triggers.py#L107)</sup>

returns cache key for checksum values (one should not be changed over time)

#### def user_cache_key_prefix(self)<sup>[source](https://github.com/occipital/django-content-settings/blob/master/content_settings/cache_triggers.py#L116)</sup>

returns cache key for user defined types (one should not be changed over time) if user defined types are not used, returns None

#### def set_local_checksum(self, value: Optional[str] = None)<sup>[source](https://github.com/occipital/django-content-settings/blob/master/content_settings/cache_triggers.py#L127)</sup>

calculate and set checksum in the local thread

#### def push_checksum(self, value: Optional[str] = None)<sup>[source](https://github.com/occipital/django-content-settings/blob/master/content_settings/cache_triggers.py#L148)</sup>

save to cache backend the checksum

#### def get_checksum_from_cache(self)<sup>[source](https://github.com/occipital/django-content-settings/blob/master/content_settings/cache_triggers.py#L158)</sup>

get the checksum from the cache backend


## caching



the caching backend is working with local thread storage to store the checksum raw and py objects.

`DATA` is a local thread storage with the following attributes:

* `ALL_RAW_VALUES: Dict[str, str]` - the raw values (values from the database) of the all settings
* `ALL_VALUES: Dict[str, Any]` - the python objects of the all settings
* `ALL_USER_DEFINES: Dict[str, BaseSetting]` - key is the setting name, value is the user defined type (with tags and help text)
* `POPULATED: bool` - the flag that indicates that all values were populated from the database

### def set_new_type(name: str, user_defined_type: str, tags_set: Set[str], help: str = '')<sup>[source](https://github.com/occipital/django-content-settings/blob/master/content_settings/caching.py#L36)</sup>

create a new user defined type and saves it to the local thread. The previous type is returned.

### def replace_user_type(name: str, cs_type: BaseSetting)<sup>[source](https://github.com/occipital/django-content-settings/blob/master/content_settings/caching.py#L56)</sup>

replace the user defined type with the new one. The previous type is returned.

### def set_new_value(name: str, new_value: str, version: Optional[str] = None)<sup>[source](https://github.com/occipital/django-content-settings/blob/master/content_settings/caching.py#L65)</sup>

takes name, raw value and saves it to the local thread if the value was changed. The previous value is returned.

raw value converts to the python object and saves to the local thread.

if version is not None - it will be verified against the version of the type

### def delete_user_value(name: str)<sup>[source](https://github.com/occipital/django-content-settings/blob/master/content_settings/caching.py#L86)</sup>

delete user defined setting from the local thread and returns its raw value

### def get_type_by_name(name: str)<sup>[source](https://github.com/occipital/django-content-settings/blob/master/content_settings/caching.py#L101)</sup>

get the type of the setting (inluding user defined types) by its name

### def get_userdefined_type_by_name(name: str)<sup>[source](https://github.com/occipital/django-content-settings/blob/master/content_settings/caching.py#L113)</sup>

get the user defined type by its name

### def get_value(name: str, suffix: Optional[str] = None)<sup>[source](https://github.com/occipital/django-content-settings/blob/master/content_settings/caching.py#L120)</sup>

get the value of the setting by its name and optional suffix

### def get_raw_value(name: str)<sup>[source](https://github.com/occipital/django-content-settings/blob/master/content_settings/caching.py#L132)</sup>

get the raw value of the setting by its name

### def get_py_value(name: str)<sup>[source](https://github.com/occipital/django-content-settings/blob/master/content_settings/caching.py#L141)</sup>

get the python object of the setting by its name

### def is_populated()<sup>[source](https://github.com/occipital/django-content-settings/blob/master/content_settings/caching.py#L150)</sup>

check if the local thread is populated with the values from the database

### def get_db_objects()<sup>[source](https://github.com/occipital/django-content-settings/blob/master/content_settings/caching.py#L157)</sup>

get the database objects for the settings

### def get_all_names()<sup>[source](https://github.com/occipital/django-content-settings/blob/master/content_settings/caching.py#L166)</sup>

get the names of the settings (including user defined types) from the local thread

### def populate()<sup>[source](https://github.com/occipital/django-content-settings/blob/master/content_settings/caching.py#L175)</sup>

reset the local thread with the values from the database

### def validate_default_values()<sup>[source](https://github.com/occipital/django-content-settings/blob/master/content_settings/caching.py#L207)</sup>

validate default values for all of the registered settings.

Only is VALIDATE_DEFAULT_VALUE is True.

### def reset_user_values(db: Optional[Dict[str, Any]] = None)<sup>[source](https://github.com/occipital/django-content-settings/blob/master/content_settings/caching.py#L228)</sup>

reset the local thread with the values from the database for user defined types

if trigger_checksum is not the same as the checksum in the local thread, the checksum in the cache backend will be updated

### def reset_values(db: Optional[Dict[str, Any]] = None)<sup>[source](https://github.com/occipital/django-content-settings/blob/master/content_settings/caching.py#L264)</sup>

reset the local thread with the values from the database for code settings

if trigger_checksum is not the same as the checksum in the local thread, the checksum in the cache backend will be updated

### def check_update()<sup>[source](https://github.com/occipital/django-content-settings/blob/master/content_settings/caching.py#L301)</sup>

check if checksum in the cache backend is the same as the checksum in the local thread

if not, the values from the database will be loaded

### def recalc_checksums()<sup>[source](https://github.com/occipital/django-content-settings/blob/master/content_settings/caching.py#L317)</sup>

recalculate the checksums in the cache backend


## conf



the module collects all settings from all apps and makes them available as `content_settings` object.

It has the following global variables:

* `USER_DEFINED_TYPES_INSTANCE: Dict[str, Callable]` - key is the slug of the user defined setting, value is a function that returns a type with tags and help text
* `USER_DEFINED_TYPES_INITIAL: Dict[str, BaseSetting]` - key is a slug of the user defined type, value is a type without tags and help text
* `USER_DEFINED_TYPES_NAME: Dict[str, str]` - the name of the user defined types
* `ALL: Dict[str, BaseSetting]` - the all registereg settings types
* `PREFIXSES: Dict[str, Callable]` - all registereg prefixes (using `register_prefix` decorator)
* `CALL_TAGS: Optional[List[Callable]]` - the list of function that is taken from `CONTENT_SETTINGS_TAGS` setting and used to generate tags for settings.

### def get_call_tags()<sup>[source](https://github.com/occipital/django-content-settings/blob/master/content_settings/conf.py#L55)</sup>

returns list of functions from `CONTENT_SETTINGS_TAGS` setting that are used to generate tags for settings.
the result is cached in `CALL_TAGS` variable.

### def gen_tags(name: str, cs_type: BaseSetting, value: Any)<sup>[source](https://github.com/occipital/django-content-settings/blob/master/content_settings/conf.py#L79)</sup>

generate tags based on `CONTENT_SETTINGS_TAGS` setting.

### def register_prefix(name: str)<sup>[source](https://github.com/occipital/django-content-settings/blob/master/content_settings/conf.py#L89)</sup>

decorator for registration a new prefix

### def lazy_prefix(name: str, suffix: str)<sup>[source](https://github.com/occipital/django-content-settings/blob/master/content_settings/conf.py#L103)</sup>

lazy__ prefix that gives a lazy proxy object by the name of the setting.

### def type_prefix(name: str, suffix: str)<sup>[source](https://github.com/occipital/django-content-settings/blob/master/content_settings/conf.py#L111)</sup>

type__ prefix that return setting type by the name of the setting.

### def startswith_prefix(name: str, suffix: str)<sup>[source](https://github.com/occipital/django-content-settings/blob/master/content_settings/conf.py#L121)</sup>

startswith__ prefix that returns all settings as a dict (setting name: setting value) that start with the given name.

### def withtag_prefix(name: str, suffix: str)<sup>[source](https://github.com/occipital/django-content-settings/blob/master/content_settings/conf.py#L131)</sup>

withtag__ prefix that returns all settings as a dict (setting name: setting value) that have the given tag.

### def split_attr(value: str)<sup>[source](https://github.com/occipital/django-content-settings/blob/master/content_settings/conf.py#L174)</sup>

splits the name of the attr on 3 parts: prefix, name, suffix

* prefix should be registered by register_prefix
* name should be uppercase
* suffix can be any string, but not uppercase

### def validate_all_with_context(context: Dict[str, Any])<sup>[source](https://github.com/occipital/django-content-settings/blob/master/content_settings/conf.py#L205)</sup>

validate all settings with the given context to make sure all of them are valid.

Do not perform if `CONTENT_SETTINGS_CHAIN_VALIDATE = False`

### def get_str_tags(cs_name: str, cs_type: BaseSetting, value: Optional[str] = None)<sup>[source](https://github.com/occipital/django-content-settings/blob/master/content_settings/conf.py#L225)</sup>

    get tags as a text (joined by `
`) for specific setting type. name and value are used to generate content tags.

    from saving in DB.
    

### def set_initial_values_for_db(apply: bool = False)<sup>[source](https://github.com/occipital/django-content-settings/blob/master/content_settings/conf.py#L241)</sup>

sync settings with DB.
    * creates settings that are not in DB
    * updates settings that are in DB but have different attributes such as help text or tags
    * deletes settings that are in DB but are not in ALL

attribute `apply` is used to apply changes in DB immediately. Can be used in tests.

### class _Settings()<sup>[source](https://github.com/occipital/django-content-settings/blob/master/content_settings/conf.py#L345)</sup>

the main object that uses for getting settings for cache.

#### def __dir__(self)<sup>[source](https://github.com/occipital/django-content-settings/blob/master/content_settings/conf.py#L359)</sup>

dir() returns all settings names

#### def form_checksum(self)<sup>[source](https://github.com/occipital/django-content-settings/blob/master/content_settings/conf.py#L371)</sup>

the current checksum of the settings.

used for validation of settings weren't changed over time.

#### def admin_head(self)<sup>[source](https://github.com/occipital/django-content-settings/blob/master/content_settings/conf.py#L380)</sup>

the admin head.

#### def admin_raw_js(self)<sup>[source](https://github.com/occipital/django-content-settings/blob/master/content_settings/conf.py#L387)</sup>

the admin raw js.


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


## export



Module for exporting, previewing and importing content settings from and to JSON

### def export_to_format(content_settings: Iterable[ContentSetting])<sup>[source](https://github.com/occipital/django-content-settings/blob/master/content_settings/export.py#L34)</sup>

Export content settings to JSON format

### def preview_data(data: dict, user: Optional[User] = None)<sup>[source](https://github.com/occipital/django-content-settings/blob/master/content_settings/export.py#L59)</sup>

Validate data and return three lists: errors, applied, skipped

Those list are used for previewing import and applying import.

### def applied_preview(name: str, value: dict, user: Optional[User] = None)<sup>[source](https://github.com/occipital/django-content-settings/blob/master/content_settings/export.py#L79)</sup>

the function returns applied element for previewing import.

if function returns None, the setting is not applied, added to skipped list instead.

if function raises an exception, the setting is not applied, added to errors list instead.

### def applied_preview_user_defined_type(name: str, value: dict, user: Optional[User] = None)<sup>[source](https://github.com/occipital/django-content-settings/blob/master/content_settings/export.py#L126)</sup>

`applied_preview` for user defined type.

### def import_to(data: Dict, applied: List[Dict], preview: bool, user: Optional[User] = None)<sup>[source](https://github.com/occipital/django-content-settings/blob/master/content_settings/export.py#L180)</sup>

Import content settings from JSON data and previewed apply data. Arguments:
- data: JSON data
- applied: List of applied settings. The list is returned by import_preview_data.
- user: User object
- preview: If True, import to preview

It raises Error if something is wrong.


## functools



in the same way as python has functools, the module also has a few functions
to help with the function manipulation.

### def and_()<sup>[source](https://github.com/occipital/django-content-settings/blob/master/content_settings/functools.py#L9)</sup>

Returns a function that performs an 'and' operation on multiple functions.

### def or_()<sup>[source](https://github.com/occipital/django-content-settings/blob/master/content_settings/functools.py#L22)</sup>

Returns a function that performs an 'or' operation on multiple functions.

### def not_(func)<sup>[source](https://github.com/occipital/django-content-settings/blob/master/content_settings/functools.py#L35)</sup>

Returns a function that performs a 'not' operation on a function.


## middlewares



Available middlewares for the content settings.

### def preivew_on_site(get_response)<sup>[source](https://github.com/occipital/django-content-settings/blob/master/content_settings/middlewares.py#L12)</sup>

the middleware required for previewing the content settings on the site.

It checks content_settings.can_preview_on_site permission for the user and if the user has it, then the middleware will preview the content settings for the user.


## migrate



A set of functions that can be used inside migrations.

### def RunImport(data: Union[str, dict], reverse_data: Optional[Union[str, dict]] = None)<sup>[source](https://github.com/occipital/django-content-settings/blob/master/content_settings/migrate.py#L12)</sup>

The function that can be used inside your migration file.

Args:
    data (Union[str, dict]): The data to import. Can be either a JSON string or a dictionary.
    reverse_data (Optional[Union[str, dict]], optional): The data to use for reversing the migration.
        Can be either a JSON string or a dictionary. If None, the migration will not be reversible. Defaults to None.

Returns:
    migrations.RunPython: A RunPython operation that can be used in a migration file.

Example:
    In your migration file:

    from content_settings.migrate import RunImport

    class Migration(migrations.Migration):
        dependencies = [
            ('content_settings', '0004_userdefined_preview'),
        ]

        operations = [
            RunImport({
                "settings": {
                    "AFTER_TITLE": {
                        "value": "Best Settings Framework",
                        "version": ""
                    },
                    "ARTIST_LINE": {
                        "value": "",
                        "version": ""
                    },
                    "DAYS_WITHOUT_FAIL": {
                        "value": "5",
                        "version": "
                    },
                    "WEE": {
                        "value": "12",
                        "tags": "",
                        "help": "12",
                        "version": "",
                        "user_defined_type": "text"
                    }
                }
            }),
        ]

Note:
    This function is designed to be used within Django migration files. It handles the import of content settings,
    creating or updating them as necessary. If reverse_data is provided, it also sets up the reverse operation
    for the migration.

### def import_settings(data: Dict[str, Any], model_cs: Type[models.Model], model_cs_history: Optional[Type[models.Model]] = None, user: Optional[User] = None)<sup>[source](https://github.com/occipital/django-content-settings/blob/master/content_settings/migrate.py#L96)</sup>

Import content settings from a dictionary.

Args:
    data (Dict[str, Any]): A dictionary containing the settings to import.
    model_cs (Type[models.Model]): The ContentSetting model class.
    model_cs_history (Optional[Type[models.Model]]): The ContentSettingHistory model class, if history tracking is enabled.
    user (Optional[User]): The user performing the import, if applicable.

Returns:
    None

This function iterates through the settings in the provided data dictionary,
creating or updating ContentSetting objects as necessary. It also handles
history tracking if a history model is provided.


## models



Django Models for the content settings.

### class ContentSetting(models.Model)<sup>[source](https://github.com/occipital/django-content-settings/blob/master/content_settings/models.py#L21)</sup>

The main model for the content settings. Is stores all of the raw values for the content settings.

#### def tags_set(self)<sup>[source](https://github.com/occipital/django-content-settings/blob/master/content_settings/models.py#L59)</sup>

tags field stores tags in a newline separated format. The property returns a set of tags.

### class HistoryContentSetting(models.Model)<sup>[source](https://github.com/occipital/django-content-settings/blob/master/content_settings/models.py#L72)</sup>

The model for the history of the content settings. Is used to store the history of changes for the content settings such as changed/added/removed.

The the generation of the history is done in two steps.
First step is to create a record when the setting is changed.
Second step is to assign other changing parameters such as by_user.

#### def update_last_record_for_name(cls, name: str, user: Optional[User] = None)<sup>[source](https://github.com/occipital/django-content-settings/blob/master/content_settings/models.py#L141)</sup>

Update the last record with the information about the source of the update.

#### def gen_unique_records(cls, name)<sup>[source](https://github.com/occipital/django-content-settings/blob/master/content_settings/models.py#L175)</sup>

The current issue is that sometimes the same setting is changed multiple times in a row.
This method is used to generate unique records for the history.

### class UserTagSetting(models.Model)<sup>[source](https://github.com/occipital/django-content-settings/blob/master/content_settings/models.py#L204)</sup>

User can assign personal tags to the settings for extending tags-filtering functionality.
The model contains those assignees.

The allowed tags to assign in Django Admin panel can be found in `CONTENT_SETTINGS_USER_TAGS` django setting.

### class UserPreview(models.Model)<sup>[source](https://github.com/occipital/django-content-settings/blob/master/content_settings/models.py#L233)</sup>

The user is allowed to preview settings before applying.

The model contains the information of which settings are currently previewing.

#### def add_by_user(cls, user: User, name: str)<sup>[source](https://github.com/occipital/django-content-settings/blob/master/content_settings/models.py#L270)</sup>

Adding the setting to the user's preview settings.

#### def apply(self)<sup>[source](https://github.com/occipital/django-content-settings/blob/master/content_settings/models.py#L301)</sup>

Applying the preview setting into an actual setting.

Works for:
* userdefined settings
* non-userdefined settings
* userdefined preview for non-exist setting

### class UserPreviewHistory(models.Model)<sup>[source](https://github.com/occipital/django-content-settings/blob/master/content_settings/models.py#L343)</sup>

Contains history of the user's preview settings. Because the settings can also change logic, so we want to keep the history of the settings for future investigations.

#### def user_record(cls, preview_setting: UserPreview, status: int = STATUS_CREATED)<sup>[source](https://github.com/occipital/django-content-settings/blob/master/content_settings/models.py#L374)</sup>

Making a record in the history of the user's preview settings.

#### def user_record_by_name(cls, user: User, name: str, value: str, user_defined_type: Optional[str] = None, tags: Optional[str] = None, help: Optional[str] = None, status: int = STATUS_CREATED)<sup>[source](https://github.com/occipital/django-content-settings/blob/master/content_settings/models.py#L389)</sup>

Making a record in the history of the user's preview settings by the name of the setting and the value.


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


## store



the module is used for collecting information.

the `APP_NAME_STORE` a dict `setting_name: app_name` is used to store the name of the app that uses the setting. Which later on can be used in `tags.app_name` to generate a tag with the name of the app.

### def add_app_name(cs_name: str, app_name: str)<sup>[source](https://github.com/occipital/django-content-settings/blob/master/content_settings/store.py#L17)</sup>

add the name of the app that uses the setting.

### def cs_has_app(cs_name: str)<sup>[source](https://github.com/occipital/django-content-settings/blob/master/content_settings/store.py#L24)</sup>

check if the setting has an app name.

### def get_app_name(cs_name: str)<sup>[source](https://github.com/occipital/django-content-settings/blob/master/content_settings/store.py#L31)</sup>

get the name of the app that uses the setting.

### def add_admin_head_css(css_url: str)<sup>[source](https://github.com/occipital/django-content-settings/blob/master/content_settings/store.py#L38)</sup>

add a css url to the admin head.

### def add_admin_head_js(js_url: str)<sup>[source](https://github.com/occipital/django-content-settings/blob/master/content_settings/store.py#L46)</sup>

add a js url to the admin head.

### def add_admin_head_css_raw(css: str)<sup>[source](https://github.com/occipital/django-content-settings/blob/master/content_settings/store.py#L54)</sup>

add a css code to the admin head.

### def add_admin_head_js_raw(js: str)<sup>[source](https://github.com/occipital/django-content-settings/blob/master/content_settings/store.py#L62)</sup>

add a js code to the admin head.

### def add_admin_head(setting: BaseSetting)<sup>[source](https://github.com/occipital/django-content-settings/blob/master/content_settings/store.py#L70)</sup>

add a setting to the admin head.

### def get_admin_head()<sup>[source](https://github.com/occipital/django-content-settings/blob/master/content_settings/store.py#L84)</sup>

get the admin head.

### def get_admin_raw_js()<sup>[source](https://github.com/occipital/django-content-settings/blob/master/content_settings/store.py#L100)</sup>

get the admin raw js.


## tags



the functions that can be used for `CONTENT_SETTINGS_TAGS` and generate tags for the content settings based on setting name, type and value.

### def changed(name: str, cs_type: BaseSetting, value: str)<sup>[source](https://github.com/occipital/django-content-settings/blob/master/content_settings/tags.py#L11)</sup>

returns a tag `changed` if the value of the setting is different from the default value.

the name of the tag can be changed in `CONTENT_SETTINGS_TAG_CHANGED` django setting.

### def app_name(name: str, cs_type: BaseSetting, value: str)<sup>[source](https://github.com/occipital/django-content-settings/blob/master/content_settings/tags.py#L20)</sup>

returns a tag with the name of the app that uses the setting.


## utils



A set of available utilites

### def classes(setting_cls: Type[BaseSetting])<sup>[source](https://github.com/occipital/django-content-settings/blob/master/content_settings/utils.py#L13)</sup>

Returns an iterator of classes that are subclasses of the given class.

### def class_names(setting_cls: Type[BaseSetting])<sup>[source](https://github.com/occipital/django-content-settings/blob/master/content_settings/utils.py#L31)</sup>

Returns an iterator of tuple with module and class name that are subclasses of the given class.

### def import_object(path: str)<sup>[source](https://github.com/occipital/django-content-settings/blob/master/content_settings/utils.py#L39)</sup>

getting an object from the module by the path. `full.path.to.Object` -> `Object`

### def function_has_argument(func: Callable, arg: str)<sup>[source](https://github.com/occipital/django-content-settings/blob/master/content_settings/utils.py#L51)</sup>

Check if the function has the given argument in its definition.

### def is_bline(func: TCallableStr)<sup>[source](https://github.com/occipital/django-content-settings/blob/master/content_settings/utils.py#L58)</sup>

Check if it is a string defined as b"string", or is other words bites string.

The function is part of the future idea https://github.com/occipital/django-content-settings/issues/110

### def obj_base_str(obj: Any, call_base: Any = None)<sup>[source](https://github.com/occipital/django-content-settings/blob/master/content_settings/utils.py#L67)</sup>

if a given obj is not String - return the obj. If it is string than try to find it using call_base

### def call_base_str(func: TCallableStr)<sup>[source](https://github.com/occipital/django-content-settings/blob/master/content_settings/utils.py#L89)</sup>

The goal of the function is to extend interface of callable attributes, so instead of passing a function you can pass a name of the function or full import path to the function.

It is not only minimise the amout of import lines but also allows to use string attributes in `CONTENT_SETTINGS_DEFAULTS`.


## views



Those are the views can be used in the Integration with the Project.

### def gen_startswith(startswith: str)<sup>[source](https://github.com/occipital/django-content-settings/blob/master/content_settings/views.py#L14)</sup>

for names attribute of FetchSettingsView, to find settings by name starts with `startswith`

### def gen_hastag(tag: str)<sup>[source](https://github.com/occipital/django-content-settings/blob/master/content_settings/views.py#L27)</sup>

for names attribute of FetchSettingsView, to find settings by tag

### def gen_all()<sup>[source](https://github.com/occipital/django-content-settings/blob/master/content_settings/views.py#L40)</sup>

for names attribute of FetchSettingsView, to find all settings

### class FetchSettingsView(View)<sup>[source](https://github.com/occipital/django-content-settings/blob/master/content_settings/views.py#L52)</sup>

A View for featching settings from the content settings.

Use attribute `names` to define the names of the settings to fetch.

```
FetchSettingsView.as_view(
    names=[
        "DESCRIPTION",
        "OPEN_DATE",
        "TITLE",
    ]
)
```

Suffix can be used in names

```
FetchSettingsView.as_view(
    names=[
        "TITLE",
        "BOOKS__available_names",
    ]
),
```

function for getting names by specific conditions can be used

```
FetchSettingsView.as_view(names=gen_hastag("general")),
```

or combinations of them

```
FetchSettingsView.as_view(names=(gen_startswith("IS_"), "TITLE")),
```


## widgets



Widgets that can be used in `widget` attribute of the content settings.

It includes all of the widgets from django.forms.widgets + several custom widgets.

### class LongInputMix()<sup>[source](https://github.com/occipital/django-content-settings/blob/master/content_settings/widgets.py#L10)</sup>

Mixin that makes input maximum long

### class LongTextInput(LongInputMix, TextInput)<sup>[source](https://github.com/occipital/django-content-settings/blob/master/content_settings/widgets.py#L23)</sup>

Long text input

### class LongTextarea(LongInputMix, Textarea)<sup>[source](https://github.com/occipital/django-content-settings/blob/master/content_settings/widgets.py#L31)</sup>

Long textarea

### class LongURLInput(LongInputMix, URLInput)<sup>[source](https://github.com/occipital/django-content-settings/blob/master/content_settings/widgets.py#L39)</sup>

Long URL Input

### class LongEmailInput(LongInputMix, EmailInput)<sup>[source](https://github.com/occipital/django-content-settings/blob/master/content_settings/widgets.py#L45)</sup>

Long Email Input


## templatetags.content_settings_extras





### def content_settings_call(name)<sup>[source](https://github.com/occipital/django-content-settings/blob/master/content_settings/templatetags/content_settings_extras.py#L12)</sup>

template tag that call callable settings in the template


## types.array



Types that convert a string into a list of values.

### class SimpleStringsList(SimpleText)<sup>[source](https://github.com/occipital/django-content-settings/blob/master/content_settings/types/array.py#L33)</sup>

    Split a text into a list of strings.

    * comment_starts_with (default: #): if not None, the lines that start with this string are removed
    * filter_empty (default: True): if True, empty lines are removed
    * split_lines (default: 
): the string that separates the lines
    * filters (default: None): a list of additional filters to apply to the lines.
    

#### def get_filters(self)<sup>[source](https://github.com/occipital/django-content-settings/blob/master/content_settings/types/array.py#L58)</sup>

Get the filters based on the current configuration.

* If filters is not None, it is returned.
* If filter_empty is True, f_empty is added to the filters.
* If comment_starts_with is not None, f_comment is added to the filters.

#### def gen_to_python(self, value: str)<sup>[source](https://github.com/occipital/django-content-settings/blob/master/content_settings/types/array.py#L117)</sup>

Converts a string value into a generator of filtered lines.


## types.basic



The most basic types for the content settings. SimpleString is used as the base for all other types.

### class SimpleString(BaseSetting)<sup>[source](https://github.com/occipital/django-content-settings/blob/master/content_settings/types/basic.py#L35)</sup>

A very basic class that returns the string value, the same as a given value.

Basic attributes (TCallableStr - type for attribute that can be either a string and an import line):

- `constant: bool = False`: Whether the setting is constant (can not be changed).
- `cls_field: TCallableStr = "CharField"`: The form field class to use for the setting. For str value class from django.forms.fields is used.
- `widget: TCallableStr = "LongTextInput"`: The form widget to use for the cls_field. For str value class from django.forms.widgets is used.
- `widget_attrs: Optional[dict] = None`: Optional attributes for the widget initiation.
- `fetch_permission: TCallableStr = "none"`: Permission required to fetch the setting in API. For str value function from content_settings.permissions is used
- `update_permission: TCallableStr = "staff"`: Optional permission required to update  the setting in Django Admin. For str value function from content_settings.permissions is used
- `view_permission: TCallableStr = "staff"`: Optional permission required to view the setting in Django Admin. For str value function from content_settings.permissions is used
- `view_history_permission: Optional[TCallableStr]`: Optional permission required to see the hisotry of changes. `None` means the permission is taken from `view_permission`. For str value function from content_settings.permissions is used
- `help: Optional[str] = ""`: Optional help text for the setting.
- `value_required: bool = False`: Whether a value is required for the setting.
- `version: str = ""`: The version of the setting (using for caching).
- `tags: Optional[Iterable[str]] = None`: Optional tags associated with the setting.
- `validators: Tuple[TCallableStr] = ()`: Validators to apply to the setting value.
- `validators_raw: Tuple[TCallableStr] = ()`: Validators to apply to the text value of the setting.
- `admin_preview_as: PREVIEW = PREVIEW.NONE`: The format to use for the admin preview.

Advanced attributes - rarely used:

- `help_format: Optional[str] = "string"`: Optional format string for the help text for the format (align to the type).
- `suffixes: Optional[Dict[str, TCallableStr]] = None`: Suffixes that can be appended to the setting value.
- `user_defined_slug: Optional[str] = None`: it contains a slug from db If the setting is defined in DB only (should not be set in content_settings)
- `overwrite_user_defined: bool = False`: Whether the setting can overwrite a user defined setting.
- `default: Union[str, required, optional] = ""`: The default value for the setting.
- `on_change: Tuple[TCallableStr] = ()`: list of functions to call when the setting is changed
- `on_change_commited: Tuple[TCallableStr] = ()`: list of functions to call when the setting is changed and commited
- `admin_head_css: Tuple[str] = ()`: list of css urls to include in the admin head
- `admin_head_js: Tuple[str] = ()`: list of js urls to include in the admin head
- `admin_head_css_raw: Tuple[str] = ()`: list of css codes to include in the admin head
- `admin_head_js_raw: Tuple[str] = ()`: list of js codes to include in the admin head

#### def __init__(self, default: Optional[Union[str, required, optional]] = None)<sup>[source](https://github.com/occipital/django-content-settings/blob/master/content_settings/types/basic.py#L100)</sup>

The init function accepts initial attributes for the content setting type.
It can assing any attribute that is defined in the class. (The exception is help_text instead of help)

All of the changes for type instance can only be done inside of __init__ method. The other methods should not change self object.

#### def init_assign_kwargs(self, kwargs)<sup>[source](https://github.com/occipital/django-content-settings/blob/master/content_settings/types/basic.py#L136)</sup>

Assign the attributes from the kwargs to the instance.

Use init__{attribute_name} method if it exists, otherwise use setattr

#### def init__tags(self, tags: Union[None, str, Iterable[str]])<sup>[source](https://github.com/occipital/django-content-settings/blob/master/content_settings/types/basic.py#L150)</sup>

Assign the tags to the instance from kwargs.

#### def get_admin_head_css(self)<sup>[source](https://github.com/occipital/django-content-settings/blob/master/content_settings/types/basic.py#L164)</sup>

Return the list of css urls to include in the admin head.

#### def get_admin_head_js(self)<sup>[source](https://github.com/occipital/django-content-settings/blob/master/content_settings/types/basic.py#L170)</sup>

Return the list of js urls to include in the admin head.

#### def get_admin_head_css_raw(self)<sup>[source](https://github.com/occipital/django-content-settings/blob/master/content_settings/types/basic.py#L176)</sup>

Return the list of css codes to include in the admin head.

#### def get_admin_head_js_raw(self)<sup>[source](https://github.com/occipital/django-content-settings/blob/master/content_settings/types/basic.py#L182)</sup>

Return the list of js codes to include in the admin head.

#### def can_view(self, user: User)<sup>[source](https://github.com/occipital/django-content-settings/blob/master/content_settings/types/basic.py#L188)</sup>

Return True if the user has permission to view the setting in the django admin panel.

Use view_permission attribute

#### def can_view_history(self, user: User)<sup>[source](https://github.com/occipital/django-content-settings/blob/master/content_settings/types/basic.py#L198)</sup>

Return True if the user has permission to view the setting changing history in the django admin panel.

Use view_history_permission attribute, but if it is None, use can_view

#### def can_update(self, user: User)<sup>[source](https://github.com/occipital/django-content-settings/blob/master/content_settings/types/basic.py#L214)</sup>

Return True if the user has permission to update the setting in the django admin panel.

Use update_permission attribute

#### def can_fetch(self, user: User)<sup>[source](https://github.com/occipital/django-content-settings/blob/master/content_settings/types/basic.py#L224)</sup>

Return True if the user has permission to fetch the setting value using API.

Use fetch_permission attribute

#### def get_admin_preview_as(self)<sup>[source](https://github.com/occipital/django-content-settings/blob/master/content_settings/types/basic.py#L234)</sup>

Return the format (PREVIEW Enum) to use for the admin preview.

Use admin_preview_as attribute

#### def get_on_change(self)<sup>[source](https://github.com/occipital/django-content-settings/blob/master/content_settings/types/basic.py#L242)</sup>

Return the list of functions to call when the setting is changed.

Use on_change attribute

#### def get_on_change_commited(self)<sup>[source](https://github.com/occipital/django-content-settings/blob/master/content_settings/types/basic.py#L250)</sup>

Return the list of functions to call when the setting is changed and commited.
Uses for syncing data or triggering emails.

Use on_change_commited attribute–

#### def get_suffixes(self, value: Any)<sup>[source](https://github.com/occipital/django-content-settings/blob/master/content_settings/types/basic.py#L259)</sup>

Return the list of suffixes that can be used

#### def get_suffixes_names(self, value: Any)<sup>[source](https://github.com/occipital/django-content-settings/blob/master/content_settings/types/basic.py#L265)</sup>

Return the tuple of suffixes that can be used

#### def can_suffix(self, suffix: Optional[str], value: Any)<sup>[source](https://github.com/occipital/django-content-settings/blob/master/content_settings/types/basic.py#L271)</sup>

Return True if the suffix is valid for the setting.

#### def can_assign(self, name: str)<sup>[source](https://github.com/occipital/django-content-settings/blob/master/content_settings/types/basic.py#L277)</sup>

Return True if the attribute can be assigned to the instance.

#### def get_help_format(self)<sup>[source](https://github.com/occipital/django-content-settings/blob/master/content_settings/types/basic.py#L289)</sup>

Generate help for the specific type.

The help of the format goes after the help for the specific setting and expalins the format of the setting.

#### def get_help(self)<sup>[source](https://github.com/occipital/django-content-settings/blob/master/content_settings/types/basic.py#L297)</sup>

Generate help for the specific setting (includes format help)

#### def get_tags(self)<sup>[source](https://github.com/occipital/django-content-settings/blob/master/content_settings/types/basic.py#L309)</sup>

Return the tags associated with the setting.

#### def get_content_tags(self, name: str, value: str)<sup>[source](https://github.com/occipital/django-content-settings/blob/master/content_settings/types/basic.py#L318)</sup>

Generate tags based on current type and value.

Uses CONTENT_SETTINGS_TAGS for generating, but overriding the method allows you to change the behavior for the specific type.

#### def get_validators(self)<sup>[source](https://github.com/occipital/django-content-settings/blob/master/content_settings/types/basic.py#L328)</sup>

Return the list of validators to apply to the setting python value.

#### def get_validators_raw(self)<sup>[source](https://github.com/occipital/django-content-settings/blob/master/content_settings/types/basic.py#L334)</sup>

Return the list of validators to apply to the setting text value.

#### def get_field(self)<sup>[source](https://github.com/occipital/django-content-settings/blob/master/content_settings/types/basic.py#L344)</sup>

Generate the form field for the setting. Which will be used in the django admin panel.

#### def get_widget(self)<sup>[source](https://github.com/occipital/django-content-settings/blob/master/content_settings/types/basic.py#L356)</sup>

Generate the form widget for the setting. Which will be used in the django admin panel.

#### def validate_raw_value(self, value: str)<sup>[source](https://github.com/occipital/django-content-settings/blob/master/content_settings/types/basic.py#L368)</sup>

Validate the text value of the setting.
In the validation you only need to make sure the value is possible to be converted into py object.

#### def validate_value(self, value: str)<sup>[source](https://github.com/occipital/django-content-settings/blob/master/content_settings/types/basic.py#L381)</sup>

Full validation of the setting text value.

#### def validate(self, value: Any)<sup>[source](https://github.com/occipital/django-content-settings/blob/master/content_settings/types/basic.py#L389)</sup>

Validate py object. Validate consistency of the object with the project.

#### def to_python(self, value: str)<sup>[source](https://github.com/occipital/django-content-settings/blob/master/content_settings/types/basic.py#L398)</sup>

Converts text value to python value.

#### def json_view_value(self, value: Any)<sup>[source](https://github.com/occipital/django-content-settings/blob/master/content_settings/types/basic.py#L404)</sup>

Converts the setting value to JSON.

#### def give_python_to_admin(self, value: str, name: str)<sup>[source](https://github.com/occipital/django-content-settings/blob/master/content_settings/types/basic.py#L410)</sup>

Converts the setting text value to setting admin value that will be used for rendering admin preview.

By default it uses to_python method, but it make sense to override it for some types, for example callable types,
where you want to show the result of the call in the preview.

#### def get_admin_preview_html(self, value: Any, name: str)<sup>[source](https://github.com/occipital/django-content-settings/blob/master/content_settings/types/basic.py#L419)</sup>

Generate the admin preview for PREVIEW.HTML format.

#### def get_admin_preview_text(self, value: Any, name: str)<sup>[source](https://github.com/occipital/django-content-settings/blob/master/content_settings/types/basic.py#L425)</sup>

Generate the admin preview for PREVIEW.TEXT format.

#### def get_admin_preview_python(self, value: Any, name: str)<sup>[source](https://github.com/occipital/django-content-settings/blob/master/content_settings/types/basic.py#L431)</sup>

Generate the admin preview for PREVIEW.PYTHON format.

#### def get_admin_preview_value(self, value: str)<sup>[source](https://github.com/occipital/django-content-settings/blob/master/content_settings/types/basic.py#L437)</sup>

Generate the admin preview for the setting based on the admin_preview_as attribute (or get_admin_preview_as method).

Using text value of the setting.

#### def get_full_admin_preview_value(self, value: str)<sup>[source](https://github.com/occipital/django-content-settings/blob/master/content_settings/types/basic.py#L450)</sup>

Generate data for json response for preview

#### def get_admin_preview_object(self, value: Any, name: str)<sup>[source](https://github.com/occipital/django-content-settings/blob/master/content_settings/types/basic.py#L465)</sup>

Generate the admin preview for the setting based on the admin_preview_as attribute (or get_admin_preview_as method).

Using admin value of the setting.

#### def lazy_give(self, l_func: Callable, suffix = None)<sup>[source](https://github.com/occipital/django-content-settings/blob/master/content_settings/types/basic.py#L481)</sup>

Return the LazyObject that will be used for the setting value.

This value will be returned using lazy prefix in the content_settings.

#### def give(self, value: Any, suffix: Optional[str] = None)<sup>[source](https://github.com/occipital/django-content-settings/blob/master/content_settings/types/basic.py#L489)</sup>

The will be returned as the content_settings attribute using python value of the setting.

Suffix can be used.

### class SimpleText(SimpleString)<sup>[source](https://github.com/occipital/django-content-settings/blob/master/content_settings/types/basic.py#L507)</sup>

Multiline text setting type.

### class SimpleTextPreview(SimpleText)<sup>[source](https://github.com/occipital/django-content-settings/blob/master/content_settings/types/basic.py#L515)</sup>

Multiline text setting type with preview. By default SimpleText and SimpleString don't have preview, but for showing preview in EachMixin, we need to have preview for each type.

### class SimpleHTML(HTMLMixin, SimpleText)<sup>[source](https://github.com/occipital/django-content-settings/blob/master/content_settings/types/basic.py#L523)</sup>

Multiline HTML setting type.

### class URLString(EmptyNoneMixin, SimpleString)<sup>[source](https://github.com/occipital/django-content-settings/blob/master/content_settings/types/basic.py#L531)</sup>

URL setting type.

### class EmailString(EmptyNoneMixin, SimpleString)<sup>[source](https://github.com/occipital/django-content-settings/blob/master/content_settings/types/basic.py#L544)</sup>

Email setting type.

### class SimpleInt(SimpleString)<sup>[source](https://github.com/occipital/django-content-settings/blob/master/content_settings/types/basic.py#L557)</sup>

Integer setting type.

### class SimpleBool(SimpleString)<sup>[source](https://github.com/occipital/django-content-settings/blob/master/content_settings/types/basic.py#L571)</sup>

Boolean setting type.

Attributes:
- yeses (Tuple[str]): Accepted values for True.
- noes (Tuple[str]): Accepted values for False.

### class SimpleDecimal(SimpleString)<sup>[source](https://github.com/occipital/django-content-settings/blob/master/content_settings/types/basic.py#L611)</sup>

Decimal setting type.

Attributes:
- decimal_json_as_string (bool): set False if you want to return the decimal as a float in the JSON view.

### class SimplePassword(SimpleString)<sup>[source](https://github.com/occipital/django-content-settings/blob/master/content_settings/types/basic.py#L629)</sup>

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

### class SimpleTimedelta(EmptyNoneMixin, SimpleString)<sup>[source](https://github.com/occipital/django-content-settings/blob/master/content_settings/types/datetime.py#L160)</sup>

Converts into a timedelta object.


## types.each



EachMixin is the main mixin of the module, which allows types to have subtypes, that check, preview and converts the structure of the value.

For example `array.TypedStringsList`

### class Item(BaseEach)<sup>[source](https://github.com/occipital/django-content-settings/blob/master/content_settings/types/each.py#L73)</sup>

Converts each element of the array into a specific type `cs_type`

### class Keys(BaseEach)<sup>[source](https://github.com/occipital/django-content-settings/blob/master/content_settings/types/each.py#L144)</sup>

Converts values of the specific keys into specific types `cs_types`

### class Values(BaseEach)<sup>[source](https://github.com/occipital/django-content-settings/blob/master/content_settings/types/each.py#L245)</sup>

Converts each value of the given dict into `cs_type`

### class EachMixin()<sup>[source](https://github.com/occipital/django-content-settings/blob/master/content_settings/types/each.py#L317)</sup>

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





### def mix()<sup>[source](https://github.com/occipital/django-content-settings/blob/master/content_settings/types/mixins.py#L16)</sup>

Returns a mix of types. Mixins should go first and the last one should be the main type.

Example:
mix(HTMLMixin, SimpleInt)

### class ProcessorsMixin()<sup>[source](https://github.com/occipital/django-content-settings/blob/master/content_settings/types/mixins.py#L26)</sup>

Mixin that adds processors to the type.

The processors is a pipeline of functions that are applied to the py object.

### class GiveProcessorsMixin()<sup>[source](https://github.com/occipital/django-content-settings/blob/master/content_settings/types/mixins.py#L45)</sup>

Mixin that adds processors to the type.

### class MinMaxValidationMixin()<sup>[source](https://github.com/occipital/django-content-settings/blob/master/content_settings/types/mixins.py#L73)</sup>

Mixin that validates that value is between min_value and max_value.

Attributes:
min_value: Minimum value. If None, then no minimum value.
max_value: Maximum value. If None, then no maximum value.

### class EmptyNoneMixin()<sup>[source](https://github.com/occipital/django-content-settings/blob/master/content_settings/types/mixins.py#L114)</sup>

Mixin for types that returns None if value is empty string.

Works only for `value_required=False`

### class HTMLMixin()<sup>[source](https://github.com/occipital/django-content-settings/blob/master/content_settings/types/mixins.py#L132)</sup>

Mixin for types that should be displayed in HTML format.
And also returned content should be marked as safe.

### class PositiveValidationMixin(MinMaxValidationMixin)<sup>[source](https://github.com/occipital/django-content-settings/blob/master/content_settings/types/mixins.py#L149)</sup>

Mixin that validates that value is positive.

### class CallToPythonMixin()<sup>[source](https://github.com/occipital/django-content-settings/blob/master/content_settings/types/mixins.py#L157)</sup>

Mixin for callable types, or types that should be called to get the value.

### class GiveCallMixin()<sup>[source](https://github.com/occipital/django-content-settings/blob/master/content_settings/types/mixins.py#L264)</sup>

Mixin for callable types, but result of the call without artuments should be returned.

If suffix is "call" then callable should be returned.

### class MakeCallMixin()<sup>[source](https://github.com/occipital/django-content-settings/blob/master/content_settings/types/mixins.py#L291)</sup>

Mixin for non-callable python objects will be returned as callable given.

Can be usefull when you change callable types to a simple type but don't want to change the code that uses that type.

### class AdminPreviewMenuMixin()<sup>[source](https://github.com/occipital/django-content-settings/blob/master/content_settings/types/mixins.py#L308)</sup>

Mixin that adds a menu to the admin preview.

### class AdminPreviewSuffixesMixin(AdminSuffixesMixinPreview, AdminPreviewMenuMixin)<sup>[source](https://github.com/occipital/django-content-settings/blob/master/content_settings/types/mixins.py#L379)</sup>

Mixin shows links to preview different suffixes of the value in the admin preview.

### class AdminActionsMixinPreview()<sup>[source](https://github.com/occipital/django-content-settings/blob/master/content_settings/types/mixins.py#L409)</sup>

Mixin that adds actions to the admin preview.


## types.template



One of the most complicated module contains callable types. The Python object for those types usually needs to be called.

The complexity of the module also illustrates the flexibility of types.

The module is called a "template" because the setting's raw value is a template that will be used to generate a real value.

See `CallToPythonMixin`

### class StaticDataMixin()<sup>[source](https://github.com/occipital/django-content-settings/blob/master/content_settings/types/template.py#L54)</sup>

Adds static data to the context, such as SETTINGS or/and CONTENT_SETTINGS.

Attributes:

- `template_static_includes` - tuple of `STATIC_INCLUDES` that should be included in the context. Default: `(STATIC_INCLUDES.CONTENT_SETTINGS, STATIC_INCLUDES.SETTINGS)`. If `STATIC_INCLUDES.SETTINGS` is included, `django.conf.settings` will be added to the context. If `STATIC_INCLUDES.CONTENT_SETTINGS` is included, `content_settings.conf.content_settings` will be added to the context.
- `template_static_data` - static data that should be added to the context (on top of what will be added by `template_static_includes`). It can be a dictionary or a callable that returns a dictionary. Default: `None`.

### class SimpleCallTemplate(CallToPythonMixin, StaticDataMixin, SimpleText)<sup>[source](https://github.com/occipital/django-content-settings/blob/master/content_settings/types/template.py#L100)</sup>

Base class for templates that can be called.

#### def prepate_input_to_dict(self)<sup>[source](https://github.com/occipital/django-content-settings/blob/master/content_settings/types/template.py#L147)</sup>

prepares an inpit dictuonary for the call based on the given arguments and kwargs

### class DjangoTemplate(SimpleCallTemplate)<sup>[source](https://github.com/occipital/django-content-settings/blob/master/content_settings/types/template.py#L173)</sup>

The setting of that type generates value based on the Django Template in the raw value.

### class DjangoTemplateHTML(HTMLMixin, DjangoTemplate)<sup>[source](https://github.com/occipital/django-content-settings/blob/master/content_settings/types/template.py#L209)</sup>

Same as `DjangoTemplate` but the rendered value is marked as safe.

### class DjangoTemplateNoArgs(GiveCallMixin, DjangoTemplate)<sup>[source](https://github.com/occipital/django-content-settings/blob/master/content_settings/types/template.py#L217)</sup>

Same as `DjangoTemplate` but the setting value is not callablle, but already rendered value.

### class DjangoTemplateNoArgsHTML(HTMLMixin, DjangoTemplateNoArgs)<sup>[source](https://github.com/occipital/django-content-settings/blob/master/content_settings/types/template.py#L225)</sup>

Same as `DjangoTemplateNoArgs` but the rendered value is marked as safe.

### class DjangoModelTemplateMixin()<sup>[source](https://github.com/occipital/django-content-settings/blob/master/content_settings/types/template.py#L233)</sup>

Mixing that uses one argument for the template from the model queryset.

Attributes:

- `template_model_queryset` - QuerySet or a callable that returns a Model Object. For QuerySet, the first object will be used. For callable, the object returned by the callable will be used. The generated object will be used as validator and for preview.
- `template_object_name` - name of the object in the template. Default: "object".

#### def get_first_call_validator(self)<sup>[source](https://github.com/occipital/django-content-settings/blob/master/content_settings/types/template.py#L252)</sup>

generates the first validator based of template_model_queryset, which will be used for validation and for preview.

### class DjangoModelTemplate(DjangoModelTemplateMixin, DjangoTemplate)<sup>[source](https://github.com/occipital/django-content-settings/blob/master/content_settings/types/template.py#L278)</sup>

Django Template that uses one argument as a model object.

### class DjangoModelTemplateHTML(DjangoModelTemplate)<sup>[source](https://github.com/occipital/django-content-settings/blob/master/content_settings/types/template.py#L286)</sup>

Same as `DjangoModelTemplate` but the rendered value is marked as safe.

### class SimpleEval(SimpleCallTemplate)<sup>[source](https://github.com/occipital/django-content-settings/blob/master/content_settings/types/template.py#L298)</sup>

Template that evaluates the Python code (using `eval` function).

### class DjangoModelEval(DjangoModelTemplateMixin, SimpleEval)<sup>[source](https://github.com/occipital/django-content-settings/blob/master/content_settings/types/template.py#L329)</sup>

Same as `SimpleEval` but uses one value as a model object.

### class SimpleEvalNoArgs(GiveCallMixin, SimpleEval)<sup>[source](https://github.com/occipital/django-content-settings/blob/master/content_settings/types/template.py#L337)</sup>

Same as `SimpleEval` but the setting value is not callable, but already evaluated.

### class SystemExec()<sup>[source](https://github.com/occipital/django-content-settings/blob/master/content_settings/types/template.py#L345)</sup>

Mixin class that brings exec functionality into type

Attributes:

- `template_return` - dictates what will be returned as a setting value.
    - If `None`, the whole context will be returned. The default value.
    - if a string, the string will be used as a key from the context and that value will be returned.
    - If a dictionary, only the keys from the dictionary will be returned. The values will be used as defaults.
    - If a callable, the callable will be called and the return value will be used as a dictionary.
    - If an iterable, the iterable will be used as keys for the return dictionary. The values will be `None` by default.
- `template_bultins` - allows to limit the builtin functions. By default it is `"BUILTINS_SAFE"`, which allows all functions except `memoryview`, `open`, `input` and `import`. If you want to include import use `"BUILTINS_ALLOW_IMPORT"`, if you don't want to use any limitation - just assign `None` to the attribute.
- `template_raise_return_error` - raises an error if `template_return` doesn't match the context. Default: `False`.

### class SimpleExec(SystemExec, SimpleCallTemplate)<sup>[source](https://github.com/occipital/django-content-settings/blob/master/content_settings/types/template.py#L434)</sup>

Template that executes the Python code (using `exec` function).

### class SimpleExecNoArgs(GiveCallMixin, SimpleExec)<sup>[source](https://github.com/occipital/django-content-settings/blob/master/content_settings/types/template.py#L459)</sup>

Same as `SimpleExec` but the setting value is not callable, but already executed.

### class DjangoModelExec(DjangoModelTemplateMixin, SimpleExec)<sup>[source](https://github.com/occipital/django-content-settings/blob/master/content_settings/types/template.py#L467)</sup>

Same as `SimpleExec` but uses one value as a model object.

### class SimpleExecNoCompile(SystemExec, StaticDataMixin, SimpleText)<sup>[source](https://github.com/occipital/django-content-settings/blob/master/content_settings/types/template.py#L475)</sup>

It is not a Template, probably closed to markdown module, as it simply takes the text value and convert it into py object, which is not a compiled code but the result of execution of the code.

But it is in the template module as it is very similar to `SimpleExecNoArgs`.

It is super easy to shot in the foot with this class so be very cautious.


## types.validators



A list of functions that are used as values for validators attribute of a type.

### class PreviewValidator()<sup>[source](https://github.com/occipital/django-content-settings/blob/master/content_settings/types/validators.py#L14)</sup>

return instance of the class from the validator to show the result of validation

### class PreviewValidationError(ValidationError)<sup>[source](https://github.com/occipital/django-content-settings/blob/master/content_settings/types/validators.py#L24)</sup>

use class instead of ValidatorError to show the input arguments that cause the ValidationError

### class call_validator()<sup>[source](https://github.com/occipital/django-content-settings/blob/master/content_settings/types/validators.py#L34)</sup>

create a valiator that calls the function with the given args and kwargs.

### class result_validator(call_validator)<sup>[source](https://github.com/occipital/django-content-settings/blob/master/content_settings/types/validators.py#L69)</sup>

Not only call the function, but also validate the result of the call.

takes two new arguments:

* function that validates the result of the call
* error message that will be shown if the function returns False

### class gen_call_validator(call_validator)<sup>[source](https://github.com/occipital/django-content-settings/blob/master/content_settings/types/validators.py#L91)</sup>

Same as call_validator, but the args and kwargs are generated by a given function.

Create a valiator that calls the function that generates the args and kwargs, that will be used for the call.

The function will be regenerated every time when the validator is called.

The reason of having one is when you are not able to get possible args at the time of the creation of the validator.

### class gen_args_call_validator(gen_call_validator)<sup>[source](https://github.com/occipital/django-content-settings/blob/master/content_settings/types/validators.py#L138)</sup>

Same as gen_call_validator, but only generates the list for args.

### class gen_signle_arg_call_validator(gen_call_validator)<sup>[source](https://github.com/occipital/django-content-settings/blob/master/content_settings/types/validators.py#L147)</sup>

Same as gen_call_validator, but only generates one arg.

### class gen_kwargs_call_validator(gen_call_validator)<sup>[source](https://github.com/occipital/django-content-settings/blob/master/content_settings/types/validators.py#L156)</sup>

Same as gen_call_validator, but only generates the dict for kwargs.


## defaults.collections



defaults collections for using in `CONTENT_SETTINGS_DEFAULTS`.

For example:

```python
CONTENT_SETTINGS_DEFAULTS = [
    codemirror_python(),
    codemirror_json(),
]
```

Or:

```python
CONTENT_SETTINGS_DEFAULTS = [
    *codemirror_all(),
]
```

### def codemirror_python(path: str = DEFAULT_CODEMIRROR_PATH, class_attr: str = 'codemirror_python')<sup>[source](https://github.com/occipital/django-content-settings/blob/master/content_settings/defaults/collections.py#L48)</sup>

Replace Textarea with CodeMirror for python code for SimpleEval and SimpleExec.

### def codemirror_json(path: str = DEFAULT_CODEMIRROR_PATH, class_attr: str = 'codemirror_json')<sup>[source](https://github.com/occipital/django-content-settings/blob/master/content_settings/defaults/collections.py#L72)</sup>

Replace Textarea with CodeMirror for json code for SimpleJSON.

### def codemirror_yaml(path: str = DEFAULT_CODEMIRROR_PATH, class_attr: str = 'codemirror_yaml')<sup>[source](https://github.com/occipital/django-content-settings/blob/master/content_settings/defaults/collections.py#L92)</sup>

Replace Textarea with CodeMirror for yaml code for SimpleYAML.

### def codemirror_all(path: str = DEFAULT_CODEMIRROR_PATH, class_attr_prefix: str = 'codemirror_')<sup>[source](https://github.com/occipital/django-content-settings/blob/master/content_settings/defaults/collections.py#L112)</sup>

Replace Textarea with CodeMirror for python, json and yaml code.


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
    * **kwargs: Arbitrary keyword arguments representing key-value pairs to unite.
    _use_type_kwargs: (default True) A boolean indicating whether to use type kwargs.
    _empty_not_set: (default False) A boolean indicating whether empty value should be removed from updates.

#### def __call__(self, type_kwargs: Dict[str, Any], updates: Dict[str, Any], kwargs: Dict[str, Any])<sup>[source](https://github.com/occipital/django-content-settings/blob/master/content_settings/defaults/modifiers.py#L58)</sup>

Unites the provided updates and kwargs dictionaries with the parameters.

Args:
    type_kwargs: The default kwargs of the settings type.
    updates: The dictionary with already collected kwargs from default context.
    kwargs: The kwargs passed in the definition of the settings type.

Returns:
    A dictionary with united key-value pairs.

#### def process(self, value: Any, tw: Any, up: Any, kw: Any)<sup>[source](https://github.com/occipital/django-content-settings/blob/master/content_settings/defaults/modifiers.py#L96)</sup>

Returns value for the update dictionary.

Args:
    value: The value from the parameter of the modifier.
    tw: The current value in the type kwargs.
    up: The current value in the update dictionary.
    kw: The current value in the settings kwargs.

Returns:
    The processed value to be set in the update dictionary.

### class unite_set_add(unite)<sup>[source](https://github.com/occipital/django-content-settings/blob/master/content_settings/defaults/modifiers.py#L112)</sup>

unite that modifies a set by adding new values in it.

### class unite_set_remove(unite)<sup>[source](https://github.com/occipital/django-content-settings/blob/master/content_settings/defaults/modifiers.py#L132)</sup>

unite that modifies a set by removing given values.

### class unite_tuple_add(unite)<sup>[source](https://github.com/occipital/django-content-settings/blob/master/content_settings/defaults/modifiers.py#L153)</sup>

unite that modifies a tuple by adding new values in it.

### class unite_dict_update(unite)<sup>[source](https://github.com/occipital/django-content-settings/blob/master/content_settings/defaults/modifiers.py#L178)</sup>

unite that modifies a dictionary by updating it with new values.

### def add_tags(tags: Iterable[str])<sup>[source](https://github.com/occipital/django-content-settings/blob/master/content_settings/defaults/modifiers.py#L198)</sup>

add tags to the setting

### def remove_tags(tags: Iterable[str])<sup>[source](https://github.com/occipital/django-content-settings/blob/master/content_settings/defaults/modifiers.py#L205)</sup>

Removes tags from the update context.

### def add_tag(tag: str)<sup>[source](https://github.com/occipital/django-content-settings/blob/master/content_settings/defaults/modifiers.py#L212)</sup>

same as `add_tags` but only one.

### def remove_tag(tag: str)<sup>[source](https://github.com/occipital/django-content-settings/blob/master/content_settings/defaults/modifiers.py#L219)</sup>

same as `remove_tags` but only one.

### class unite_str(unite)<sup>[source](https://github.com/occipital/django-content-settings/blob/master/content_settings/defaults/modifiers.py#L226)</sup>

unite that modifies a string by formatting it.

Args:
    _format: A string to format the value use `{new_value}` as a placeholder for the passed value in kwargs and `{old_value}` as a placeholder for the value in the update context.
    **kwargs: Arbitrary keyword arguments.

### def help_prefix(prefix: str)<sup>[source](https://github.com/occipital/django-content-settings/blob/master/content_settings/defaults/modifiers.py#L256)</sup>

add prefix to help

### def help_suffix(suffix: str)<sup>[source](https://github.com/occipital/django-content-settings/blob/master/content_settings/defaults/modifiers.py#L263)</sup>

add suffix to help

### def add_admin_head(css: Iterable[str] = (), js: Iterable[str] = (), css_raw: Iterable[str] = (), js_raw: Iterable[str] = ())<sup>[source](https://github.com/occipital/django-content-settings/blob/master/content_settings/defaults/modifiers.py#L270)</sup>

add css and js to the admin head

* css -> admin_head_css
* js -> admin_head_js
* css_raw -> admin_head_css_raw
* js_raw -> admin_head_js_raw

### class add_widget_class(unite_dict_update)<sup>[source](https://github.com/occipital/django-content-settings/blob/master/content_settings/defaults/modifiers.py#L292)</sup>

add widget class or classes splited by space.

### def update_widget_attrs()<sup>[source](https://github.com/occipital/django-content-settings/blob/master/content_settings/defaults/modifiers.py#L332)</sup>

update widget attrs

[![Stand With Ukraine](https://raw.githubusercontent.com/vshymanskyy/StandWithUkraine/main/banner-direct-single.svg)](https://stand-with-ukraine.pp.ua)

