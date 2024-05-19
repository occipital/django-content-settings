"""
One of the most complicated module contains callable types. The Python object for those types usually needs to be called.

The complexity of the module also illustrates the flexibility of types.

The module is called a "template" because the setting's raw value is a template that will be used to generate a real value.

See `CallToPythonMixin`
"""

from itertools import zip_longest
from typing import Any, Tuple, Optional, Callable, Iterable
from enum import Enum, auto

from django.core.exceptions import ValidationError
from django.utils.safestring import mark_safe
from django.db.models.query import QuerySet

from .basic import SimpleText
from .mixins import CallToPythonMixin, GiveCallMixin, HTMLMixin
from .validators import call_validator, gen_signle_arg_call_validator
from . import PREVIEW, required
from ..permissions import superuser


class STATIC_INCLUDES(Enum):
    CONTENT_SETTINGS = auto()
    SETTINGS = auto()
    UNITED_SETTINGS = auto()


class StaticDataMixin:
    """
    Adds static data to the context, such as SETTINGS or/and CONTENT_SETTINGS.

    Attributes:

    - `template_static_includes` - tuple of `STATIC_INCLUDES` that should be included in the context. Default: `(STATIC_INCLUDES.CONTENT_SETTINGS, STATIC_INCLUDES.SETTINGS)`. If `STATIC_INCLUDES.SETTINGS` is included, `django.conf.settings` will be added to the context. If `STATIC_INCLUDES.CONTENT_SETTINGS` is included, `content_settings.conf.content_settings` will be added to the context. If `STATIC_INCLUDES.UNITED_SETTINGS` is included, both `django.conf.settings` and `content_settings.conf.settings` will be added to the context in the `SETTINGS` key.
    - `template_static_data` - static data that should be added to the context (on top of what will be added by `template_static_includes`). It can be a dictionary or a callable that returns a dictionary. Default: `None`.
    """

    template_static_includes: Tuple[STATIC_INCLUDES] = (
        STATIC_INCLUDES.CONTENT_SETTINGS,
        STATIC_INCLUDES.SETTINGS,
    )
    template_static_data: Optional[dict | Callable] = None

    def get_template_static_data(self):
        if not self.template_static_data:
            return {}
        if callable(self.template_static_data):
            return self.template_static_data()
        return self.template_static_data

    def get_template_full_static_data(self):
        ret = {}

        if STATIC_INCLUDES.CONTENT_SETTINGS in self.template_static_includes:
            from content_settings.conf import content_settings

            ret["CONTENT_SETTINGS"] = content_settings

        if STATIC_INCLUDES.UNITED_SETTINGS in self.template_static_includes:
            from content_settings.conf import settings

            ret["SETTINGS"] = settings

        elif STATIC_INCLUDES.SETTINGS in self.template_static_includes:
            from django.conf import settings

            ret["SETTINGS"] = settings

        return {
            **ret,
            **self.get_template_static_data(),
        }


class SimpleCallTemplate(CallToPythonMixin, StaticDataMixin, SimpleText):
    """
    Base class for templates that can be called.
    """

    admin_preview_as: PREVIEW = PREVIEW.TEXT
    template_args_default = None

    def prepare_python_call(self, value):
        raise NotImplementedError()

    def python_call(self, *args, **kwargs):
        raise NotImplementedError()

    def get_template_args_default(self):
        if not self.template_args_default:
            return {}
        return self.template_args_default

    def get_validators(self):
        validators = super().get_validators()
        if validators:
            return validators

        has_required_args = any(
            v == required for v in self.get_template_args_default().values()
        )
        if has_required_args:
            return ()

        return (call_validator(),)

    def get_help_format(self):
        yield self.help_format
        yield " Available objects:<ul>"

        for name, default in self.get_template_args_default().items():
            yield f"<li>{name}"
            if default == required:
                yield f" - required</li>"
            else:
                yield f" - {repr(default)}</li>"

        for name in self.get_template_full_static_data().keys():
            yield f"<li>{name}</li>"

        yield "</ul>"

    def prepate_input_to_dict(self, *args, **kwargs):
        """
        prepares an inpit dictuonary for the call based on the given arguments and kwargs
        """
        template_args_default = self.get_template_args_default()
        no_value = {}
        kwargs = {
            **{
                default[0]: (default[1] if arg_value == no_value else arg_value)
                for arg_value, default in zip_longest(
                    args, template_args_default.items(), fillvalue=no_value
                )
                if default != no_value
            },
            **kwargs,
        }

        for name, value in kwargs.items():
            if value == required:
                raise ValidationError(f"Missing required argument {name}")

        return kwargs


