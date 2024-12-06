"""
One of the most complicated module contains callable types. The Python object for those types usually needs to be called.

The complexity of the module also illustrates the flexibility of types.

The module is called a "template" because the setting's raw value is a template that will be used to generate a real value.

See `CallToPythonMixin`
"""

from itertools import zip_longest
from typing import Any, Tuple, Optional, Callable, Iterable, Union, Dict
from enum import Enum, auto

from django.core.exceptions import ValidationError
from django.utils.safestring import mark_safe
from django.db.models.query import QuerySet
from django.utils.translation import gettext as _

from content_settings.utils import obj_base_str
from .basic import SimpleText
from .mixins import CallToPythonMixin, GiveCallMixin, HTMLMixin
from .validators import call_validator, gen_signle_arg_call_validator
from . import PREVIEW, required


BUILTINS_SAFE = {}
BUILTINS_ALLOW_IMPORT = {}


def gen_builtins():
    if isinstance(BUILTINS_SAFE, dict):
        yield from __builtins__.items()
    else:
        for name in dir(__builtins__):
            yield name, getattr(__builtins__, name)


for name, value in gen_builtins():
    if name in ["memoryview", "open", "input"]:
        continue
    BUILTINS_ALLOW_IMPORT[name] = value

    if name == "__import__":
        continue
    BUILTINS_SAFE[name] = value


class STATIC_INCLUDES(Enum):
    CONTENT_SETTINGS = auto()
    SETTINGS = auto()


class StaticDataMixin:
    """
    Adds static data to the context, such as SETTINGS or/and CONTENT_SETTINGS.

    Attributes:

    - `template_static_includes` - tuple of `STATIC_INCLUDES` that should be included in the context. Default: `(STATIC_INCLUDES.CONTENT_SETTINGS, STATIC_INCLUDES.SETTINGS)`. If `STATIC_INCLUDES.SETTINGS` is included, `django.conf.settings` will be added to the context. If `STATIC_INCLUDES.CONTENT_SETTINGS` is included, `content_settings.conf.content_settings` will be added to the context.
    - `template_static_data` - static data that should be added to the context (on top of what will be added by `template_static_includes`). It can be a dictionary or a callable that returns a dictionary. Default: `None`.
    """

    template_static_includes: Tuple[STATIC_INCLUDES] = (
        STATIC_INCLUDES.CONTENT_SETTINGS,
        STATIC_INCLUDES.SETTINGS,
    )
    template_static_data: Optional[Union[Dict, Callable]] = None

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

        if STATIC_INCLUDES.SETTINGS in self.template_static_includes:
            from django.conf import settings

            ret["SETTINGS"] = settings

        return {
            **ret,
            **self.get_template_static_data(),
        }


class SimpleFunc(CallToPythonMixin, SimpleText):
    admin_preview_as: PREVIEW = PREVIEW.PYTHON


class SimpleCallTemplate(CallToPythonMixin, StaticDataMixin, SimpleText):
    """
    Base class for templates that can be called.
    """

    admin_preview_as: PREVIEW = PREVIEW.TEXT
    template_args_default = None

    def get_template_args_default(self):
        if not self.template_args_default:
            return {}
        return self.template_args_default

    def get_validators(self):
        validators = super().get_validators()

        if validators and any(isinstance(v, call_validator) for v in validators):
            return validators

        has_required_args = any(
            v == required for v in self.get_template_args_default().values()
        )
        if has_required_args:
            return validators

        return (call_validator(), *validators)

    def get_help_format(self):
        yield _("Available objects:")
        yield "<ul>"

        for name, default in self.get_template_args_default().items():
            yield f"<li>{name}"
            if default == required:
                yield " - "
                yield _("required")
                yield "</li>"
            else:
                yield " - "
                yield repr(default)
                yield "</li>"

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
                raise ValidationError(
                    _("Missing required argument %(name)s") % {"name": name}
                )

        return kwargs


