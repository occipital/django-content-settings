"""
A set of available utilites
"""

import inspect
from typing import Iterator, Tuple, Type
from content_settings.types import BaseSetting


def classes(setting_cls: Type[BaseSetting]) -> Iterator[Type[BaseSetting]]:
    """
    Returns an iterator of classes that are subclasses of the given class.
    """
    for cls in inspect.getmro(setting_cls):

        if not cls.__name__ or not cls.__module__:
            continue
        if cls.__module__ == "builtins":
            continue
        if (cls.__module__, cls.__name__) in (
            ("content_settings.types", "BaseSetting"),
            ("content_settings.types.basic", "SimpleString"),
        ) and cls != setting_cls:
            continue
        yield cls


def class_names(setting_cls: Type[BaseSetting]) -> Iterator[Tuple[str, str]]:
    """
    Returns an iterator of tuple with module and class name that are subclasses of the given class.
    """
    for cls in classes(setting_cls):
        yield (cls.__module__, cls.__name__)
