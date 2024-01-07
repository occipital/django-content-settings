from django.core.exceptions import ValidationError
from pprint import pformat


class call_validator:
    def __init__(self, *args, **kwargs):
        self.args = args
        self.kwargs = kwargs

    def __call__(self, func):
        try:
            return func(*self.args, **self.kwargs)
        except Exception as e:
            raise ValidationError(str(e))

    def __str__(self) -> str:
        ret = ""
        if self.args:
            ret += ", ".join([pformat(arg) for arg in self.args])

        if self.kwargs:
            if ret:
                ret += ", "
            ret += ", ".join(
                [f"{key}={pformat(value)}" for key, value in self.kwargs.items()]
            )

        return ret

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} {str(self)}>"
