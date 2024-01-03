![Django Content Settings](img/title_2.png)

# Changelog

## 0.2.3 (test coverage: 87%)

* `context_mamangers`
    * parameter `init` for processors in `context_defaults`. You can now not only update default values, but also update assigned values
    * new processors: `add_tags`, `remove_tags`, `str_append`, `str_prepend`, `str_format`, `help_format`
* new [django setting](settings.md): `CONTENT_SETTINGS_CONTEXT_PROCESSORS` and `CONTENT_SETTINGS_CONTEXT_PROCESSORS` - you can now set a default context
* support default tags for types
* add default tags for templates and markups types
* add `superuser` in `permissions`
* fix: `content_settings_context`
