from itertools import zip_longest

from django.core.exceptions import ValidationError

from .basic import SimpleText
from .mixins import CallToPythonMixin
from .validators import call_validator


class required:
    pass


class SimpleCallTemplate(CallToPythonMixin, SimpleText):
    template_static_data = None
    template_args_default = None
    preview_html = True
    help_format = "Simple <a href='https://docs.djangoproject.com/en/3.2/topics/templates/' target='_blank'>Django Template</a>. Available objects:"

    def prepare_python_call(self, value):
        raise NotImplementedError()

    def python_call(self, *args, **kwargs):
        raise NotImplementedError()

    def get_template_args_default(self):
        if not self.template_args_default:
            return {}
        return self.template_args_default

    def get_template_static_data(self):
        if not self.template_static_data:
            return {}
        return self.template_static_data

    def get_help_format(self):
        yield self.help_format
        yield "<ul>"

        for name in self.get_template_args_default().keys():
            yield f"<li>{name}</li>"

        for name in self.get_template_static_data().keys():
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

    def get_template_static_data(self):
        from django.conf import settings
        from content_settings.conf import content_settings

        ret = {
            "CONTENT_SETTINGS": content_settings,
            "SETTINGS": settings,
        }

        if self.template_static_data is not None:
            ret = {**ret, **self.template_static_data}
        return ret

    def get_admin_preview_value(self, value, name):
        ret = super().get_admin_preview_value(value, name)
        if self.preview_html:
            return ret
        return f"<pre>{ret}</pre>"


class DjangoTemplate(SimpleCallTemplate):
    def prepare_python_call(self, value):
        from django.template import Template

        return {"template": Template(value.strip())}

    def python_call(self, *args, **kwargs):
        from django.template import Context

        template = kwargs.pop("template")
        return template.render(
            Context(
                {
                    **self.get_template_static_data(),
                    **self.prepate_input_to_dict(*args, **kwargs),
                }
            )
        )


class DjangoModelTemplate(DjangoTemplate):
    model_queryset = None
    obj_name = "object"

    def get_template_args_default(self):
        return {
            self.obj_name: required,
            **super().get_template_args_default(),
        }

    def get_validators(self):
        validators = super().get_validators()

        if self.model_queryset is not None:
            first = self.model_queryset.first()
            if first is not None:
                validators = (*validators, call_validator(self.model_queryset.first()))

        return validators


class SimpleEval(SimpleCallTemplate):
    help_format = "Python code that returns a value"

    def prepare_python_call(self, value):
        return {"template": compile(value, "<string>", "eval")}

    def python_call(self, *args, **kwargs):
        template = kwargs.pop("template")
        globs = {
            **self.get_template_static_data(),
            **self.prepate_input_to_dict(*args, **kwargs),
            "__import__": None,
        }

        return eval(template, globs)
