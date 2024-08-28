[![Stand With Ukraine](https://raw.githubusercontent.com/vshymanskyy/StandWithUkraine/main/banner-direct-single.svg)](https://stand-with-ukraine.pp.ua)

# Changelog

### master

* `DjangoTemplateNoArgsHTML` and change `DjangoTemplateHTML`
* `ProcessorsMixin` and `GiveProcessorsMixin` new mixins. More in [types](types.md#mixins-source)
* new doc about [template types](template_types.md)
* `result_validator`
* `PreviewValidator`, `PreviewValidationError`. More in [template types](template_types.md#custom-validator).
* `SimpleExecNoCompile`. More in [template types](template_types.md#simpleexecnocompilesystemexec-staticdatamixin-simpletext).
* refactoring of template attributes. They all have prefix template now. More in [template types](template_types.md).
* `suffixes` attribute is a dict with function as value.
* `template_bultins` attrubute as a replacement for `allow_import`. More in [template types](template_types.md).

#### 0.20.1

* new [settings](settings.md) - `CONTENT_SETTINGS_CHECK_UPDATE_CELERY` and `CONTENT_SETTINGS_CHECK_UPDATE_HUEY`
* fix `widgets_attr`

### 0.20 Long widgets

### 0.19 Import/Export through the UI and commands

* Import/Export UI in Django Admin. [Read more in UI](ui.md#import-export)
* Import/Export commands. [Read more in Commands](commands.md)
* Mechanism of reverting update from hisotry and seeing the update batch
* `context_managers.content_settings_context` now works with user defifined types
* previewed content settings doesn't work for urls from Django Admin content settings. To prevent validation issues
* migration that extends the history with user defined type attributes, such as tags and help
* you can do a preview for user defined types, you can do a preview of creation of new user defined type
* names of the URLS has "content_settings" prefix
* fix bug with assign only attributes (not methods)
* defaults takes type arguments into account - you can now extend `yeses` and `noes` into `CONTENT_SETTINGS_DEFAULTS`

#### 0.18.2 CallToPythonMixin.call_prepare_func

* `SimpleFunc` a very basic template type.
* new `CallToPythonMixin` attributes `call_func_argument_name` and `call_prepare_func`
* More in [Types](types.md#templates-content_settingstypestemplate-source)

#### 0.18.1

* setting `CONTENT_SETTINGS_PREVIEW_ON_SITE_SHOW = False` hides preview on site functionality
* fix some bugs

### 0.18 Better validation

* attributes that accept function can also accept string as name of the function. `fetch_permission="staff"` or `fetch_permission="content_settings.permissions.staff"`
* `FetchAllSettingsView.as_view()` - new view for getting all avaliable settings in the system
    * `FetchAllSettingsView.as_view(names=gen_all())` - works in the same way
* py objects validation at the time when the project is started. 
* `CONTENT_SETTINGS_CHAIN_VALIDATE` - new django setting, by default True. Every time you change the variable it not only test the variable you've changed, but also all other variables to make sure your changes doesn't break other variables.
* [article](ui.md) about Admin User interface with the link in the interface.
* simplify `json_view_value` for simple values, to speed up the API


### 0.17 CodeMirror

* new attributes for css and js
    * `admin_head_css: Tuple[str] = ()`
    * `admin_head_js: Tuple[str] = ()`
    * `admin_head_css_raw: Tuple[str] = ()`
    * `admin_head_js_raw: Tuple[str] = ()`
* new `defaults.modifiers`
    * `update_widget_attrs`
    * `add_widget_class`
    * `add_admin_head`
* `defaults.collections` - allows you to add [CodeMirror 5](https://codemirror.net/5/) support

### 0.16

* remove `urls.py` now the only quick way to connect API is to use [Views](api.md)
* remove `content_settings.startswith` and `content_settings.withtag`
* more [doc-strings](source.md), update `poetry.lock` and test coverage 94%

### 0.15

* fixing nox testing for covering different Python and Django versions
* `context_managers.context_defaults` moved to `defaults.context.defaults`. More in [defaults documentation](defaults.md)
* `CONTENT_SETTINGS_DEFAULTS` is a replacement for `CONTENT_SETTINGS_CONTEXT_PROCESSORS` and `CONTENT_SETTINGS_CONTEXT`. More in [defaults documentation](defaults.md)
* Ability to assign defaults globally for specific setting types. More in [defaults documentation](defaults.md)
* `CONTENT_SETTINGS_ADMIN_CHECKSUM_CHECK_BEFORE_SAVE` - new settings that makes sure that nothing is changed while the Django Admin panel for content settings were opened
* remove overwriting default attributes tags and permissions in subclasses.
* new module [functools](#functools) - which now contains logical functions `not_`, `or_` and `and_`, moved from module `permissions` since those functions are used for `defaults.filters` as well
* [Preparation for the version 1](https://github.com/occipital/django-content-settings/labels/v1)

### 0.13.1

* `SimpleExec.call_return` and `DjangoModelTemplateMixin.model_queryset` can be callable now
* `mdsource` for generation docs from the source code
* black version was updated to use for Python 3.8

## 0.13

* `CONTENT_SETTINGS_TAGS` refactoring, the function accepts additional argument name
* `"content_settings.tags.app_name"` - autogenerate tag with the app name
* new validators `gen_call_validator`, `gen_args_call_validator` and `gen_kwargs_call_validator`
* AttributeError when you trying to use an uknown setting name

### 0.12.1

* 📖 SimpleExecNoCall
* 📖 GiveOneKeyMixin
* 📖 SimpleExecOneKey
* 📖 SimpleExecOneKeyNoCall
* STATIC_INCLUDES.UNITED_SETTINGS

## 0.12

* internal constants refactoring to Enums.
* validation changes on the list view using `content_settings_context`
* Admin: fix delete link

### 0.11.4

* `from content_settings.conf import settings`

### 0.11.2

* new attributes `on_change` and `on_change_commited`
* pass user object in the preview

### 0.11.1 hot fix for edit form

## 0.11 Preview On Site

![DictSuffixesPreviewMixin](img/preview_on_site.png)

* admin can now preview settings on site before applying
* new middleware `middlewares.preivew_on_site`

### 0.10.2

* help_text is alternative for help attribute
* fix warnings
* using urls is optional

## 0.10 AdminPreviewActionsMixin

* `SplitByFirstLine` is now in `EachMixin`
* `SplitByFirstLine.split_type` can be a dict with key:cs_type
* `AdminPreviewActionsMixin`
* new attribute `validators_raw`

## 0.9 Django Admin Panel

* Fixing a lot of bugs with admin of content settings. Such as preivew, search, tags filters and cetera
* fixing dynamic work with local changes in content settings
* fix help text for user defined types
* if variable constant or removed from code - admin is not allowed to see it in django admin
* new type `DjangoModelTemplateHTML`
* fix issue with \r\n in tags field for user defined types
* remove attribute `empty_is_none`, we have `EmptyNoneMixin` mixin instead
* `validators` can be tuple and list now
* `EachMixin` now works only with expected types.
* new class for `EachMixin` - `each.Values` - convers all values in the dict
* fixing bugs with lazy object
* for `CallToPythonMixin`, `preview_validators` and `admin_preview_call` are removed. Now, all of the validators, that are instance of `call_validator` will be shows in preview and settings call will be always shown if more than one validators are for preview
* the change above requires massive refactoring for preview of template/call types
* if `SimpleCallTemplate` doesn't have a required arguments and doesn't have validators - the system uses one validator `call_validator()`
* `DjangoTemplateHTML(HTMLMixin, DjangoTemplate)` -> `DjangoTemplateHTML(HTMLMixin, DjangoTemplateNoArgs)`

### 0.8.1

* `SplitByFirstLine.split_key_validator_failed`
* fix preview for `each.Keys`

## 0.8 EachMixin and HTMLMixin

* `EachMixin`
* `HTMLMixin` and `DjangoTemplateHTML`
* showing type name(s) in admin panel
* migrate can also show "adjust" in case of changing tags or/and help
* yet another admin preview function refactoring.
* fix quoting in text/python preview

### 0.7.1 help format

* Default preview for Exec and Eval is Python
* SimpleBool more possible input options
* help_format for SplitTranslation
* test covarage: 95%

## 0.7 permissions and content tags

* __content generated tags__ - tags that can be generated not based on the given tags, but based on the given value.
* `CONTENT_SETTINGS_TAGS` - a list of functions that can generate tags for variable based on value
* `view_permission` and `view_history_permission`
* `SimplePassword`
* `json_view_value` returns string

### 0.6.4

* `caching.get_raw_value` - new function
* `context_manager.process_set` - correct work with str, list and other iterable (those will be converted to set)
* prevent resetting value if only help of tags were updated. The value will be reset to default only in case of version update

### 0.6.3 fix caching for huey and celery

### 0.6.2 SimpleHTML and DjangoModelTemplateMixin

* new mixin `DjangoModelTemplateMixin` and new types `DjangoModelEval` and `DjangoModelExec`
* give for `SimpleHTML` is now marked safe, so no need to use `|safe` filter in template
* fix `SimpleEval` and `SimpleExec` permissions
* fix `SimpleStringsList.comment_starts_with`

### 0.6.1 SimpleCSV: you can now set default, required and optional argument for the column type

```python
from content_settings.types import required, optional

var = SimpleCSV(
    csv_fields={
        "name": SimpleString(required),
        "balance": SimpleDecimal("0"),
        "price": SimpleDecimal(optional),
    },
)
```

## 0.6 I18N & suffix preview in admin

* `types.mixin.AdminPreviewMixin` - build menu on top of preview
* `types.mixin.AdminPreviewSuffixesMixin` - top menu build based on using suffixes
* `types.mixin.DictSuffixesPreviewMixin` - mix with `DictSuffixesMixin`

![DictSuffixesPreviewMixin](img/dict_suffixes_preview.gif)

* `types.array.SplitByFirstLine` - splitting text by multiple suffixes with custom chooser of the default value
* `types.array.SplitTranslation` - `types.array.SplitByFirstLine` with chooser by the current translation

![SplitTranslation](img/split_translation.png)

Minor:

* `validate_value` now splitted on two `validate_raw_value` for validation text and `validate` for validation python object
* `withtag__NAME` - new built-in prefix, that returns all of the names that have tag "name"
* `help_format` - by default empty text
* `get_admin_preview_as`
* `validate_value` and other validators does not return value
* `get_admin_preview_(self, value, name, **kwargs)` - has now `**kwargs` can be passed from the preview request

## 0.5 User Defined Variables & Constants

* User Defined Variables - variables can now be created not only in code but also in admin
* `overwrite_user_defined` - new attribute that allows overwrite user defined variable
* `constant` - new attribute that makes the code variable unchangable in admin panel and only default value is using
* `conf.register_prefix` - decorator that allows you to registered a new prefix
* `startswith__NAME` - new built-in prefix, that returns all of the names that starts with NAME
* `dir(content_settings)` - shows all of the registered variables
* db now stores tags and help for all variables
* `CHECKSUM_USER_KEY_PREFIX` and `USER_DEFINED_TYPES` two new settings
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
