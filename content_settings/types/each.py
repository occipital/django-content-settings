from pprint import pformat

from django.core.exceptions import ValidationError

from . import required, optional, PREVIEW_HTML


class BaseEach:
    pass


class Item(BaseEach):
    def __init__(self, cs_type):
        self.cs_type = cs_type

    def validate(self, value):
        for i, v in enumerate(value, start=1):
            try:
                self.cs_type.validate(v)
            except ValidationError as e:
                raise ValidationError(f"item #{i}: {e.message}")

    def to_python(self, value):
        ret = []
        for i, v in enumerate(value, start=1):
            try:
                ret.append(self.cs_type.to_python(v))
            except ValidationError as e:
                raise ValidationError(f"item #{i}: {e.message}")
        return ret

    def give_python_to_admin(self, value, name, **kwargs):
        ret = []
        for i, v in enumerate(value, start=1):
            try:
                ret.append(self.cs_type.give_python_to_admin(v, name, **kwargs))
            except ValidationError as e:
                raise ValidationError(f"item #{i}: {e.message}")
        return ret

    def get_help_format(self):
        yield "A list of items. Each item should be: "
        yield "<div class='subitem'>"
        yield from self.cs_type.get_help_format()
        yield "</div>"

    def give(self, value, suffix=None):
        return [self.cs_type.give(v, suffix) for v in value]

    def get_admin_preview_object(self, value, *args, **kwargs):
        return (
            "["
            + (
                ",".join(
                    [
                        "<div class='subitem'>"
                        + self.cs_type.get_admin_preview_object(v, *args, **kwargs)
                        + "</div>"
                        for v in value
                    ]
                )
            )
            + "]"
        )


class Keys(BaseEach):
    def __init__(self, **kwargs):
        self.cs_types = kwargs

    def validate(self, value):
        for k, v in value.items():
            if k not in self.cs_types:
                continue
            try:
                self.cs_types[k].validate(v)
            except ValidationError as e:
                raise ValidationError(f"key {k}: {e.message}")

        for k, v in self.cs_types.items():
            if k not in value:
                if v.default == required:
                    raise ValidationError(f"Missing required key {k}")

    def to_python(self, value):
        ret = {}
        for k, v in value.items():
            if k in self.cs_types:
                try:
                    ret[k] = self.cs_types[k].to_python(v)
                except ValidationError as e:
                    raise ValidationError(f"key {k}: {e.message}")
            else:
                ret[k] = v

        for k, v in self.cs_types.items():
            if k not in ret and v.default not in (optional, required):
                ret[k] = v.to_python(v.default)

        return ret

    def give_python_to_admin(self, value, name, **kwargs):
        ret = {}
        for k, v in value.items():
            if k in self.cs_types:
                try:
                    ret[k] = self.cs_types[k].give_python_to_admin(v, name, **kwargs)
                except ValidationError as e:
                    raise ValidationError(f"key {k}: {e.message}")
            else:
                ret[k] = v

        for k, v in self.cs_types.items():
            if k not in ret and v.default not in (optional, required):
                ret[k] = v.give_python_to_admin(v.default, name, **kwargs)

        return ret

    def get_help_format(self):
        yield "A dictionary. Keys: "
        for k, v in self.cs_types.items():
            yield "<div class='subitem'>"
            yield f"<i>{k}</i> - "
            if v.default == required:
                yield "(required) "
            elif v.default == optional:
                yield "(optional) "
            else:
                yield f"(default: {v.default if v.default else '<i>empty</i>'}) "
            yield from v.get_help_format()
            yield "</div>"

    def give(self, value, suffix=None):
        return {
            k: self.cs_types[k].give(v, suffix) if k in self.cs_types else v
            for k, v in value.items()
        }

    def get_admin_preview_object(self, value, *args, **kwargs):
        def pre_format(val):
            "<pre>{}</pre>".format(pformat(value).replace("<", "&lt;"))

        return (
            "{"
            + ",".join(
                [
                    f"<div class='subitem'><i>{k}</i>: {self.cs_types[k].get_admin_preview_object(v, *args, **kwargs) if k in self.cs_types else pre_format(v)}</div>"
                    for k, v in value.items()
                ]
            )
            + "}"
        )


class EachMixin:
    admin_preview_as = PREVIEW_HTML
    each = None

    def process_each_validate(self, value):
        self.each.validate(value)

    def process_each_to_python(self, value):
        return self.each.to_python(value)

    def validate(self, value):
        super().validate(value)
        if value is None:
            return
        self.process_each_validate(value)

    def to_python(self, value):
        value = super().to_python(value)
        if value is None:
            return None
        return self.process_each_to_python(value)

    def get_help_format(self):
        yield from super().get_help_format()
        yield from self.each.get_help_format()

    def give(self, value, suffix=None):
        return self.each.give(value, suffix)

    def give_python_to_admin(self, value, *args, **kwargs):
        value = super().to_python(value)
        return self.each.give_python_to_admin(value, *args, **kwargs)

    def get_admin_preview_object(self, *args, **kwargs) -> str:
        return self.each.get_admin_preview_object(*args, **kwargs)
