# Available Settings

## Overview

The `content_settings.settings.py` module in the `django-content-settings` package contains various settings that can be customized to tailor the functionality of the module. This article provides a comprehensive overview of these settings.

## Caching

Detailed information about caching can be found in a [dedicated section](caching.md). The following are the settings related to caching:

### `CONTENT_SETTINGS_CACHE_TRIGGER`

*default: "content_settings.cache_triggers.VersionChecksum"*

Triggers class and configuration.

Can be string as classname:

```python
CONTENT_SETTINGS_CACHE_TRIGGER = "content_settings.cache_triggers.VersionChecksum"
```

Can be a dict with backend key as classname and other keys are keys for init arguments:

```python
CONTENT_SETTINGS_CACHE_TRIGGER = {
    "backend": "content_settings.cache_triggers.VersionChecksum",
    "cache_timeout": 100000,
}
```

other keys, except "backend" can be different from different backends. [Read more about this in caching section](caching.md)

## Admin Panel

Additional functionalities related to the admin panel can be found in a [special section](admin.md). The following setting is specific to the admin panel:

### `CONTENT_SETTINGS_USER_TAGS`

Allows the addition of custom tags that users can assign to variables. This is a dict where the keys are tag names and the values are tuples. Each tuple contains two elements: the first element is the display representation when the tag is added, and the second is its display when it can be added.

*default:*

```python
{
    "favorites": ("⭐", "⚝"),
    "marked": ("💚", "♡"),
}
```

In this default setting, users can tag variables as 'favorites' or 'marked' with corresponding emojis for added and addable states.

### `CONTENT_SETTINGS_ADMIN_CHECKSUM_CHECK_BEFORE_SAVE`

*default: False*

make check of the current checksum before saving data in django admin. If the page is opened for too long, and someone change any settings between page is opened and submited - changes wouldn't be applied.

### `CONTENT_SETTINGS_CHAIN_VALIDATE`

*default: True*

the settings can be connected with each other through the template types or one setting is included into validation of another setting. With having a chain `CONTENT_SETTINGS_CHAIN_VALIDATE = True` the system validates all of the py values before applying a new value.

### `CONTENT_SETTINGS_UI_DOC_URL`

*default: https://django-content-settings.readthedocs.io/en/0.19/ui/*

Link to the help page of the UI of Django Content settings. The link is shown in Django Admin panel. If the value is `None` - the link woudn't be shown.

### `CONTENT_SETTINGS_USER_DEFINED_TYPES`

*default: []*

Empty list means that the user is not allowed to create own user defined settings. Read more about user defined types [here](uservar.md).

It is a list of tuples with 3 strings. Example:

```python
CONTENT_SETTINGS_USER_DEFINED_TYPES=[
    ("text", "content_settings.types.basic.SimpleText", "Simple Text"),
    ("html", "content_settings.types.basic.SimpleHTML", "HTML"),
]
```

* slug (for example `"text"`) - value for internal use, should be unique.
* import line of the type class (for example `"content_settings.types.basic.SimpleText"`) - which class would be used for creating setting.
* name (for example `"Simple Text"`) - value that would be shown to the user in the drop-down list of the form.


### `CONTENT_SETTINGS_PREVIEW_ON_SITE_SHOW`

*default: True*

Use preview on site functionality. In case of `False` value - preview on site middleware `content_settings.middlewares.preivew_on_site` will be ignored and preview on site checkboxes will be hiden.

### `CONTENT_SETTINGS_PREVIEW_ON_SITE_HREF`

*default: /*

Preview on site panel has a link "View On Site". The setting contains href attribute for that link.

## Integration

### `CONTENT_SETTINGS_CHECK_UPDATE_CELERY`

*default: True*

if it is possible to import celery, the system checks updates for every `task_prerun`

### `CONTENT_SETTINGS_CHECK_UPDATE_HUEY`

*default: True*

if it is possible to import huey, the system checks updates for every `pre_execute`

## Other

### `CONTENT_SETTINGS_VALUES_ONLY_FROM_DB`

*default: False*

The values for variables should only be taken from DB. In case of any value is missing in DB - it will raise AssertionError

### `CONTENT_SETTINGS_VALIDATE_DEFAULT_VALUE`

*default: `settings.DEFAULT`*

With the app launch/reload validates not only DB values but also default values

### `CONTENT_SETTINGS_DEFAULTS`

*default: [] (empty list)*

defines a global defauls contexts for specific types.

a list of tuples. Each tuple has at least two elements.

The first element is a filter which defined which settings type is eligable for the global context. *The list of available filtes can be find in `content_settings.filters`*.

All other arguments are modiers that change the default arguments. *All modifiers can be found in `content_settings.defaults.modifiers`*.

[Read more about defaults context](defaults.md#global-updates-content_settings_defaults)

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

### `CONTENT_SETTINGS_TAGS`

*default: [] (empty list)*

Allows you to add automatically generated tags to all of your settings. It is a list of functions (or import line to the function)

The function should take three arguments - the name of the setting, setting object, and new value

Available built in types:

* `"content_settings.tags.changed"` - changed tag to filter only changed settings (the name of the tag can changed in setting `CONTENT_SETTINGS_TAG_CHANGED`)
* `"content_settings.tags.app_name"` - every setting will have a tag with app name where one was defined

### `CONTENT_SETTINGS_UPDATE_DB_VALUES_BY_MIGRATE`

*default: True*

Sync settings configurations (new version, new setting) after migrations is done. You can turn this function off and use command `content_settings_migrate` (see [commands](commands.md#content_settings_migrate))

[![Stand With Ukraine](https://raw.githubusercontent.com/vshymanskyy/StandWithUkraine/main/banner-direct-single.svg)](https://stand-with-ukraine.pp.ua)