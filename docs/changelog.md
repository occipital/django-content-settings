# Changelog

## 0.3 - "give" control and admin preview refactoring

* `give` and `give_python` - new base method allows Type to control how the cached value will be given to the code. See the [Cookbook](cookbook.md) for usecases
* new mixins `GiveCallMixin` and `MakeCallMixin`
* new classes based on `GiveCallMixin` - `DjangoTemplateNoArgs` and `SimpleEvalNoArgs`
* Admin Preview refactoring:
    * `admin_preview_as` new base-class attribute. Possible values html/text/python
    * `preview_validators` new `CallToPythonMixin` attribute. A list/tuple of all validators for preview
    * `admin_preview_call` new `CallToPythonMixin` bool attribute. Should function execution be shown in preview
* `template_static_includes` - new attrubite for `SimpleCallTemplate`. 

## 0.2.3 - advanced context_managers

* `context_manangers`
    * parameter `init` for processors in `context_defaults`. You can now not only update default values, but also update assigned values
    * new processors: `add_tags`, `remove_tags`, `str_append`, `str_prepend`, `str_format`, `help_format`
* new [django setting](settings.md): `CONTENT_SETTINGS_CONTEXT_PROCESSORS` and `CONTENT_SETTINGS_CONTEXT_PROCESSORS` - you can now set a default context
* support default tags for types
* add default tags for templates and markups types
* add `superuser` in `permissions`
* fix: `content_settings_context`
* test coverage: 87%
