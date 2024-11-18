# Defaults

The defaults context in Django content settings allows you to group settings with common parameters, reducing redundancy and making your code cleaner and more maintainable. This is especially useful as the number of settings grows, enabling you to manage shared parameters efficiently.

---

## Use Cases

### Group Settings by Common Parameters

When defining multiple settings with the same parameters, you can use the defaults context to avoid repetition.

#### Example Without Using `defaults` Context:

```python
from content_settings.types.basic import SimpleString, SimpleBool
from content_settings.permissions import superuser

SITE_TITLE = SimpleString("Songs", update_permission=superuser, tags=["caution"])
SITE_TAG_LINE = SimpleString("Super Songs", update_permission=superuser, tags=["caution"])
SITE_DEV_MODE = SimpleBool("0", update_permission=superuser, tags=["caution"])
```

This example repeats parameters for each setting. Using `defaults`, you can group settings and assign shared parameters.

#### Example Using the `defaults` Context:

```python
from content_settings.types.basic import SimpleString, SimpleBool
from content_settings.permissions import superuser
from content_settings.defaults.context import defaults

with defaults(update_permission=superuser, tags=["caution"]):
    SITE_TITLE = SimpleString("Songs")
    SITE_TAG_LINE = SimpleString("Super Songs")
    SITE_DEV_MODE = SimpleBool("0")
```

The `defaults` context changes default parameters for settings inside the block. If a parameter is explicitly set in a setting, it overrides the default value.

#### Example Overriding Defaults:

```python
from content_settings.types.basic import SimpleString, SimpleBool
from content_settings.permissions import superuser, staff
from content_settings.defaults.context import defaults

with defaults(update_permission=superuser, tags=["caution"]):
    SITE_TITLE = SimpleString("Songs")
    SITE_TAG_LINE = SimpleString("Super Songs", update_permission=staff)
    SITE_DEV_MODE = SimpleBool("0")
```

In this example, `SITE_TAG_LINE` uses `update_permission=staff`, while other settings use `update_permission=superuser`.

---

### Nested Defaults Contexts

You can nest `defaults` contexts. Inner contexts override or update parameters from outer contexts.

#### Example Using Nested Contexts:

```python
from content_settings.types.basic import SimpleString, SimpleBool
from content_settings.permissions import superuser, staff
from content_settings.defaults.context import defaults

with defaults(update_permission=superuser, tags=["caution"]):
    SITE_TITLE = SimpleString("Songs")
    SITE_DEV_MODE = SimpleBool("0")

    with defaults(update_permission=staff):
        SITE_TAG_LINE = SimpleString("Super Songs")
```

In this example, `SITE_TAG_LINE` uses `update_permission=staff` from the inner context and `tags=["caution"]` from the outer context.

---

### Update Parameters

You can use defaults to add or update parameters, such as tags or help text, without overwriting existing ones.

#### Example Adding Tags:

Without `defaults`:

```python
from content_settings.types.basic import SimpleString, SimpleBool

SITE_TITLE = SimpleString("Songs", tags=["caution", "seo"])
SITE_TAG_LINE = SimpleString("Super Songs", tags=["caution", "ui"])
SITE_DEV_MODE = SimpleBool("0", tags=["caution", "dev"])
```

With `defaults`:

```python
from content_settings.types.basic import SimpleString, SimpleBool
from content_settings.defaults.context import defaults
from content_settings.defaults.modifiers import unite_set_add

with defaults(unite_set_add(tags=["caution"])):
    SITE_TITLE = SimpleString("Songs", tags=["seo"])
    SITE_TAG_LINE = SimpleString("Super Songs", tags=["ui"])
    SITE_DEV_MODE = SimpleBool("0", tags=["dev"])
```

---

### Simplifying Defaults with Modifiers

```python
from content_settings.defaults.context import defaults
from content_settings.defaults.modifiers import add_tags

with defaults(add_tags(["caution"])):
    ...
```

Or even more simply:

```python
from content_settings.defaults.context import default_tags

with default_tags(["caution"]):
    ...
```

---

### Global Updates with `CONTENT_SETTINGS_DEFAULTS`

You can overwrite defaults globally. For example, to apply a code highlight widget for all fields inherited from JSON:

```python
from content_settings.defaults.modifiers import set_if_missing
from content_settings.defaults.filters import full_name_exact

CONTENT_SETTINGS_DEFAULTS = [
    (full_name_exact("content_settings.types.markup.SimpleJSON"), set_if_missing(widget=SomeCodeWidget)),
]
```

For applying settings to all Python fields (e.g., `SimpleEval` and `SimpleExec`):

```python
from content_settings.permissions import superuser
from content_settings.filters import full_name_exact
from content_settings.defaults.modifiers import set_if_missing
from content_settings.functools import _or

CONTENT_SETTINGS_DEFAULTS = [
    (_or(
        full_name_exact("content_settings.types.template.SimpleEval"),
        full_name_exact("content_settings.types.template.SimpleExec"),
    ), set_if_missing(update_permission=superuser)),
]
```

---

### Extend Yeses and Noes

The `defaults` context can modify default values like `yeses` for `SimpleBool`.

#### Example Extending Yeses:

```python
from content_settings.types.basic import SimpleBool
from content_settings.defaults.context import defaults
from content_settings.defaults.modifiers import unite_tuple_add

with defaults(unite_tuple_add(yeses=("tak",))):
    SITE_OPENED = SimpleBool("1")
```

Globally updating defaults for all `SimpleBool` settings:

```python
from content_settings.filters import full_name_exact
from content_settings.defaults.modifiers import unite_tuple_add

CONTENT_SETTINGS_DEFAULTS = [
    (full_name_exact("content_settings.types.basic.SimpleBool"), unite_tuple_add(yeses=("tak",))),
]
```

---

### Defaults Collections

In the module [`content_settings.defaults.collections`](source.md#defaultscollections), you can find prebuilt functions for common use cases.

#### Example Activating CodeMirror for Python:

```python
from content_settings.defaults.collections import codemirror_python

CONTENT_SETTINGS_DEFAULTS = [
    codemirror_python(),
]
```

#### Example Activating CodeMirror for All Supported Types:

```python
from content_settings.defaults.collections import codemirror_all

CONTENT_SETTINGS_DEFAULTS = [
    codemirror_all(),
]
```

---

[![Stand With Ukraine](https://raw.githubusercontent.com/vshymanskyy/StandWithUkraine/main/banner-direct-single.svg)](https://stand-with-ukraine.pp.ua)
