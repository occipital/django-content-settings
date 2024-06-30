"""
Functions that can be used as filters for the `DEFAULTS` setting.

Each function has a single attribute *settings type* and should return a boolean.
"""

from typing import Callable, Type

from content_settings.types import BaseSetting
from content_settings.utils import class_names

TFilter = Callable[[Type[BaseSetting]], bool]


def any_name(cls: Type[BaseSetting]) -> bool:
    """
    Allow all settings.
    """
    return True


def name_exact(name: str) -> TFilter:
    """
    Allow only settings with the exact type name or parent type name.

    Args:
        name (str): The exact name to match.
    """

    def f(cls: Type[BaseSetting]) -> bool:
        return any(name == el[1] for el in class_names(cls))

    return f


def full_name_exact(name: str) -> TFilter:
    """
    Allow only settings with the exact full type name or parent type name. The name includes module name.

    Args:
        name (str): The exact full name to match, including the module.

    """

    def f(cls: Type[BaseSetting]) -> bool:
        return any(name == f"{el[0]}.{el[1]}" for el in class_names(cls))

    return f
