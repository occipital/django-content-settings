from django.core.exceptions import ValidationError


class call_validator:
    def __init__(self, *args, **kwargs):
        self.args = args
        self.kwargs = kwargs

    def __call__(self, func):
        try:
            return func(*self.args, **self.kwargs)
        except Exception as e:
            raise ValidationError(str(e))
