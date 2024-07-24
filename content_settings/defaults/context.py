from contextlib import contextmanager
from typing import Iterator, Set, Dict, Any

from content_settings.settings import DEFAULTS as DEFAULTS_SETTINGS
from content_settings.types import BaseSetting
from content_settings.defaults.modifiers import TModifier

from .filters import any_name
from .modifiers import set_if_missing, add_tags, help_prefix, help_suffix, NotSet


DEFAULTS = [*DEFAULTS_SETTINGS]


@contextmanager
def defaults(*args, **kwargs):
    """
    Context manager for setting defaults.
    """
    DEFAULTS.append((any_name, *args, set_if_missing(**kwargs)))
    try:
        yield
    finally:
        DEFAULTS.pop()


@contextmanager
def default_tags(tags: Set[str]):
    """
    defaults context for setting default tags.
    """
    with defaults(add_tags(tags)):
        yield


@contextmanager
def default_help_prefix(prefix: str):
    """
    defaults context for setting default help prefix.
    """
    with defaults(help_prefix(prefix)):
        yield


@contextmanager
def default_help_suffix(suffix: str):
    """
    defaults context for setting default help suffix.
    """
    with defaults(help_suffix(suffix)):
        yield


def defaults_modifiers(setting: BaseSetting) -> Iterator[TModifier]:
    """
    Generator for all modifiers for the given setting.
    """
    for modifier in DEFAULTS:
        if not modifier[0](setting.__class__):
            continue
        yield from modifier[1:]


def update_defaults(setting: BaseSetting, kwargs: Dict[str, Any]):
    """
    Update paramas of the setting type by applying all of the modifiers from the defaults context.
    """
    type_kwargs = {
        name: getattr(setting, name)
        for name in dir(setting)
        if setting.can_assign(name)
    }
    updates = {}
    for modifier in defaults_modifiers(setting):
        updates.update(modifier(type_kwargs, updates, kwargs))

    if not updates:
        return kwargs

    return {
        **kwargs,
        **{
            k: v
            for k, v in updates.items()
            if setting.can_assign(k) and v is not NotSet and type_kwargs[k] != v
        },
    }
