"""
in the same way as python has functools, the module also has a few functions
to help with the function manipulation.
"""


def and_(*funcs):
    """
    Returns a function that performs an 'and' operation on multiple functions.
    """

    def _(*args, **kwargs):
        return all(func(*args, **kwargs) for func in funcs)

    return _


def or_(*funcs):
    """
    Returns a function that performs an 'or' operation on multiple functions.
    """

    def _(*args, **kwargs):
        return any(func(*args, **kwargs) for func in funcs)

    return _


def not_(func):
    """
    Returns a function that performs a 'not' operation on a function.
    """

    def _(*args, **kwargs):
        return not func(*args, **kwargs)

    return _