class DjangoTemplate(SimpleCallTemplate):
    """
    The setting of that type generates value based on the Django Template in the raw value.
    """

    admin_preview_as: PREVIEW = PREVIEW.TEXT

    def get_help_format(self):
        yield _(
            "Simple <a href='https://docs.djangoproject.com/en/3.2/topics/templates/' target='_blank'>Django Template</a>."
        )
        yield " "
        yield from super().get_help_format()

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


class DjangoTemplateHTML(HTMLMixin, DjangoTemplate):
    """
    Same as `DjangoTemplate` but the rendered value is marked as safe.
    """

    pass


class DjangoTemplateNoArgs(GiveCallMixin, DjangoTemplate):
    """
    Same as `DjangoTemplate` but the setting value is not callablle, but already rendered value.
    """

    pass


class DjangoTemplateNoArgsHTML(HTMLMixin, DjangoTemplateNoArgs):
    """
    Same as `DjangoTemplateNoArgs` but the rendered value is marked as safe.
    """

    pass


class DjangoModelTemplateMixin:
    """
    Mixing that uses one argument for the template from the model queryset.

    Attributes:

    - `template_model_queryset` - QuerySet or a callable that returns a Model Object. For QuerySet, the first object will be used. For callable, the object returned by the callable will be used. The generated object will be used as validator and for preview.
    - `template_object_name` - name of the object in the template. Default: "object".
    """

    template_model_queryset: Optional[Union[QuerySet, Callable]] = None
    template_object_name: str = "object"

    def get_template_model_queryset(self):
        return self.template_model_queryset

    def get_template_object_name(self):
        return self.template_object_name

    def get_template_args_default(self):
        return {
            self.get_template_object_name(): required,
            **super().get_template_args_default(),
        }

    def get_first_call_validator(self):
        """
        generates the first validator based of template_model_queryset, which will be used for validation and for preview.
        """
        template_model_queryset = self.get_template_model_queryset()
        if template_model_queryset is not None:
            if isinstance(template_model_queryset, QuerySet):
                first = template_model_queryset.first()
                if first is not None:
                    return call_validator(first)
            elif callable(template_model_queryset):
                return gen_signle_arg_call_validator(template_model_queryset)
            else:
                raise ValueError(
                    _("template_model_queryset must be a QuerySet or a callable")
                )

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
    """

    admin_preview_as: PREVIEW = PREVIEW.PYTHON
    template_bultins: Optional[Union[str, Dict]] = "BUILTINS_SAFE"

    def get_help_format(self):
        yield _("Python code that returns a value.")
        yield " "
        yield from super().get_help_format()

    def prepare_python_call(self, value):
        return {"template": compile(value, "<string>", "eval")}

    def python_call(self, *args, **kwargs):
        template = kwargs.pop("template")
        globs = {
            **self.get_template_full_static_data(),
            **self.prepate_input_to_dict(*args, **kwargs),
        }

        if self.template_bultins:
            globs["__builtins__"] = obj_base_str(
                self.template_bultins, "content_settings.types.template"
            )

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


class SystemExec:
    """
    Mixin class that brings exec functionality into type

    Attributes:

    - `template_return` - dictates what will be returned as a setting value.
        - If `None`, the whole context will be returned. The default value.
        - if a string, the string will be used as a key from the context and that value will be returned.
        - If a dictionary, only the keys from the dictionary will be returned. The values will be used as defaults.
        - If a callable, the callable will be called and the return value will be used as a dictionary.
        - If an iterable, the iterable will be used as keys for the return dictionary. The values will be `None` by default.
    - `template_bultins` - allows to limit the builtin functions. By default it is `"BUILTINS_SAFE"`, which allows all functions except `memoryview`, `open`, `input` and `import`. If you want to include import use `"BUILTINS_ALLOW_IMPORT"`, if you don't want to use any limitation - just assign `None` to the attribute.
    - `template_raise_return_error` - raises an error if `template_return` doesn't match the context. Default: `False`.
    """

    template_return: Optional[Union[Iterable, Callable, Dict, str]] = None
    template_bultins: Optional[Union[str, Dict]] = "BUILTINS_SAFE"
    template_raise_return_error: bool = False

    def get_template_return(self):
        return self.template_return

    def get_template_raise_return_error(self):
        return self.template_raise_return_error

    def get_template_bultins(self):
        return obj_base_str(self.template_bultins, "content_settings.types.template")

    def get_help_format(self):
        yield from super().get_help_format()

        template_return = self.get_template_return()

        if template_return is None or callable(template_return):
            yield _("Return Dict is not specified")
        elif isinstance(template_return, str):
            yield _("Return value from the variable: %(variable)s") % {
                "variable": template_return
            }
        elif isinstance(template_return, dict):
            yield _("Return Dict: ")
            yield "<ul>"
            for name, value in template_return.items():
                yield f"<li>{name} - default: {value}</li>"
            yield "</ul>"
        elif isinstance(template_return, Iterable):
            yield _("Return Dict: ")
            yield "<ul>"
            for name in template_return:
                yield f"<li>{name}</li>"
            yield "</ul>"
        else:
            raise ValueError(_("Invalid template_return"))

    def system_exec(self, code, globs):
        globs = {**globs}
        if self.template_bultins:
            globs["__builtins__"] = self.get_template_bultins()

        exec(code, globs)
        template_return = self.get_template_return()

        if template_return is None:
            return globs
        elif callable(template_return):
            return template_return(globs)
        elif isinstance(template_return, str):
            if self.get_template_raise_return_error() and template_return not in globs:
                raise ValidationError(
                    _("Variable %(variable)s is required")
                    % {"variable": template_return}
                )
            return globs.get(template_return)
        elif isinstance(template_return, dict):
            return {k: globs.get(k, v) for k, v in template_return.items()}
        elif isinstance(template_return, Iterable):
            if self.get_template_raise_return_error() and (
                diff_keys := set(template_return).difference(set(globs.keys()))
            ):
                raise ValidationError(
                    _("Variables in the context are required: %(variables)s")
                    % {"variables": ", ".join(diff_keys)}
                )
            return {k: globs.get(k, None) for k in template_return}
        else:
            raise ValidationError(_("Invalid template_return"))


class SimpleExec(SystemExec, SimpleCallTemplate):
    """
    Template that executes the Python code (using `exec` function).
    """

    admin_preview_as: PREVIEW = PREVIEW.PYTHON

    def get_help_format(self):
        yield _("Python code that execute and returns generated variables.")
        yield " "
        yield from super().get_help_format()

    def prepare_python_call(self, value):
        return {"template": compile(value, "<string>", "exec")}

    def python_call(self, *args, **kwargs):
        template = kwargs.pop("template")
        globs = {
            **self.get_template_full_static_data(),
            **self.prepate_input_to_dict(*args, **kwargs),
        }

        return self.system_exec(template, globs)


class SimpleExecNoArgs(GiveCallMixin, SimpleExec):
    """
    Same as `SimpleExec` but the setting value is not callable, but already executed.
    """

    pass


class DjangoModelExec(DjangoModelTemplateMixin, SimpleExec):
    """
    Same as `SimpleExec` but uses one value as a model object.
    """

    pass


class SimpleExecNoCompile(SystemExec, StaticDataMixin, SimpleText):
    """
    It is not a Template, probably closed to markdown module, as it simply takes the text value and convert it into py object, which is not a compiled code but the result of execution of the code.

    But it is in the template module as it is very similar to `SimpleExecNoArgs`.

    It is super easy to shot in the foot with this class so be very cautious.
    """

    admin_preview_as: PREVIEW = PREVIEW.PYTHON

    def to_python(self, value: str) -> Any:
        value = super().to_python(value)
        return self.system_exec(value, self.get_template_full_static_data())
