# Changelog

📖 - documentation is required [issue](https://github.com/occipital/django-content-settings/issues/30)

## 0.5

* User Defined Variables - variables can now be created not only in code but also in admin
* 📖 `overwrite_user_defined` - new attribute that allows overwrite user defined variable
* 📖 `constant` - new attribute that makes the code variable unchangable in admin panel and only default value is using
* 📖 `conf.register_prefix` - decorator that allows you to registered a new prefix
* 📖 `startswith__` - new built-in decorator, that returns all of the names that starts with NAME
* `dir(content_settings)` - shows all of the registered variables
* db now stores tags and help for all variables
* 📖 `CHECKSUM_USER_KEY_PREFIX` and `USER_DEFINED_TYPES` two new settings
* fix "Preview Loading..." for variables without preview
* `caching.get_type_by_name` - new function
* test covarage: 93%

### 0.4.4

* built-in support huey and celery

### 0.4.3

* fix field validators
* None admin preview by default
* `SimpleHTML` - same as SimpleText but with HTML preview
* `EmailString` - new base type
* `SimpleExec` and `SimpleExecNoArgs` - new types. Works in the same way as SimpleEval, but using exec instead of eval and return values based on `call_return` attribute
* all eval and exec types have `superuser` as default value for `update_permission`
* `MakeCallMixin` has `call` suffix, just in case

### 0.4.2 - local dev fixes

* handeling removed settigs
* `CONTENT_SETTINGS_VALUES_ONLY_FROM_DB` - for DEBUG=False only
* handleling update version during local debug
* preview and updates for non-existed settings

### 0.4.1

* fix admin fields

## 0.4 - suffix and `fetch_groups` deprication

* `lazy_give` new function for giving a lazy object of the type. `LazyObject` has moved to own module `types.lazy`
* deprication of `fetch_groups` attribute and `views.FetchSettingsView` as a replacement
* uppercase for variable name is mandatory
* `call` suffix for `GiveCallMixin`. you can call no-args types like `content_settings.VAN_NAME__call("value")`
* DictSuffixesMixin - use dict for suffixes, where values are lambdas
* `suffix` is URLs for getting value from suffix
* new URL  `fetch/<str:name>/suffix/<str:suffix>/`
* test covarage: 89%


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
