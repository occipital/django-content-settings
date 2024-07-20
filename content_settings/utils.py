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
    parts = path.split(".")
    module = import_module(".".join(parts[:-1]))
    return getattr(module, parts[-1])


def function_has_argument(func: Callable, arg: str) -> bool:
    """
    Check if the function has the given argument in its definition.
    """
    return arg in inspect.signature(func).parameters


def func_base_str(func: TCallableStr, call_base: Any = None) -> Callable:
    """
    if a given function is not callable it is converted into callable function
    """
    if callable(func):
        return func

    if "." in func:
        return import_object(func)

    assert (
        call_base
    ), "the first argument can not be empty if the first argument a name of the function"
    if isinstance(call_base, str):
        call_base = import_object(call_base)

    return getattr(call_base, func)


def call_base_str(func: TCallableStr, *args, call_base: Any = None, **kwargs) -> Any:
    """
    The goal of the function is to extend interface of callable attributes, so instead of passing a function you can pass a name of the function or full import path to the function.

    It is not only minimise the amout of import lines but also allows to use string attributes in `CONTENT_SETTINGS_DEFAULTS`.
    """

    func = func_base_str(func, call_base)

    if function_has_argument(func, "call_base"):
        kwargs["call_base"] = call_base

    return func(*args, **kwargs)
