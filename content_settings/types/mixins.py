from typing import Any, Optional, Union, Dict, Tuple, Iterable, Callable
from pprint import pformat
from decimal import Decimal

from django.core.exceptions import ValidationError
from django.utils.safestring import mark_safe
from django.utils.translation import gettext as _

from .validators import call_validator, PreviewValidator, PreviewValidationError
from . import PREVIEW, pre, TCallableStr
from ..utils import call_base_str

TNumber = Union[int, float, Decimal]


def mix(*cls):
    """
    Returns a mix of types. Mixins should go first and the last one should be the main type.

    Example:
    mix(HTMLMixin, SimpleInt)
    """
    return type("", cls, {})


class ProcessorsMixin:
    """
    Mixin that adds processors to the type.

    The processors is a pipeline of functions that are applied to the py object.
    """

    processors: Iterable[TCallableStr] = ()

    def get_processors(self):
        return self.processors

    def to_python(self, value: str) -> Any:
        py_value = super().to_python(value)
        for processor in self.get_processors():
            py_value = call_base_str(processor, py_value)
        return py_value


class GiveProcessorsMixin:
    """
    Mixin that adds processors to the type.
    """

    give_processors: Iterable[
        Union[TCallableStr, Tuple[Optional[str], TCallableStr]]
    ] = ()

    def get_give_processors(self):
        return self.give_processors

    def give(self, value: Any, suffix: Optional[str] = None):
        ret = super().give(value, suffix)

        for processor_pair in self.get_give_processors():
            if isinstance(processor_pair, tuple):
                processor_suffix, processor_func = processor_pair
            else:
                processor_suffix = None
                processor_func = processor_pair

            if processor_suffix == suffix:
                ret = call_base_str(processor_func, ret)

        return ret


class ToRawProcessorsMixin:
    """
    Mixin that adds to_raw processor to the type.
    """

    to_raw_processor: Optional[Callable] = None
    to_raw_processor_suffixes: Optional[Dict[str, Callable]] = None

    def to_raw(self, value: Any, suffix: Optional[str] = None) -> str:
        if suffix is None:
            if self.to_raw_processor is None:
                return super().to_raw(value, suffix)
            else:
                return self.to_raw_processor(value)
        else:
            if self.to_raw_processor_suffixes is None:
                return super().to_raw(value, suffix)
            else:
                return self.to_raw_processor_suffixes[suffix](value)


class MinMaxValidationMixin:
    """
    Mixin that validates that value is between min_value and max_value.

    Attributes:
    min_value: Minimum value. If None, then no minimum value.
    max_value: Maximum value. If None, then no maximum value.
    """

    min_value: Optional[TNumber] = None
    max_value: Optional[TNumber] = None

    def validate(self, value):
        super().validate(value)

        is_none_valid = self.min_value is None and self.max_value is None
        if not is_none_valid and value is None:
            raise ValidationError(_("Value cannot be None"))

        if self.min_value is not None and value < self.min_value:
            raise ValidationError(
                _("Value cannot be less than %(min_value)s")
                % {"min_value": self.min_value}
            )

        if self.max_value is not None and value > self.max_value:
            raise ValidationError(
                _("Value cannot be greater than %(max_value)s")
                % {"max_value": self.max_value}
            )

    def get_help_format(self):
        yield from super().get_help_format()

        if self.min_value is not None:
            yield f" from {self.min_value}"

        if self.max_value is not None:
            yield f" to {self.max_value}"


class EmptyNoneMixin:
    """
    Mixin for types that returns None if value is empty string.

    Works only for `value_required=False`
    """

    def to_python(self, value):
        if not value and not self.value_required:
            return None
        return super().to_python(value)

    def validate_value(self, value: str):
        if not value and not self.value_required:
            return
        super().validate_value(value)


class HTMLMixin:
    """
    Mixin for types that should be displayed in HTML format.
    And also returned content should be marked as safe.
    """

    admin_preview_as: PREVIEW = PREVIEW.HTML

    def get_help_format(self):
        yield from super().get_help_format()
        yield " "
        yield _("in HTML format")

    def give(self, value, suffix=None):
        return mark_safe(super().give(value, suffix))


