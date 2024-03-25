"""
EachMixin is the main mixin of the module, which allows types to have subtypes, that check, preview and converts the structure of the value.

For example `array.TypedStringsList`
"""

from enum import Enum, auto
from typing import Union, Any

from django.core.exceptions import ValidationError

from . import required, optional, PREVIEW, pre, BaseSetting


class BaseEach:
    def is_each(self, value: Any):
        return True

    def validate(self, value: Any):
        if not self.is_each(value):
            return
        self.each_validate(value)

    def to_python(self, value: Any):
        if not self.is_each(value):
            return value
        return self.each_to_python(value)

    def give(self, value: Any, suffix=None):
        if not self.is_each(value):
            return value
        return self.each_give(value, suffix)

    def give_python_to_admin(self, value: Any, name, **kwargs):
        if not self.is_each(value):
            return value
        return self.each_give_python_to_admin(value, name, **kwargs)

    def get_admin_preview_object(self, value, *args, **kwargs):
        if not self.is_each(value):
            return pre(value)
        return self.each_get_admin_preview_object(value, *args, **kwargs)


TCSType = Union[BaseEach, BaseSetting]


class Item(BaseEach):
    """
    Converts each element of the array into a specific type `cs_type`
    """

    def __init__(self, cs_type: TCSType):
        self.cs_type = cs_type

    def is_each(self, value: Any):
        return isinstance(value, (list, tuple))

    def each_validate(self, value):
        for i, v in enumerate(value, start=1):
            try:
                self.cs_type.validate(v)
            except ValidationError as e:
                raise ValidationError(f"item #{i}: {e.message}")

    def each_to_python(self, value):
        ret = []
        for i, v in enumerate(value, start=1):
            try:
                ret.append(self.cs_type.to_python(v))
            except ValidationError as e:
                raise ValidationError(f"item #{i}: {e.message}")
        return ret

    def each_give_python_to_admin(self, value, name, **kwargs):
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

    def each_give(self, value, suffix=None):
        return [self.cs_type.give(v, suffix) for v in value]

    def each_get_admin_preview_object(self, value, *args, **kwargs):
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
    """
    Converts values of the specific keys into specific types `cs_types`
    """

    def __init__(self, **kwargs: dict[str, TCSType]):
        self.cs_types = kwargs

    def is_each(self, value):
        return isinstance(value, dict)

    def each_validate(self, value):
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

    def each_to_python(self, value):
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

    def each_give_python_to_admin(self, value, name, **kwargs):
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

    def each_give(self, value, suffix=None):
        return {
            k: self.cs_types[k].give(v, suffix) if k in self.cs_types else v
            for k, v in value.items()
        }

    def each_get_admin_preview_object(self, value, *args, **kwargs):
        return (
            "{"
            + ",".join(
                [
                    f"<div class='subitem'><i>{k}</i>: {self.cs_types[k].get_admin_preview_object(v, *args, **kwargs) if k in self.cs_types else pre(v)}</div>"
                    for k, v in value.items()
                ]
            )
            + "}"
        )


class Values(BaseEach):
    """
    Converts each value of the given dict into `cs_type`
    """

    def __init__(self, cs_type: TCSType):
        self.cs_type = cs_type

    def is_each(self, value):
        return isinstance(value, dict)

    def each_validate(self, value):
        for k, v in value.items():
            try:
                self.cs_type.validate(v)
            except ValidationError as e:
                raise ValidationError(f"key {k}: {e.message}")

    def each_to_python(self, value):
        ret = {}

        for k, v in value.items():
            try:
                ret[k] = self.cs_type.to_python(v)
            except ValidationError as e:
                raise ValidationError(f"key {k}: {e.message}")

        return ret

    def each_give_python_to_admin(self, value, name, **kwargs):
        ret = {}

        for k, v in value.items():
            try:
                ret[k] = self.cs_type.give_python_to_admin(v, name, **kwargs)
            except ValidationError as e:
                raise ValidationError(f"key {k}: {e.message}")

        return ret

    def get_help_format(self):
        yield "A dictionary. Each value should be: "
        yield "<div class='subitem'>"
        yield from self.cs_type.get_help_format()
        yield "</div>"

    def each_give(self, value, suffix=None):
        return {k: self.cs_type.give(v, suffix) for k, v in value.items()}

    def each_get_admin_preview_object(self, value, *args, **kwargs):
        return (
            "{"
            + ",".join(
                [
                    f"<div class='subitem'><i>{k}</i>: {self.cs_type.get_admin_preview_object(v, *args, **kwargs)}</div>"
                    for k, v in value.items()
                ]
            )
            + "}"
        )


class EACH_SUFFIX(Enum):
    USE_OWN = auto()
    USE_PARENT = auto()
    SPLIT_OWN = auto()
    SPLIT_PARENT = auto()


class EachMixin:
    """
    Attributes:

    - `each` - the type of the subvalues.
    - `each_suffix_use` - how to use the suffixes. Can be `USE_OWN`, `USE_PARENT`, `SPLIT_OWN`, `SPLIT_PARENT`
    - `each_suffix_splitter` - the string that separates the suffixes. Applicable only when `each_suffix_use` is `SPLIT_OWN` or `SPLIT_PARENT`
    """

    admin_preview_as: PREVIEW = PREVIEW.HTML
    each: BaseEach = None
    each_suffix_use: EACH_SUFFIX = EACH_SUFFIX.USE_OWN
    each_suffix_splitter: str = "_by_"

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

    def get_each_suffix_splitter(self):
        return self.each_suffix_splitter

    def get_each_suffix_use(self):
        return self.each_suffix_use

    def get_help_format(self):
        yield from super().get_help_format()
        yield from self.each.get_help_format()

    def give_siffixes(self, value):
        if value is None:
            return None, None

        if self.get_each_suffix_use() == EACH_SUFFIX.USE_OWN:
            return value, None

        if self.get_each_suffix_use() == EACH_SUFFIX.USE_PARENT:
            return None, value

        splitter = self.get_each_suffix_splitter()
        if splitter not in value:
            if self.get_each_suffix_use() == EACH_SUFFIX.SPLIT_OWN:
                return value, None
            else:
                return None, value

        suffix, parent_suffix = value.split(splitter, 1)
        suffix = suffix
        return suffix, parent_suffix

    def give(self, value, suffix=None):
        suffix, each_suffix = self.give_siffixes(suffix)
        value = self.each.give(value, each_suffix)
        return super().give(value, suffix)

    def give_python_to_admin(self, value, *args, **kwargs):
        value = super().to_python(value)
        return self.each.give_python_to_admin(value, *args, **kwargs)

    def get_admin_preview_object(self, *args, **kwargs) -> str:
        return self.each.get_admin_preview_object(*args, **kwargs)
