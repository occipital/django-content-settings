def any(user):
    return True


def none(user):
    return False


def authenticated(user):
    return user.is_authenticated


def staff(user):
    return user.is_active and user.is_staff


def superuser(user):
    return user.is_active and user.is_superuser


def has_perm(perm):
    def _(user):
        return user.is_active and user.has_perm(perm)

    return _


def and_(*funcs):
    def _(user):
        return all(func(user) for func in funcs)

    return _


def or_(*funcs):
    def _(user):
        return any(func(user) for func in funcs)

    return _


def not_(func):
    def _(user):
        return not func(user)

    return _
