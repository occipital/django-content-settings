"""
A list of functions that are used as values for type attributes such as `fetch_permission`, `view_permission`, `update_permission`, and `view_history_permission`.
"""


def any(user):
    """
    Returns True for any user.
    """
    return True


def none(user):
    """
    Returns False for any user.
    """
    return False


def authenticated(user):
    """
    Returns True if the user is authenticated.
    """
    return user.is_authenticated


def staff(user):
    """
    Returns True if the user is active and a staff member.
    """
    return user.is_active and user.is_staff


def superuser(user):
    """
    Returns True if the user is active and a superuser.
    """
    return user.is_active and user.is_superuser


def has_perm(perm):
    """
    Returns a function that checks if the user has a specific permission.
    """

    def _(user):
        return user.is_active and user.has_perm(perm)

    return _


def and_(*funcs):
    """
    Returns a function that performs an 'and' operation on multiple functions.
    """

    def _(user):
        return all(func(user) for func in funcs)

    return _


def or_(*funcs):
    """
    Returns a function that performs an 'or' operation on multiple functions.
    """

    def _(user):
        return any(func(user) for func in funcs)

    return _


def not_(func):
    """
    Returns a function that performs a 'not' operation on a function.
    """

    def _(user):
        return not func(user)

    return _
