"""
in the same way as python has functools, the module also has a few functions
to help with the function manipulation.
"""

from .utils import call_base_str


def and_(*funcs):
    """
    Returns a function that performs an 'and' operation on multiple functions.
    """

    def _(*args, call_base=None, **kwargs):
        return all(
            call_base_str(func, *args, call_base=call_base, **kwargs) for func in funcs
        )

    return _


def or_(*funcs):
    """
    Returns a function that performs an 'or' operation on multiple functions.
    """

    def _(*args, call_base=None, **kwargs):
        return any(
            call_base_str(func, *args, call_base=call_base, **kwargs) for func in funcs
        )

    return _


def not_(func):
    """
    Returns a function that performs a 'not' operation on a function.
    """

    def _(*args, call_base=None, **kwargs):
        return not call_base_str(func, *args, call_base=call_base, **kwargs)

    return _
