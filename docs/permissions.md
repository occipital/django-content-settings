# Permissions

## Overview

The `content_settings.permissions` *([source](source.md#permissions))* module in Django provides functions that can be used as arguments for the permission attributes of your settings, such as:

- `fetch_permission`: Controls API access to variables through `views.FetchSettingsView`.
- `update_permission`: Restricts the ability to change a variable in the admin panel.
- `view_permission`: Determines who can see the variable in the admin panel (it will not be listed for unauthorized users).
- `view_history_permission`: Governs access to the history of changes for a variable. This is the only permission where `None` is allowed; in such cases, the permission defaults to `view_permission`.

---

## Functions in the Module

### `any`

Allows access for all users.

### `none`

Denies access to all users.

### `authenticated`

Grants access only to authenticated users.

### `staff`

Restricts access to staff users.

### `superuser`

Restricts access to superusers.

### `has_perm(perm)`

Allows access to users with a specific permission.

**Example**:

```python
has_perm('app_label.permission_codename')
```

---

## Functions from `functools` Module

### `and_(*funcs)`

Combines multiple permission functions using a logical AND.

**Example**:

```python
and_(authenticated, has_perm('app_label.permission_codename'))
```

### `or_(*funcs)`

Combines multiple permission functions using a logical OR.

**Example**:

```python
or_(staff, has_perm('app_label.permission_codename'))
```

### `not_(*funcs)`

Applies a logical NOT to the given permission functions.

---

## Usage Examples

### Example 1: Setting Multiple Permissions

Restrict a variable so that only staff members or users with a specific permission can update it:

```python
from content_settings.types.basic import SimpleString, SimpleDecimal
from content_settings.permissions import staff, has_perm
from content_settings.functools import or_

TITLE = SimpleString(
    "default value",
    update_permission=or_(staff, has_perm("app_label.permission_codename"))
)

MAX_PRICE = SimpleDecimal(
    "9.99",
    fetch_permission=staff,
)
```

In this example:
- `TITLE` can be updated by either staff members or users with the specified permission.
- `MAX_PRICE` can only be fetched by staff members.

---

### Example 2: Using Permission Names Instead of Functions

You can use permission names directly if they are defined in the `content_settings.permissions` module:

```python
from content_settings.types.basic import SimpleString, SimpleDecimal
from content_settings.permissions import has_perm
from content_settings.functools import or_

TITLE = SimpleString(
    "default value",
    update_permission=or_("staff", has_perm("app_label.permission_codename"))
)

MAX_PRICE = SimpleDecimal(
    "9.99",
    fetch_permission="staff",
)
```

Alternatively, use the full import path for custom permissions:

```python
from content_settings.types.basic import SimpleDecimal

MAX_PRICE = SimpleDecimal(
    "9.99",
    fetch_permission="my_project.permissions.main_users",
)
```

---

[![Stand With Ukraine](https://raw.githubusercontent.com/vshymanskyy/StandWithUkraine/main/banner-direct-single.svg)](https://stand-with-ukraine.pp.ua)
