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

    def prepare_python_call(self, value):
        return {"prepared": value}

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

    def get_admin_preview_value(self, value, name):
        first_validator = next(
            (v for v in self.get_validators() if isinstance(v, call_validator)), None
        )

        if first_validator is None:
            return "No preview validators. Add at least one call_validator"

        return first_validator(self.to_python(value))
