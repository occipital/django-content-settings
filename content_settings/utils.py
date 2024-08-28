"""
A set of available utilites
"""

from typing import Iterator, Tuple, Type, Any, Callable, Union

import inspect
from importlib import import_module

from content_settings.types import BaseSetting, TCallableStr


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


def import_object(path: str) -> Any:
    """
    getting an object from the module by the path. `full.path.to.Object` -> `Object`
    """
    try:
        return import_module(path)
    except ImportError:
        parts = path.split(".")
        module = import_module(".".join(parts[:-1]))
        return getattr(module, parts[-1])


def function_has_argument(func: Callable, arg: str) -> bool:
    """
    Check if the function has the given argument in its definition.
    """
    return arg in inspect.signature(func).parameters


def is_bline(func: TCallableStr) -> bool:
    """
    Check if it is a string defined as b"string", or is other words bites string.

    The function is part of the future idea https://github.com/occipital/django-content-settings/issues/110
    """
    return isinstance(func, bytes)


def obj_base_str(obj: Any, call_base: Any = None) -> Callable:
    """
    if a given obj is not String - return the obj. If it is string than try to find it using call_base
    """
    if is_bline(obj):
        obj = obj.decode("utf-8")

    if not isinstance(obj, str):
        return obj

    if "." in obj:
        return import_object(obj)

    assert (
        call_base
    ), "the first argument can not be empty if the first argument a name of the function"
    if isinstance(call_base, str):
        call_base = import_object(call_base)

    return getattr(call_base, obj)


def call_base_str(func: TCallableStr, *args, call_base: Any = None, **kwargs) -> Any:
    """
    The goal of the function is to extend interface of callable attributes, so instead of passing a function you can pass a name of the function or full import path to the function.

    It is not only minimise the amout of import lines but also allows to use string attributes in `CONTENT_SETTINGS_DEFAULTS`.
    """

    func = obj_base_str(func, call_base)

    if function_has_argument(func, "call_base"):
        kwargs["call_base"] = call_base

    return func(*args, **kwargs)