class DjangoTemplate(SimpleCallTemplate):
    """
    The setting of that type generates value based on the Django Template in the raw value.
    """

    tags = {"template"}
    admin_preview_as: PREVIEW = PREVIEW.TEXT
    help_format = "Simple <a href='https://docs.djangoproject.com/en/3.2/topics/templates/' target='_blank'>Django Template</a>."

    def prepare_python_call(self, value):
        from django.template import Template

        return {"template": Template(value.strip())}

    def python_call(self, *args, **kwargs):
        from django.template import Context

        template = kwargs.pop("template")
        return (
            template.render(
                Context(
                    {
                        **self.get_template_full_static_data(),
                        **self.prepate_input_to_dict(*args, **kwargs),
                    }
                )
            )
            + ""  # to avoid returning SafeText
        )


class DjangoTemplateNoArgs(GiveCallMixin, DjangoTemplate):
    """
    Same as `DjangoTemplate` but the setting value is not callablle, but already rendered value.
    """

    pass


class DjangoTemplateHTML(HTMLMixin, DjangoTemplateNoArgs):
    """
    Same as `DjangoTemplateNoArgs` but the rendered value is marked as safe.
    """

    pass


class DjangoModelTemplateMixin:
    """
    Mixing that uses one argument for the template from the model queryset.

    Attributes:

    - `model_queryset` - QuerySet or a callable that returns a Model Object. For QuerySet, the first object will be used. For callable, the object returned by the callable will be used. The generated object will be used as validator and for preview.
    - `obj_name` - name of the object in the template. Default: "object".
    """

    model_queryset: Optional[QuerySet | Callable] = None
    obj_name: str = "object"

    def get_template_args_default(self):
        return {
            self.obj_name: required,
            **super().get_template_args_default(),
        }

    def get_first_call_validator(self):
        """
        generates the first validator based of model_queryset, which will be used for validation and for preview.
        """
        if self.model_queryset is not None:
            if isinstance(self.model_queryset, QuerySet):
                first = self.model_queryset.first()
                if first is not None:
                    return call_validator(first)
            elif callable(self.model_queryset):
                return gen_signle_arg_call_validator(self.model_queryset)
            else:
                raise ValueError("model_queryset must be a QuerySet or a callable")

    def get_validators(self):
        validators = super().get_validators()
        first_validator = self.get_first_call_validator()

        if first_validator is not None:
            validators = (first_validator, *validators)

        return validators


class DjangoModelTemplate(DjangoModelTemplateMixin, DjangoTemplate):
    """
    Django Template that uses one argument as a model object.
    """

    pass


class DjangoModelTemplateHTML(DjangoModelTemplate):
    """
    Same as `DjangoModelTemplate` but the rendered value is marked as safe.
    """

    admin_preview_as: PREVIEW = PREVIEW.HTML

    def give(self, value, suffix=None):
        render_func = super().give(value, suffix)
        return lambda *a, **k: mark_safe(render_func(*a, **k))


class SimpleEval(SimpleCallTemplate):
    """
    Template that evaluates the Python code (using `eval` function).

    By default, `update_permission` is set to `superuser`.
    """

    update_permission = staticmethod(superuser)
    help_format = "Python code that returns a value."
    tags = {"eval"}
    admin_preview_as: PREVIEW = PREVIEW.PYTHON

    def prepare_python_call(self, value):
        return {"template": compile(value, "<string>", "eval")}

    def python_call(self, *args, **kwargs):
        template = kwargs.pop("template")
        globs = {
            **self.get_template_full_static_data(),
            **self.prepate_input_to_dict(*args, **kwargs),
            "__import__": None,
        }

        return eval(template, globs)


class DjangoModelEval(DjangoModelTemplateMixin, SimpleEval):
    """
    Same as `SimpleEval` but uses one value as a model object.
    """

    pass


class SimpleEvalNoArgs(GiveCallMixin, SimpleEval):
    """
    Same as `SimpleEval` but the setting value is not callable, but already evaluated.
    """

    pass


