[![Stand With Ukraine](https://raw.githubusercontent.com/vshymanskyy/StandWithUkraine/main/banner-direct-single.svg)](https://stand-with-ukraine.pp.ua)

# Extends

*the article is still in WIP*

The aim of the article is to show all of the ways how you can extend the basic content settings functionality.

## Create your own classes

The most basic and the most common way to extend the functionality is to create your own class based on those that `content_settings.types` already have.

Check how the other types are created, and check the extension points for [`content_settings.types.basic.SimpleString](source.md#class-simplestringbasesettingsource)

## Generating tags

Using Django Setting [`CONTENT_SETTINGS_TAGS`](settings.md#content_settings_tags) you can use some of the builtin tags, such as `content_settings.tags.changed`, but also you can create your own function own function and for generating tags for your settings based of the content of the setting. Check the [source code](source.md#tags) of the tags already created.

## Redefine default attributes for all settings

Using Django Setting [`CONTENT_SETTINGS_DEFAULTS`](settings.md#content_settings_defaults) you can change how the default values for all (or for some) settings will look like

## Custom access rules

Every setting has access rules you can define not only by assign specific functions to specific attributes (see [permissions](permissions.md)), but you can define your own function that defines access rule.

## Custom prefix for settings

Currently we have several builtin prefixes `withtag__`, `startswith__`, `lazy__` and so on, but you can register own prefix using `conf.register_prefix` decorator.

For example:

```python
from content_settings.conf import register_prefix
from content_settings.caching import get_value


@register_prefix("endswith")
def endswith_prefix(name: str, suffix: str):
    return {
        k: get_value(k, suffix) for k in dir(content_settings) if k.endswith(name)
    }

```

register a new prefix, so now, in code you can use it

```python

for name, value in content_settngs.endswith__BETA:
    ...
```