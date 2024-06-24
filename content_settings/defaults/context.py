from contextlib import contextmanager
from typing import Iterator, Set

from content_settings.settings import DEFAULTS as DEFAULTS_SETTINGS
from content_settings.types import BaseSetting
from content_settings.defaults.modifiers import TModifier

from .filters import any_name
from .modifiers import set_if_missing, add_tags, help_prefix, help_suffix


DEFAULTS = [*DEFAULTS_SETTINGS]


@contextmanager
def defaults(*args, **kwargs):
    """
    Context manager for setting defaults.
    """
    DEFAULTS.insert(0, (any_name, *args, set_if_missing(**kwargs)))
    try:
        yield
    finally:
        DEFAULTS.pop(0)


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
