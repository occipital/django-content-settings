from typing import Any, Optional
from pprint import pformat
from django.core.exceptions import ValidationError

from .validators import call_validator
from . import PREVIEW_NONE


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


class PositiveValidationMixin(MinMaxValidationMixin):
    min_value = 0


class CallToPythonMixin:
    call_func = None
    preview_validators = None
    admin_preview_call = True

    def prepare_python_call(self, value):
        return {"prepared": value}

    def get_preview_validators(self):
        if self.preview_validators is None:
            return ()
        return self.preview_validators

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

    def give_python_to_admin(self, value, name):
        try:
            value = self.to_python(value)
        except Exception as e:
            return [(None, e)]
        ret = []
        for validator in self.get_preview_validators():
            str_validator = (
                f"{name}({str(validator)})" if self.admin_preview_call else None
            )
            try:
                ret.append((str_validator, validator(value)))
            except Exception as e:
                ret.append((str_validator, e))
        return ret

    def get_admin_preview_html(self, value, name, **kwargs):
        ret = self.give_python_to_admin(value, name)
        if not ret:
            return "No preview (add at least one validator to preview_validators)"
        html = ""
        for validator, val in ret:
            if validator:
                html += f"<div>{validator}</div>"

            if isinstance(val, Exception):
                val = f"ERROR!!! {val}"

            if not self.admin_preview_call and len(ret) == 1:
                html += str(val)
            else:
                html += f"<div>{val}</div>"

        return html

    def get_admin_preview_text(self, value, name, **kwargs):
        ret = self.give_python_to_admin(value, name)
        if not ret:
            return "No preview (add at least one validator to preview_validators)"

        def _():
            for validator, val in ret:
                if validator:
                    yield f">>> {validator}"

                if isinstance(val, Exception):
                    yield f"ERROR!!! {val}"
                elif not self.admin_preview_call and len(ret) == 1:
                    yield str(val)
                else:
                    yield f"<<< {pformat(val)}"

        return "\n".join(_())

    def get_admin_preview_python(self, value, name, **kwargs):
        ret = self.give_python_to_admin(value, name)

        if self.admin_preview_call:
            return ret

        ret = [v for _, v in ret]
        if len(ret) == 1:
            return ret[0]

        return ret


class GiveCallMixin:
    """
    for Template-like classes, when to_python should return a function,
    but as value you want to return not a function, but call it and return result
    """

    admin_preview_call = False

    def get_suffixes(self):
        return ("call",) + super().get_suffixes()

    def get_validators(self):
        return (call_validator(),) + super().get_validators()

    def get_preview_validators(self):
        return (call_validator(),) + super().get_preview_validators()

    def give(self, value, suffix=None):
        if suffix is None:
            return value()
        if suffix == "call":
            return value
        return super().give(value, suffix)


class MakeCallMixin:
    def get_suffixes(self):
        return ("call",) + super().get_suffixes()

    def give_python_to_admin(self, value, name):
        return self.give_python(value)()

    def give(self, value, suffix=None):
        return lambda *args, **kwargs: value


class DictSuffixesMixin:
    suffixes = {}

    def give(self, value, suffix=None):
        if suffix is None:
            return value
        return self.suffixes[suffix](value)


class AdminPreviewMixin:
    def get_admin_preview_html_menu(self, value: str, name: str, **kwargs) -> str:
        return ""

    def get_admin_preview_value(self, value: str, name: str, **kwargs) -> str:
        if self.get_admin_preview_as() == PREVIEW_NONE:
            return ""
        return self.get_admin_preview_html_menu(
            value, name, **kwargs
        ) + super().get_admin_preview_value(value, name, **kwargs)


class AdminPreviewSuffixesMixin(AdminPreviewMixin):
    admin_preview_suffixes = ()
    admin_preview_suffixes_default = "default"

    def get_admin_preview_suffixes_default(self):
        return self.admin_preview_suffixes_default

    def get_admin_preview_suffixes(self, value: str, name: str, **kwargs):
        return self.admin_preview_suffixes

    def get_admin_preview_html_menu(
        self, value: str, name: str, suffix: Optional[str] = None, **kwargs
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

    def give_python_to_admin(
        self, value: str, name: str, suffix: Optional[str] = None, **kwargs
    ) -> Any:
        return self.give_python(value, suffix)


class DictSuffixesPreviewMixin(DictSuffixesMixin, AdminPreviewSuffixesMixin):
    def get_admin_preview_suffixes(self, value: str, name: str, **kwargs):
        return tuple(self.suffixes.keys())