class PositiveValidationMixin(MinMaxValidationMixin):
    """
    Mixin that validates that value is positive.
    """

    min_value = 0


class CallToPythonMixin:
    """
    Mixin for callable types, or types that should be called to get the value.
    """

    call_func_argument_name: str = "prepared"
    call_func: TCallableStr = staticmethod(
        lambda *args, prepared=None, **kwargs: prepared(*args, **kwargs)
    )
    call_prepare_func: TCallableStr = staticmethod(lambda value: value)

    def get_call_prepare_func(self) -> TCallableStr:
        return self.call_prepare_func

    def prepare_python_call(self, value: Any) -> Dict[str, Any]:
        return {
            self.call_func_argument_name: call_base_str(
                self.get_call_prepare_func(), value
            )
        }

    def get_call_func(self) -> TCallableStr:
        return self.call_func

    def python_call(self, *args, **kwargs):
        return call_base_str(self.get_call_func(), *args, **kwargs)

    def get_preview_validators(self):
        return [validator for validator in self.get_validators()]

    def to_python(self, value):
        value = super().to_python(value)
        prepared_kwargs = self.prepare_python_call(value)

        def ret(*args, **kwargs):
            return self.python_call(*args, **prepared_kwargs, **kwargs)

        return ret

    def give_python_to_admin(self, value, name, **kwargs):
        try:
            value = self.to_python(value)
        except Exception as e:
            return [(None, e)]
        ret = []
        for validator in self.get_preview_validators():
            has_call_representation = getattr(
                validator, "has_call_representation", False
            )
            if has_call_representation:
                str_validator = f"{name}({str(validator)})"
            else:
                str_validator = f"{name}(???)"

            try:
                ret_validator = validator(value)
            except PreviewValidationError as e:
                ret.append((f"{name}({e.preview_input})", e))
            except Exception as e:
                ret.append((str_validator, e))
            else:
                if isinstance(ret_validator, PreviewValidator):
                    ret.append(
                        (
                            f"{name}({ret_validator.preview_input})",
                            ret_validator.preview_output,
                        )
                    )
                elif has_call_representation:
                    ret.append((str_validator, ret_validator))
        return ret

    def get_admin_preview_object(self, value, name, **kwargs):
        admin_preview_as = self.get_admin_preview_as()
        if admin_preview_as == PREVIEW.NONE:
            return ""

        if not value:
            return _("No preview (add at least one call_validator in validators)")

        if len(value) == 1 and admin_preview_as in (PREVIEW.TEXT, PREVIEW.HTML):
            value = value[0][1]
            if isinstance(value, Exception):
                return f"ERROR!!! {value}"
            if admin_preview_as == PREVIEW.TEXT:
                return pre(value)
            else:
                return str(value)

        def f():
            for validator, val in value:
                if validator is not None:
                    yield pre(f">>> {validator}")

                if isinstance(val, Exception):
                    yield f"ERROR!!! {val}"
                else:
                    if admin_preview_as == PREVIEW.TEXT:
                        yield pre(val)
                    elif admin_preview_as == PREVIEW.HTML:
                        yield str(val)
                    else:
                        yield pre("<<< " + pformat(val))

        return "\n".join(f())


class GiveCallMixin:
    """
    Mixin for callable types, but result of the call without artuments should be returned.

    If suffix is "call" then callable should be returned.
    """

    def get_suffixes_names(self, value: Any):
        return ("call",) + super().get_suffixes_names(value)

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
    """
    Mixin for non-callable python objects will be returned as callable given.

    Can be usefull when you change callable types to a simple type but don't want to change the code that uses that type.
    """

    def get_suffixes_names(self, value: Any):
        return ("call",) + super().get_suffixes_names(value)

    def give_python_to_admin(self, value, name, **kwargs):
        return self.give_python(value)()

    def give(self, value, suffix=None):
        return lambda *args, **kwargs: value


