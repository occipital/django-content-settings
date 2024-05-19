One of the most complicated module contains callable types. The Python object for those types usually needs to be called.

The complexity of the module also illustrates the flexibility of types.

The module is called a "template" because the setting's raw value is a template that will be used to generate a real value.

See `CallToPythonMixin`

# class StaticDataMixin() [source](https://github.com/occipital/django-content-settings/blob/master/content_settings/types/template.py#L32)

Adds static data to the context, such as SETTINGS or/and CONTENT_SETTINGS.

Attributes:

- `template_static_includes` - tuple of `STATIC_INCLUDES` that should be included in the context. Default: `(STATIC_INCLUDES.CONTENT_SETTINGS, STATIC_INCLUDES.SETTINGS)`. If `STATIC_INCLUDES.SETTINGS` is included, `django.conf.settings` will be added to the context. If `STATIC_INCLUDES.CONTENT_SETTINGS` is included, `content_settings.conf.content_settings` will be added to the context. If `STATIC_INCLUDES.UNITED_SETTINGS` is included, both `django.conf.settings` and `content_settings.conf.settings` will be added to the context in the `SETTINGS` key.
- `template_static_data` - static data that should be added to the context (on top of what will be added by `template_static_includes`). It can be a dictionary or a callable that returns a dictionary. Default: `None`.

# class SimpleCallTemplate(CallToPythonMixin, StaticDataMixin, SimpleText) [source](https://github.com/occipital/django-content-settings/blob/master/content_settings/types/template.py#L79)

Base class for templates that can be called.

## def prepate_input_to_dict(self) [source](https://github.com/occipital/django-content-settings/blob/master/content_settings/types/template.py#L127)

prepares an inpit dictuonary for the call based on the given arguments and kwargs

# class DjangoTemplate(SimpleCallTemplate) [source](https://github.com/occipital/django-content-settings/blob/master/content_settings/types/template.py#L151)

The setting of that type generates value based on the Django Template in the raw value.

# class DjangoTemplateNoArgs(GiveCallMixin, DjangoTemplate) [source](https://github.com/occipital/django-content-settings/blob/master/content_settings/types/template.py#L182)

Same as `DjangoTemplate` but the setting value is not callablle, but already rendered value.

# class DjangoTemplateHTML(HTMLMixin, DjangoTemplateNoArgs) [source](https://github.com/occipital/django-content-settings/blob/master/content_settings/types/template.py#L190)

Same as `DjangoTemplateNoArgs` but the rendered value is marked as safe.

# class DjangoModelTemplateMixin() [source](https://github.com/occipital/django-content-settings/blob/master/content_settings/types/template.py#L198)

Mixing that uses one argument for the template from the model queryset.

Attributes:

- `model_queryset` - QuerySet or a callable that returns a Model Object. For QuerySet, the first object will be used. For callable, the object returned by the callable will be used. The generated object will be used as validator and for preview.
- `obj_name` - name of the object in the template. Default: "object".

## def get_first_call_validator(self) [source](https://github.com/occipital/django-content-settings/blob/master/content_settings/types/template.py#L217)

generates the first validator based of model_queryset, which will be used for validation and for preview.

# class DjangoModelTemplate(DjangoModelTemplateMixin, DjangoTemplate) [source](https://github.com/occipital/django-content-settings/blob/master/content_settings/types/template.py#L241)

Django Template that uses one argument as a model object.

# class DjangoModelTemplateHTML(DjangoModelTemplate) [source](https://github.com/occipital/django-content-settings/blob/master/content_settings/types/template.py#L249)

Same as `DjangoModelTemplate` but the rendered value is marked as safe.

# class SimpleEval(SimpleCallTemplate) [source](https://github.com/occipital/django-content-settings/blob/master/content_settings/types/template.py#L261)

Template that evaluates the Python code (using `eval` function).

By default, `update_permission` is set to `superuser`.

# class DjangoModelEval(DjangoModelTemplateMixin, SimpleEval) [source](https://github.com/occipital/django-content-settings/blob/master/content_settings/types/template.py#L287)

Same as `SimpleEval` but uses one value as a model object.

# class SimpleEvalNoArgs(GiveCallMixin, SimpleEval) [source](https://github.com/occipital/django-content-settings/blob/master/content_settings/types/template.py#L295)

Same as `SimpleEval` but the setting value is not callable, but already evaluated.

# class SimpleExec(SimpleCallTemplate) [source](https://github.com/occipital/django-content-settings/blob/master/content_settings/types/template.py#L303)

Template that executes the Python code (using `exec` function).

By default, `update_permission` is set to `superuser`.

Attributes:

- `call_return` - dictates what will be returned as a setting value.
    - If `None`, the whole context will be returned.
    - If a dictionary, only the keys from the dictionary will be returned. The values will be used as defaults.
    - If a callable, the callable will be called and the return value will be used as a dictionary.
    - If an iterable, the iterable will be used as keys for the return dictionary. The values will be `None` by default.
- `allow_import` - allows importing modules. Default: `False`.

# class DjangoModelExec(DjangoModelTemplateMixin, SimpleExec) [source](https://github.com/occipital/django-content-settings/blob/master/content_settings/types/template.py#L369)

Same as `SimpleExec` but uses one value as a model object.

# class SimpleExecNoArgs(GiveCallMixin, SimpleExec) [source](https://github.com/occipital/django-content-settings/blob/master/content_settings/types/template.py#L377)

Same as `SimpleExec` but the setting value is not callable, but already executed.

# class SimpleExecNoCall(StaticDataMixin, SimpleText) [source](https://github.com/occipital/django-content-settings/blob/master/content_settings/types/template.py#L385)

Same as `SimpleExec` but the setting value is not callable, but already executed.

The class is not inherited from `SimpleCallTemplate`, and technically can be a part of markdown module.

# class GiveOneKeyMixin() [source](https://github.com/occipital/django-content-settings/blob/master/content_settings/types/template.py#L434)

Mixin that returns only one key from the result dict.

Attributes:

- `one_key_name` - name of the key that will be returned. Default: "result".

# class SimpleExecOneKey(GiveOneKeyMixin, SimpleExec) [source](https://github.com/occipital/django-content-settings/blob/master/content_settings/types/template.py#L455)

Same as `SimpleExec` but returns only one key (from attribute `one_key_name`) from the result dict.

# class SimpleExecOneKeyNoCall(GiveOneKeyMixin, SimpleExecNoCall) [source](https://github.com/occipital/django-content-settings/blob/master/content_settings/types/template.py#L463)

Same as `SimpleExecNoCall` but returns only one key (from attribute `one_key_name`) from the result dict.