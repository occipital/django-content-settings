from itertools import zip_longest
from typing import Any, Tuple
from enum import Enum, auto

from django.core.exceptions import ValidationError
from django.utils.safestring import mark_safe

from .basic import SimpleText
from .mixins import CallToPythonMixin, GiveCallMixin, HTMLMixin
from .validators import call_validator
from . import PREVIEW, required
from ..permissions import superuser


class STATIC_INCLUDES(Enum):
    CONTENT_SETTINGS = auto()
    SETTINGS = auto()
    UNITED_SETTINGS = auto()


class StaticDataMixin:
    template_static_includes: Tuple[STATIC_INCLUDES] = (
        STATIC_INCLUDES.CONTENT_SETTINGS,
        STATIC_INCLUDES.SETTINGS,
    )
    template_static_data = None

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
    admin_preview_as: PREVIEW = PREVIEW.TEXT
    template_args_default = None
    help_format = "Simple <a href='https://docs.djangoproject.com/en/3.2/topics/templates/' target='_blank'>Django Template</a>."

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
    tags = {"template"}
    admin_preview_as: PREVIEW = PREVIEW.TEXT

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
            + ""
        )  # to avoid returning SafeText


class DjangoTemplateNoArgs(GiveCallMixin, DjangoTemplate):
    pass


class DjangoTemplateHTML(HTMLMixin, DjangoTemplateNoArgs):
    pass


class DjangoModelTemplateMixin:
    model_queryset = None
    obj_name = "object"

    def get_template_args_default(self):
        return {
            self.obj_name: required,
            **super().get_template_args_default(),
        }

    def get_first_call_validator(self):
        if self.model_queryset is not None:
            first = self.model_queryset.first()
            if first is not None:
                return call_validator(first)

    def get_validators(self):
        validators = super().get_validators()
        first_validator = self.get_first_call_validator()

        if first_validator is not None:
            validators = (first_validator, *validators)

        return validators


class DjangoModelTemplate(DjangoModelTemplateMixin, DjangoTemplate):
    pass


class DjangoModelTemplateHTML(DjangoModelTemplate):
    admin_preview_as: PREVIEW = PREVIEW.HTML

    def give(self, value, suffix=None):
        render_func = super().give(value, suffix)
        return lambda *a, **k: mark_safe(render_func(*a, **k))


class SimpleEval(SimpleCallTemplate):
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
    pass


class SimpleEvalNoArgs(GiveCallMixin, SimpleEval):
    pass


class SimpleExec(SimpleCallTemplate):
    admin_preview_as: PREVIEW = PREVIEW.PYTHON
    update_permission = staticmethod(superuser)
    help_format = "Python code that execute and returns generated variables."
    tags = {"eval"}
    call_return = None
    allow_import = False

    def get_call_return(self):
        if self.call_return is None:
            return None
        if isinstance(self.call_return, dict):
            return self.call_return

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
    pass


class SimpleExecNoArgs(GiveCallMixin, SimpleExec):
    pass


class SimpleExecNoCall(StaticDataMixin, SimpleText):
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
    one_key_name: str = "result"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if hasattr(self, "call_return"):
            self.call_return = {self.one_key_name: required}
        self.one_key_name = self.one_key_name.lower()

    def give(self, value, suffix=None):
        return super().give(value, suffix)[self.one_key_name]


class SimpleExecOneKey(GiveOneKeyMixin, SimpleExec):
    pass


class SimpleExecOneKeyNoCall(GiveOneKeyMixin, SimpleExecNoCall):
    pass
