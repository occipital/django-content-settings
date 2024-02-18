from typing import Any, Optional
from pprint import pformat

from django.core.exceptions import ValidationError
from django.utils.safestring import mark_safe

from .validators import call_validator
from . import PREVIEW_HTML, pre, PREVIEW_TEXT, PREVIEW_PYTHON, PREVIEW_NONE


def mix(*cls):
    return type("", cls, {})


class MinMaxValidationMixin:
    min_value = None
    max_value = None

    def validate(self, value):
        super().validate(value)

        is_none_valid = self.min_value is None and self.max_value is None
        if not is_none_valid and value is None:
            raise ValidationError("Value cannot be None")

        if self.min_value is not None and value < self.min_value:
            raise ValidationError(f"Value cannot be less than {self.min_value}")

        if self.max_value is not None and value > self.max_value:
            raise ValidationError(f"Value cannot be greater than {self.max_value}")

    def get_help_format(self):
        yield from super().get_help_format()

        if self.min_value is not None:
            yield f" from {self.min_value}"

        if self.max_value is not None:
            yield f" to {self.max_value}"


class EmptyNoneMixin:
    value_required = False

    def to_python(self, value):
        if value.strip() == "":
            return None
        return super().to_python(value)


class HTMLMixin:
    admin_preview_as: str = PREVIEW_HTML

    def get_help_format(self):
        yield from super().get_help_format()
        yield " in HTML format"

    def give(self, value, suffix=None):
        return mark_safe(super().give(value, suffix))


class PositiveValidationMixin(MinMaxValidationMixin):
    min_value = 0


class CallToPythonMixin:
    call_func = None

    def prepare_python_call(self, value):
        return {"prepared": value}

    def get_preview_validators(self):
        return [
            validator
            for validator in self.get_validators()
            if isinstance(validator, call_validator)
        ]

    def get_call_func(self):
        return self.call_func

    def python_call(self, *args, **kwargs):
        return self.call_func(*args, **kwargs)

    def to_python(self, value):
        value = super().to_python(value)
        prepared_kwargs = self.prepare_python_call(value)

        def _(*args, **kwargs):
            return self.python_call(*args, **prepared_kwargs, **kwargs)

        return _

    def give_python_to_admin(self, value, name, **kwargs):
        try:
            value = self.to_python(value)
        except Exception as e:
            return [(None, e)]
        ret = []
        for validator in self.get_preview_validators():
            str_validator = f"{name}({str(validator)})"
            try:
                ret.append((str_validator, validator(value)))
            except Exception as e:
                ret.append((str_validator, e))
        return ret

    def get_admin_preview_object(self, value, name, **kwargs):
        admin_preview_as = self.get_admin_preview_as()
        if admin_preview_as == PREVIEW_NONE:
            return ""

        if not value:
            return "No preview (add at least one call_validator in validators)"

        if len(value) == 1 and admin_preview_as in (PREVIEW_TEXT, PREVIEW_HTML):
            value = value[0][1]
            if isinstance(value, Exception):
                return f"ERROR!!! {value}"
            if admin_preview_as == PREVIEW_TEXT:
                return pre(value)
            else:
                return str(value)

        def _():
            for validator, val in value:
                yield pre(f">>> {validator}")

                if isinstance(val, Exception):
                    yield f"ERROR!!! {val}"
                else:
                    if admin_preview_as == PREVIEW_TEXT:
                        yield pre(val)
                    elif admin_preview_as == PREVIEW_HTML:
                        yield str(val)
                    else:
                        yield pre("<<< " + pformat(val))

        return "\n".join(_())


class GiveCallMixin:
    """
    for Template-like classes, when to_python should return a function,
    but as value you want to return not a function, but call it and return result
    """

    def get_suffixes(self):
        return ("call",) + super().get_suffixes()

    def get_validators(self):
        return (call_validator(),) + super().get_validators()

    def get_validators(self):
        validators = super().get_validators()
        if not validators:
            return (call_validator(),)
        return validators

    def give(self, value, suffix=None):
        if suffix is None:
            return value()
        if suffix == "call":
            return value
        return super().give(value, suffix)


class MakeCallMixin:
    def get_suffixes(self):
        return ("call",) + super().get_suffixes()

    def give_python_to_admin(self, value, name, **kwargs):
        return self.give_python(value)()

    def give(self, value, suffix=None):
        return lambda *args, **kwargs: value


class DictSuffixesMixin:
    suffixes = {}

    def give(self, value, suffix=None):
        if suffix is None:
            return value
        return self.suffixes[suffix](value)


class AdminPreviewMenuMixin:
    def get_admin_preview_html_menu(self, value: Any, name: str, **kwargs) -> str:
        return ""

    def get_admin_preview_object(self, value: str, name: str, **kwargs) -> str:

        return self.get_admin_preview_html_menu(
            value, name, **kwargs
        ) + self.get_admin_preview_under_menu_object(value, name, **kwargs)

    def get_admin_preview_under_menu_object(
        self, value: Any, name: str, **kwargs
    ) -> str:
        return super().get_admin_preview_object(value, name, **kwargs)


class AdminPreviewSuffixesMixin(AdminPreviewMenuMixin):
    admin_preview_suffixes = ()
    admin_preview_suffixes_default = "default"

    def get_admin_preview_suffixes_default(self):
        return self.admin_preview_suffixes_default

    def get_admin_preview_suffixes(self, value: str, name: str, **kwargs):
        return self.admin_preview_suffixes

    def get_admin_preview_html_menu(
        self, value: Any, name: str, suffix: Optional[str] = None, **kwargs
    ) -> str:
        suffixes = self.get_admin_preview_suffixes(value, name, **kwargs)
        if not len(suffixes):
            return ""

        ret = "<div>"
        for suf in (None, *suffixes):
            if suf == suffix:
                ret += f" <b>{suf or self.get_admin_preview_suffixes_default()}</b> "
            elif suf is None:
                ret += f' <a class="cs_set_params">{self.get_admin_preview_suffixes_default()}</a> '
            else:
                ret += f' <a class="cs_set_params" data-param-suffix="{suf}">{suf}</a> '
        ret += "</div>"

        return ret

    def get_admin_preview_under_menu_object(
        self, value: Any, name: str, **kwargs
    ) -> str:
        suffix = kwargs.get("suffix", None)
        return super().get_admin_preview_under_menu_object(
            self.give(value, suffix), name, **kwargs
        )


class DictSuffixesPreviewMixin(DictSuffixesMixin, AdminPreviewSuffixesMixin):
    def get_admin_preview_suffixes(self, value: str, name: str, **kwargs):
        return tuple(self.suffixes.keys())