class SimpleExec(SimpleCallTemplate):
    """
    Template that executes the Python code (using `exec` function).

    By default, `update_permission` is set to `superuser`.

    Attributes:

    - `call_return` - dictates what will be returned as a setting value.
        - If `None`, the whole context will be returned.
        - If a dictionary, only the keys from the dictionary will be returned. The values will be used as defaults.
        - If a callable, the callable will be called and the return value will be used as a dictionary.
        - If an iterable, the iterable will be used as keys for the return dictionary. The values will be `None` by default.
    - `allow_import` - allows importing modules. Default: `False`.
    """

    admin_preview_as: PREVIEW = PREVIEW.PYTHON
    update_permission = staticmethod(superuser)
    help_format = "Python code that execute and returns generated variables."
    tags = {"eval"}
    call_return: Optional[Iterable | Callable | dict] = None
    allow_import: bool = False

    def get_call_return(self):
        if self.call_return is None:
            return None

        if isinstance(self.call_return, dict):
            return self.call_return

        if callable(self.call_return):
            return self.call_return()

        return {name: None for name in self.call_return}

    def get_help_format(self):
        yield from super().get_help_format()
        if self.get_call_return() is None:
            yield "Return Dict is not specified"
        else:
            yield f"Return Dict: <ul>"
            for name, value in self.get_call_return().items():
                yield f"<li>{name} - default: {value}</li>"
            yield "</ul>"

    def prepare_python_call(self, value):
        return {"template": compile(value, "<string>", "exec")}

    def python_call(self, *args, **kwargs):
        template = kwargs.pop("template")
        globs = {
            **self.get_template_full_static_data(),
            **self.prepate_input_to_dict(*args, **kwargs),
        }

        if not self.allow_import:
            globs["__import__"] = None

        exec(template, globs)
        call_return = self.get_call_return()

        if call_return is None:
            return globs
        return {k: globs.get(k, v) for k, v in call_return.items()}


class DjangoModelExec(DjangoModelTemplateMixin, SimpleExec):
    """
    Same as `SimpleExec` but uses one value as a model object.
    """

    pass


class SimpleExecNoArgs(GiveCallMixin, SimpleExec):
    """
    Same as `SimpleExec` but the setting value is not callable, but already executed.
    """

    pass


class SimpleExecNoCall(StaticDataMixin, SimpleText):
    """
    Same as `SimpleExec` but the setting value is not callable, but already executed.

    The class is not inherited from `SimpleCallTemplate`, and technically can be a part of markdown module.
    """

    admin_preview_as: PREVIEW = PREVIEW.PYTHON
    update_permission = staticmethod(superuser)
    help_format = "Python code that execute and generates environment variables."
    tags = {"eval"}
    call_return = None
    allow_import = False

    def get_help_format(self):
        yield self.help_format
        yield " Available objects:<ul>"

        for name in self.get_template_full_static_data().keys():
            yield f"<li>{name}</li>"

        yield "</ul>"

    def get_call_return(self):
        if self.call_return is None:
            return None
        if isinstance(self.call_return, dict):
            return self.call_return

        return {name: None for name in self.call_return}

    def to_python(self, value: str) -> Any:
        value = compile(value, "<string>", "exec")

        globs = {
            **self.get_template_full_static_data(),
        }

        if not self.allow_import:
            globs["__import__"] = None

        exec(value, globs)
        call_return = self.get_call_return()

        if call_return is None:
            return globs
        return {k: globs.get(k, v) for k, v in call_return.items()}


class GiveOneKeyMixin:
    """
    Mixin that returns only one key from the result dict.

    Attributes:

    - `one_key_name` - name of the key that will be returned. Default: "result".
    """

    one_key_name: str = "result"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if hasattr(self, "call_return"):
            self.call_return = {self.one_key_name: required}
        self.one_key_name = self.one_key_name.lower()

    def give(self, value, suffix=None):
        return super().give(value, suffix)[self.one_key_name]


class SimpleExecOneKey(GiveOneKeyMixin, SimpleExec):
    """
    Same as `SimpleExec` but returns only one key (from attribute `one_key_name`) from the result dict.
    """

    pass


class SimpleExecOneKeyNoCall(GiveOneKeyMixin, SimpleExecNoCall):
    """
    Same as `SimpleExecNoCall` but returns only one key (from attribute `one_key_name`) from the result dict.
    """

    pass
