[![Stand With Ukraine](https://raw.githubusercontent.com/vshymanskyy/StandWithUkraine/main/banner-direct-single.svg)](https://stand-with-ukraine.pp.ua)

# Available Settings

## Overview

The `content_settings.settings.py` module in the `django-content-settings` package contains various settings that can be customized to tailor the functionality of the module. This article provides a comprehensive overview of these settings.

## Caching

Detailed information about caching can be found in a [dedicated section](caching.md). The following are the settings related to caching:

### `CONTENT_SETTINGS_CHECKSUM_KEY_PREFIX` (default: `"CS_CHECKSUM_"`)

Specifies the prefix used when storing checksums.

### `CONTENT_SETTINGS_CACHE_BACKEND` (default: `"default"`)

Defines the cache backend used for storing checksums.

### `CONTENT_SETTINGS_CACHE_TIMEOUT` (default: `60 * 60 * 24`)

Sets the timeout for cache keys. Defines how long (in seconds) the cache keys will be stored before expiration.

### `CONTENT_SETTINGS_CACHE_SPLITER` (default: `"::"`)

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

## Other

### `CONTENT_SETTINGS_VALUES_ONLY_FROM_DB`

The values for variables should only be taken from DB. In case of any value is missing in DB - it will raise AssertionError

### `CONTENT_SETTINGS_CONTEXT_PROCESSORS` and `CONTENT_SETTINGS_CONTEXT`

Those are args and kwargs for global `context_defaults`. By settings one of those values you like grouping all of the under global `with context_defaults(*CONTENT_SETTINGS_CONTEXT_PROCESSORS, **CONTENT_SETTINGS_CONTEXT)`

For example if you want only superuser to update any settings by default

```python

from content_settings.permissions import superuser

CONTENT_SETTINGS_CONTEXT = {
    "update_permission": superuser
}
```

---

These customizable settings in the `django-content-settings` module enhance the flexibility and functionality of content management within Django applications. By adjusting these settings, developers can optimize the behavior of the module to better suit the specific needs of their projects.
