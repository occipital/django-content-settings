# Available Settings

## Overview

The `content_settings.settings.py` module in the `django-content-settings` package provides a variety of settings to customize the functionality of the module. This guide provides a comprehensive overview of these settings.

---

## Caching

For detailed information about caching, see the [dedicated section](caching.md).

### `CONTENT_SETTINGS_CACHE_TRIGGER`

**Default**: `"content_settings.cache_triggers.VersionChecksum"`

Specifies the trigger class and configuration for caching.

#### Example as a String:

```
CONTENT_SETTINGS_CACHE_TRIGGER = "content_settings.cache_triggers.VersionChecksum"
```

#### Example as a Dictionary:

```python
CONTENT_SETTINGS_CACHE_TRIGGER = {
    "backend": "content_settings.cache_triggers.VersionChecksum",
    "cache_timeout": 100000,
}
```

Additional keys (besides `"backend"`) vary depending on the backend. [Read more in the caching section](caching.md).

---

## Admin Panel

For more details on admin panel functionalities, refer to the [dedicated section](ui.md).

### `CONTENT_SETTINGS_USER_TAGS`

Allows admins to assign custom tags to variables through the Django Admin. This is a dictionary where keys are tag names, and values are tuples of two elements: the display for the tag when added, and its display when it can be added.

#### Default:

```python
{
    "favorites": ("⭐", "⚝"),
    "marked": ("💚", "♡"),
}
```

### `CONTENT_SETTINGS_ADMIN_CHECKSUM_CHECK_BEFORE_SAVE`

**Default**: `False`

Checks the current checksum before saving data in Django Admin. If the page has been open too long and settings are changed by another user, the changes will not be applied.

### `CONTENT_SETTINGS_CHAIN_VALIDATE`

**Default**: `True`

Validates settings that depend on each other (e.g., through template types or validations) before applying a new value.

### `CONTENT_SETTINGS_UI_DOC_URL`

**Default**: `"https://django-content-settings.readthedocs.io/en/0.25/ui/"`

Specifies the link to the UI documentation for Django Content Settings, shown in the Django Admin panel. If set to `None`, the link will not appear.

### `CONTENT_SETTINGS_USER_DEFINED_TYPES`

**Default**: `[]`

An empty list prevents users from creating custom user-defined settings. To enable this functionality, provide a list of tuples:

```python
CONTENT_SETTINGS_USER_DEFINED_TYPES = [
    ("text", "content_settings.types.basic.SimpleText", "Simple Text"),
    ("html", "content_settings.types.basic.SimpleHTML", "HTML"),
]
```

Each tuple includes:
1. **Slug**: Internal identifier (e.g., `"text"`).
2. **Import Line**: The type class to use (e.g., `"content_settings.types.basic.SimpleText"`).
3. **Name**: The display name for the dropdown in the form (e.g., `"Simple Text"`).

### `CONTENT_SETTINGS_PREVIEW_ON_SITE_SHOW`

**Default**: `True`

Enables the preview-on-site functionality. If set to `False`, the middleware `content_settings.middlewares.preview_on_site` is ignored, and preview checkboxes are hidden.

### `CONTENT_SETTINGS_PREVIEW_ON_SITE_HREF`

**Default**: `"/"`

Specifies the href attribute for the "View On Site" link in the preview panel.

---

## Integration

### `CONTENT_SETTINGS_CHECK_UPDATE_CELERY`

**Default**: `True`

If Celery is available, the system checks for updates before every `task_prerun`.

### `CONTENT_SETTINGS_CHECK_UPDATE_HUEY`

**Default**: `True`

If Huey is available, the system checks for updates before every `pre_execute`.

---

## Other

### `CONTENT_SETTINGS_VALUES_ONLY_FROM_DB`

**Default**: `False`

Restricts values to be sourced only from the database. If a value is missing in the database, an `AssertionError` will be raised. If `DEBUG=True` the setting is ignored and always `False`

### `CONTENT_SETTINGS_VALIDATE_DEFAULT_VALUE`

**Default**: `settings.DEBUG`

Validates both database values and default values during app launch or reload.

### `CONTENT_SETTINGS_DEFAULTS`

**Default**: `[]`

Defines global default contexts for specific types. Each tuple in the list contains:
1. **Filter**: Determines which settings types are eligible for the global context. (Available filters are in `content_settings.filters`.)
2. **Modifiers**: Change default arguments. (Available modifiers are in `content_settings.defaults.modifiers`.)

#### Example:

```python
from content_settings.permissions import superuser
from content_settings.functools import _or
from content_settings.filters import full_name_exact
from content_settings.defaults.modifiers import set_if_missing

CONTENT_SETTINGS_DEFAULTS = [
    (_or(
        full_name_exact("content_settings.types.template.SimpleEval"),
        full_name_exact("content_settings.types.template.SimpleExec"),
    ), set_if_missing(update_permission=superuser)),
]
```

[Learn more about defaults contexts here](defaults.md#global-updates-content_settings_defaults).

### `CONTENT_SETTINGS_TAGS`

**Default**: `[]`

Defines automatically generated tags for all settings. This is a list of functions (or their import paths) that take three arguments: the setting name, setting object, and new value.

#### Built-in Generated Tags:

- `"content_settings.tags.changed"`: Adds a "changed" tag to filter settings that have been modified (customizable via `CONTENT_SETTINGS_TAG_CHANGED`).
- `"content_settings.tags.app_name"`: Adds a tag for the app name where the setting is defined.

### `CONTENT_SETTINGS_UPDATE_DB_VALUES_BY_MIGRATE`

**Default**: `True`  
Synchronizes setting configurations (e.g., new versions or settings) after migrations are completed. To disable this behavior, set the value to `False` and use the `content_settings_migrate` command instead. [Learn more about this command here](commands.md#content_settings_migrate).

---

[![Stand With Ukraine](https://raw.githubusercontent.com/vshymanskyy/StandWithUkraine/main/banner-direct-single.svg)](https://stand-with-ukraine.pp.ua)
