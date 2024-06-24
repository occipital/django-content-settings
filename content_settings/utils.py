"""
A set of available utilites
"""

import inspect
from typing import Iterator, Tuple, Type
from content_settings.types import BaseSetting


def classes(cls: BaseSetting) -> Iterator[Type[BaseSetting]]:
    """
    Returns an iterator of classes that are subclasses of the given class.
    """
    for cls in inspect.getmro(cls):
        if not cls.__name__:
            continue
        if cls.__module__ == "builtins":
            continue
        if (cls.__module__, cls.__name__) in (
            ("content_settings.types.basic", "BaseSetting"),
            ("content_settings.types.basic", "SimpleString"),
        ):
            continue
        yield cls


def classes_plus_self(cls: BaseSetting) -> Iterator[Type[BaseSetting]]:
    """
    Returns an iterator of classes that are subclasses of the given class and the given class itself.
    """
    yield from classes(cls)
    yield cls


def class_names(cls: Type[BaseSetting]) -> Iterator[Tuple[str, str]]:
    """
    Returns an iterator of tuple with module and class name that are subclasses of the given class.
    """
    for cls in classes_plus_self(cls):
        yield (cls.__module__, cls.__name__)
