[![Stand With Ukraine](https://raw.githubusercontent.com/vshymanskyy/StandWithUkraine/main/banner-direct-single.svg)](https://stand-with-ukraine.pp.ua)

# Permissions

## Overview

The `content_settings.permissions` *([source](https://github.com/occipital/django-content-settings/blob/master/content_settings/permissions.py))* module in Django provides functions that can be used as arguments for the  permission attributes of your types. Such as:

* `fetch_permission` - permission for API access to the variables through the URLS `/content-settings/fetch/*/` and `views.FetchSettingsView`
* `update_permission` - permission to change the variable in the admin panel
* `view_permission` - permission to see the variable in the admin panel (it woudn't be listed for those who are not allowed)
* `view_history_permission` - permission to see the history of changes for the variable. It is the only permission where None is allowed, in that case the permission will be taken from `view_permission`

### Functions in the Module

#### `any`

Allows access to every user.

#### `none`

Denies access to all users.

#### `authenticated`

Allows access only to authenticated users.

#### `staff`

Restricts access to staff users.

#### `superuser`

Restricts access to staff users.

#### `has_perm(perm)`

Allows access to users with a specific permission.

**Example**:

```python
has_perm('app_label.permission_codename')
```

#### `and_(*funcs)`

Combines multiple permission functions using a logical AND.

**Example**:

```python
and_(authenticated, has_perm('app_label.permission_codename'))
```


#### `or_(*funcs)`

Combines multiple permission functions using a logical OR.

**Example**:

```python
or_(staff, has_perm('app_label.permission_codename'))
```


#### `not_(*funcs)`

Logical NOT.

### Usage examples

To set a permission where only staff members or users with a specific permission can update a variable:

```python
from content_settings.types.basic import SimpleString, SimpleDecimal
from content_settings.permissions import or_, staff, has_perm

TITLE = SimpleString(
    "default value",
    update_permission=or_(staff, has_perm('app_label.permission_codename'))
)

MAX_PRICE = SimpleDecimal(
    "9.99",
    fetch_permission=staff,
)
```

In this example, `SOME_VARIABLE` can be updated either by staff members or by users who have the specified permission and `MAX_PRICE` can be fetched by only staff

---

This documentation provides an overview of the `content_settings.permissions` module, offering versatile and straightforward functions to manage permissions in Django applications effectively.
