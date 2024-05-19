A list of functions that are used as values for type attributes such as `fetch_permission`, `view_permission`, `update_permission`, and `view_history_permission`.

# def any(user) [source](https://github.com/occipital/django-content-settings/blob/master/content_settings/permissions.py#L6)

Returns True for any user.

# def none(user) [source](https://github.com/occipital/django-content-settings/blob/master/content_settings/permissions.py#L13)

Returns False for any user.

# def authenticated(user) [source](https://github.com/occipital/django-content-settings/blob/master/content_settings/permissions.py#L20)

Returns True if the user is authenticated.

# def staff(user) [source](https://github.com/occipital/django-content-settings/blob/master/content_settings/permissions.py#L27)

Returns True if the user is active and a staff member.

# def superuser(user) [source](https://github.com/occipital/django-content-settings/blob/master/content_settings/permissions.py#L34)

Returns True if the user is active and a superuser.

# def has_perm(perm) [source](https://github.com/occipital/django-content-settings/blob/master/content_settings/permissions.py#L41)

Returns a function that checks if the user has a specific permission.

# def and_() [source](https://github.com/occipital/django-content-settings/blob/master/content_settings/permissions.py#L52)

Returns a function that performs an 'and' operation on multiple functions.

# def or_() [source](https://github.com/occipital/django-content-settings/blob/master/content_settings/permissions.py#L63)

Returns a function that performs an 'or' operation on multiple functions.

# def not_(func) [source](https://github.com/occipital/django-content-settings/blob/master/content_settings/permissions.py#L74)

Returns a function that performs a 'not' operation on a function.