class AdminPreviewMenuMixin:
    """
    Mixin that adds a menu to the admin preview.
    """

    def gen_admin_preview_html_menu_items(self, value: Any, name: str, **kwargs) -> str:
        return
        yield

    def get_admin_preview_html_menu(self, value: Any, name: str, **kwargs) -> str:
        html_items = "".join(
            self.gen_admin_preview_html_menu_items(value, name, **kwargs)
        )
        if not html_items:
            return ""
        return "<div>" + html_items + "</div>"

    def get_admin_preview_object(self, value: Any, name: str, **kwargs) -> str:

        return self.get_admin_preview_html_menu(
            value, name, **kwargs
        ) + self.get_admin_preview_under_menu_object(value, name, **kwargs)

    def get_admin_preview_under_menu_object(
        self, value: Any, name: str, **kwargs
    ) -> str:
        return super().get_admin_preview_object(value, name, **kwargs)


class AdminSuffixesMixinPreview:
    admin_preview_suffixes = None
    admin_preview_suffixes_default = "default"

    def get_admin_preview_suffixes_default(self):
        return self.admin_preview_suffixes_default

    def get_admin_preview_suffixes(self, value: Any, name: str, **kwargs):
        return (
            self.get_suffixes_names(value)
            if self.admin_preview_suffixes is None
            else self.admin_preview_suffixes
        )

    def gen_admin_preview_html_menu_items(
        self, value: Any, name: str, suffix: Optional[str] = None, **kwargs
    ) -> str:
        suffixes = self.get_admin_preview_suffixes(value, name, **kwargs)
        if not len(suffixes):
            return

        for suf in (None, *suffixes):
            if suf == suffix:
                yield f" <b>{suf or self.get_admin_preview_suffixes_default()}</b> "
            elif suf is None:
                yield f' <a class="cs_set_params">{self.get_admin_preview_suffixes_default()}</a> '
            else:
                yield f' <a class="cs_set_params" data-param-suffix="{suf}">{suf}</a> '

        yield from super().gen_admin_preview_html_menu_items(
            value, name, suffix=suffix, **kwargs
        )

    def get_admin_preview_under_menu_object(
        self, value: Any, name: str, **kwargs
    ) -> str:
        suffix = kwargs.get("suffix", None)
        return super().get_admin_preview_under_menu_object(
            self.give(value, suffix), name, **kwargs
        )


class AdminPreviewSuffixesMixin(AdminSuffixesMixinPreview, AdminPreviewMenuMixin):
    """
    Mixin shows links to preview different suffixes of the value in the admin preview.
    """

    pass


class ActionResponse(dict):
    def error(self, message):
        self["error"] = message
        return self

    def html(self, html):
        self["html"] = html
        return self

    def alert(self, message):
        self["alert"] = message
        return self

    def value(self, value):
        self["value"] = value
        return self

    def before_html(self, html):
        self["before_html"] = html
        return self


class AdminActionsMixinPreview:
    """
    Mixin that adds actions to the admin preview.
    """

    admin_preview_actions = None

    def gen_admin_preview_html_menu_items(
        self, value: Any, name: str, suffix: Optional[str] = None, **kwargs
    ) -> str:
        if self.admin_preview_actions is None:
            return

        for i, (action_name, _) in enumerate(self.admin_preview_actions):
            yield f' <a class="cs_set_params cs_set_params_once" data-param-action="{i}">{action_name}</a> '

    def get_admin_preview_function(self, *args, **kwargs):
        if self.admin_preview_actions is None:
            return

        action_name = kwargs.get("action", None)
        if action_name is None:
            return

        try:
            return self.admin_preview_actions[int(action_name)][1]
        except (IndexError, ValueError):
            return

    def process_action(self, *args, **kwargs):
        func = self.get_admin_preview_function(*args, **kwargs)
        if func is None:
            return

        response = ActionResponse()
        func(response, *args, _cs_type=self, **kwargs)
        return response

    def get_full_admin_preview_value(self, *args, **kwargs) -> str:
        response = self.process_action(*args, **kwargs)
        if not response:
            return super().get_full_admin_preview_value(*args, **kwargs)

        response = dict(response)

        before_html = response.pop("before_html", "")
        if before_html:
            response = {
                **response,
                **super().get_full_admin_preview_value(*args, **kwargs),
            }
            response["html"] = before_html + response["html"]

        return response


class AdminPreviewActionsMixin(AdminActionsMixinPreview, AdminPreviewMenuMixin):
    pass
