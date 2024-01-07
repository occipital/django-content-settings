from pprint import pformat
from django.core.exceptions import ValidationError

from .validators import call_validator


def mix(*cls):
    return type("", cls, {})


class MinMaxValidationMixin:
    min_value = None
    max_value = None

    def validate_value(self, value):
        value = super().validate_value(value)

        is_none_valid = self.min_value is None and self.max_value is None
        if not is_none_valid and value is None:
            raise ValidationError("Value cannot be None")

        if self.min_value is not None and value < self.min_value:
            raise ValidationError(f"Value cannot be less than {self.min_value}")

        if self.max_value is not None and value > self.max_value:
            raise ValidationError(f"Value cannot be greater than {self.max_value}")
        return value

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
            value = self.give_python(value)
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

    def get_admin_preview_html(self, value, name):
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

    def get_admin_preview_text(self, value, name):
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

    def get_admin_preview_python(self, value, name):
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

    def give_python_to_admin(self, value, name):
        value = self.give_python(value)
        return [
            (None, value),
        ]

    def get_validators(self):
        return (call_validator(),)

    def give(self, value):
        return value()


class MakeCallMixin:
    def give_python_to_admin(self, value, name):
        return self.give_python(value)()

    def give(self, value):
        return lambda: value
