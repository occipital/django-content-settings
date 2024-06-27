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
    with defaults(add_tags(tags)):
        yield


@contextmanager
def default_help_prefix(prefix: str):
    with defaults(help_prefix(prefix)):
        yield


@contextmanager
def default_help_suffix(suffix: str):
    with defaults(help_suffix(suffix)):
        yield


def defaults_modifiers(setting: BaseSetting) -> Iterator[TModifier]:
    """
    Get modifiers for specific class
    """
    for modifier in DEFAULTS:
        if not modifier[0](setting.__class__):
            continue
        yield from modifier[1:]


def update_defaults(setting: BaseSetting, kwargs: Dict[str, Any]):
    """
    Update paramas of the setting type by the collected modifiers
    """
    updates = {}
    for modifier in defaults_modifiers(setting):
        updates.update(modifier(updates, kwargs))

    return {
        **kwargs,
        **{
            k: v
            for k, v in updates.items()
            if setting.can_assign(k) and v is not NotSet
        },
    }
