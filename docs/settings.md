[![Stand With Ukraine](https://raw.githubusercontent.com/vshymanskyy/StandWithUkraine/main/banner-direct-single.svg)](https://stand-with-ukraine.pp.ua)

# Available Settings

## Overview

The `content_settings.settings.py` module in the `django-content-settings` package contains various settings that can be customized to tailor the functionality of the module. This article provides a comprehensive overview of these settings.

## Caching

Detailed information about caching can be found in a [dedicated section](caching.md). The following are the settings related to caching:

### `CONTENT_SETTINGS_CHECKSUM_KEY_PREFIX`

*default: `"CS_CHECKSUM_"`*

Specifies the prefix used when storing checksums.

### `CONTENT_SETTINGS_CACHE_BACKEND`

*default: `"default"`*

Defines the cache backend used for storing checksums.

### `CONTENT_SETTINGS_CACHE_TIMEOUT`

*default: `60 * 60 * 24`*

Sets the timeout for cache keys. Defines how long (in seconds) the cache keys will be stored before expiration.

### `CONTENT_SETTINGS_CACHE_SPLITER`

*default: `"::"`*

Specifies the string used to join values in caching. This value should not be used in the version value.

## Admin Panel

Additional functionalities related to the admin panel can be found in a [special section](admin.md). The following setting is specific to the admin panel:

### `CONTENT_SETTINGS_USER_TAGS`

Allows the addition of custom tags that users can assign to variables. This is a dict where the keys are tag names and the values are tuples. Each tuple contains two elements: the first element is the display representation when the tag is added, and the second is its display when it can be added.

**Default Value**:

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

## Other

### `CONTENT_SETTINGS_VALUES_ONLY_FROM_DB`

*default: False*

The values for variables should only be taken from DB. In case of any value is missing in DB - it will raise AssertionError

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

