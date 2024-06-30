# defaults

The defaults context in Django content settings allows you to group settings with common parameters, reducing redundancy and making your code cleaner and more maintainable. This is particularly useful as the number of settings grows, allowing you to manage shared parameters efficiently.

## Use Cases

### Group Settings by Common Parameters

When defining multiple settings with the same parameters, you can use the defaults context to avoid repetition.

Example without using `defaults` context:

```python
from content_settings.types.basic import SimpleString, SimpleBool
from content_settings.permissions import superuser

SITE_TITLE = SimpleString("Songs", update_permission=superuser, tags=["caution"])
SITE_TAG_LINE = SimpleString("Super Songs", update_permission=superuser, tags=["caution"])
SITE_DEV_MODE = SimpleBool("0", update_permission=superuser, tags=["caution"])
```

Those are 3 settings, we don't want to allow anyone to edit, so we have to repeat the same parameters for each settings. Using defaults you can group the setting and set parameters for the group instead of the each setting.

The same example, but using context `defaults`

```python
from content_settings.types.basic import SimpleString, SimpleBool
from content_settings.permissions import superuser
from content_settings.defaults.context import defaults

with defaults(update_permission=superuser, tags=["caution"]):
    SITE_TITLE = SimpleString("Songs")
    SITE_TAG_LINE = SimpleString("Super Songs")
    SITE_DEV_MODE = SimpleBool("0")
```

Context `defaults` changes default parameters for the setting inside the context. So when you set the parameter in the setting - it always rewrites the default value.

For example, for `SITE_TAG_LINE` you want lower permissions

```python
from content_settings.types.basic import SimpleString, SimpleBool
from content_settings.permissions import superuser, staff
from content_settings.defaults.context import defaults

with defaults(update_permission=superuser, tags=["caution"]):
    SITE_TITLE = SimpleString("Songs")
    SITE_TAG_LINE = SimpleString("Super Songs", update_permission=staff)
    SITE_DEV_MODE = SimpleBool("0")
```

# Nested defaults contexts

You can have context inside context, in that case defaults for internal context overwrites/updates values for external context.

The same example but using two level of context

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

So `SITE_TAG_LINE` will take `update_permission=staff` from internal context and `tags=["caution"]` from external context.

### Update parameters

The defaults context allows you to override and update default parameters for settings. This means you can add additional parameters, such as more tags or extra help text, on top of what is already defined.

For example you want to add tag `"caution"` to all of the settings inside the context. That means they can have own additional set of tags, and you want to add on top of what is set

Example without `defaults` context:

```python
from content_settings.types.basic import SimpleString, SimpleBool

SITE_TITLE = SimpleString("Songs", tags=["caution", "seo"])
SITE_TAG_LINE = SimpleString("Super Songs", tags=["caution", "ui"])
SITE_DEV_MODE = SimpleBool("0", tags=["caution", "dev"])
```

in that case you should use specific modifier `unite_set_add`

```python
from content_settings.types.basic import SimpleString, SimpleBool
from content_settings.defaults.context import defaults
from content_settings.defaults.modifiers import unite_set_add

with defaults(unite_set_add(tags=["caution"])):
    SITE_TITLE = SimpleString("Songs", tags=["seo"])
    SITE_TAG_LINE = SimpleString("Super Songs", tags=["ui"])
    SITE_DEV_MODE = SimpleBool("0", tags=["dev"])
```

both examples will work the same. Context in the second example add tag `"caution"` to all of the settings inside the context

The context:

```python
from content_settings.defaults.context import defaults
from content_settings.defaults.modifiers import unite_set_add

with defaults(unite_set_add(tags=["caution"])):
```

can be simplified to:

```python
from content_settings.defaults.context import defaults
from content_settings.defaults.modifiers import add_tags

with defaults(add_tags(["caution"])):
    ...
```

or even:

```python
from content_settings.defaults.context import default_tags

with default_tags(["caution"])):
    ...
```

### Global Updates `CONTENT_SETTINGS_DEFAULTS`

Allows you to overwrite defaults globally. For example you want to use code highligh widget for all fields inherited from JSON.

```python
from content_settings.defaults.modifiers import set_if_missing
from content_settings.defaults.filters import full_name_exact

CONTENT_SETTINGS_DEFAULTS = [
    (full_name_exact("content_settings.types.markup.SimpleJSON"), set_if_missing(widget=SomeCodeWidget)),
]
```

or you want to set for all Python fields (which are all SimpleEval and SimpleExec) children

```python
from content_settings.permissions import superuser
from content_settings.functools import _or
from content_settings.filters import full_name_exact
from content_settings.defaults.modifiers import set_if_missing

CONTENT_SETTINGS_DEFAULTS = [
    (_or(
        full_name_exact("content_settings.types.template.SimpleEval"),
        full_name_exact("content_settings.types.template.SimpleExec"),
    ), set_if_missing(update_permission=superuser)),
]
```