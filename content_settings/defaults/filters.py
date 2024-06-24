"""
A functions that can be used as a filter for `DEFAULTS` setting.

Each function has the only attribute *settings type* and should return bool
"""

from typing import Callable, Type

from content_settings.types import BaseSetting
from content_settings.utils import class_names

TFilter = Callable[[Type[BaseSetting]], bool]


def any_name(cls: BaseSetting) -> bool:
    """
    Allow all settings
    """
    return True


def name_exact(name: str) -> TFilter:
    """
    Allow only settings with the exact name
    """

    def f(cls: BaseSetting) -> bool:
        return any(name == el[1] for el in class_names(cls))

    return f


def full_name_exact(name: str) -> TFilter:
    """
    Allow only settings with the exact name
    """

    def f(cls: BaseSetting) -> bool:
        return any(name == f"{el[0]}.{el[1]}" for el in class_names(cls))

    return f
