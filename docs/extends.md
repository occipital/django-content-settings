# Possible Extensions

The aim of this article is to showcase the various ways you can extend the basic functionality of `django-content-settings`.

---

## Create Your Own Classes

The most basic and common way to extend functionality is by creating your own classes based on the ones in `content_settings.types`.

- Check how other types are created.
- Review the extension points for [`content_settings.types.basic.SimpleString`](source.md#class-simplestringbasesettingsource).

---

## Generating Tags

Using the Django setting [`CONTENT_SETTINGS_TAGS`](settings.md#content_settings_tags), you can leverage built-in tags, such as `content_settings.tags.changed`. 

Additionally, you can create custom functions to generate tags for your settings based on their content. For inspiration, review the [source code](source.md#tags) for existing tags.

---

## Redefine Default Attributes for All Settings

Using the Django setting [`CONTENT_SETTINGS_DEFAULTS`](settings.md#content_settings_defaults), you can customize how default attributes are applied to all (or specific) settings.

- Refer to the [collections module](source.md#defaultscollections), which includes defaults for CodeMirror support.
- Similarly, configure defaults to support other code editors or UI components.

---

## Custom Access Rules

Access rules for settings can be defined by assigning specific functions to attributes. For more information, see [permissions](permissions.md).

To go beyond predefined functions, you can create your own custom access rule functions to implement unique logic.

---

## Custom Prefix for Settings

Several built-in prefixes, such as `withtag__` and `lazy__`, are available ([see full list here](access.md#prefix)). However, you can register your own prefixes using the `conf.register_prefix` decorator.

#### Example:

```python
from content_settings.conf import register_prefix
from content_settings.caching import get_value

@register_prefix("endswith")
def endswith_prefix(name: str, suffix: str):
    return {
        k: get_value(k, suffix) for k in dir(content_settings) if k.endswith(name)
    }
```

#### Usage:

```python
for name, value in content_settings.endswith__BETA:
    ...
```

---

## Integration with Task Management Systems

There are built-in integrations for task managers like Celery and Huey. These integrations are simple, and you can create your own.

#### Example: Celery Integration

This example ensures that all settings are updated before a task begins. It can be found in [signals.py](https://github.com/occipital/django-content-settings/blob/master/content_settings/signals.py):

```python
try:
    from celery.signals import task_prerun
except ImportError:
    pass
else:

    @task_prerun.connect
    def check_update_for_celery(*args, **kwargs):
        check_update()
```

The idea is to verify that all settings are up-to-date before starting a task.

---

## Middleware for Preview

To enable the preview functionality for settings, add the middleware `content_settings.middleware.preview_on_site` to your project’s settings.

The middleware:
- Checks if the user has preview objects.
- Processes the response under the updated settings context.

You can review the middleware’s [source code here](https://github.com/occipital/django-content-settings/blob/master/content_settings/middlewares.py).

### Custom Middleware

You may create custom middleware for specialized use cases, such as integrating with [django-impersonate](https://pypi.org/project/django-impersonate/).

---

## Cache Triggers

Cache triggers are part of the [caching functionality](caching.md). They allow you to configure when to update py objects related to settings.

- See the source code for [`content_settings.cache_triggers`](source.md#cache_triggers) for more information.

---

[![Stand With Ukraine](https://raw.githubusercontent.com/vshymanskyy/StandWithUkraine/main/banner-direct-single.svg)](https://stand-with-ukraine.pp.ua)
