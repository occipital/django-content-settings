# Using Variables in Your Project

## Introduction

This article describes how to use settings created with the `django-content-settings` module in various contexts, such as code, templates, and APIs.

## Creating a Variable

Let's start by creating a `MAX_PRICE` variable, which we will use for price validation:

```python
from content_settings.types.basic import SimpleDecimal

MAX_PRICE = SimpleDecimal("9.99", help="maximum allowed price in the store")
```

By default, if not altered in the admin panel, `MAX_PRICE` will return `Decimal("9.99")`.

## Access in Templates

Using variables in templates is straightforward. If you've added `content_settings.context_processors.content_settings` to your `context_processors`, you can access `content_settings.conf.content_settings` using `{{ CONTENT_SETTINGS }}`.

```html
<b>Max Price:</b> {{ CONTENT_SETTINGS.MAX_PRICE }}
```

## Access Through API

The content settings app provides built-in views for accessing your variables through APIs.

Below is an example of how to use it in your `urls.py`:

```python
from django.urls import path
from content_settings.views import FetchSettingsView

urlpatterns = [
    path("fetch/main/", FetchSettingsView.as_view(names=[
        "TITLE",
        "DESCRIPTION",
    ]), name="fetch_main"),
]
```

This defines an API that provides access to two variables, `TITLE` and `DESCRIPTION`. [Read more about APIs here](api.md).

Next, define permissions for the setting (i.e., who is allowed to read it). Use the `fetch_permission` attribute:

```python
from content_settings.types.basic import SimpleText

DESCRIPTION = SimpleText(
    "The best book store in the world",
    fetch_permission="any",  # <-- update
)
```

[Learn more about permissions here](permissions.md).

## Usage in Python Code

Variables are accessible via `content_settings` located in `content_settings.conf`.

### Example

```python
from decimal import Decimal
from content_settings.conf import content_settings

def update_price(request):
    new_price = Decimal(request.POST["price"])
    if new_price > content_settings.MAX_PRICE:
        raise ValueError("Price is too high")
    
    # ...
```

## Prefix

The `content_settings` object has a system of prefixes that allow you to apply specific functions to settings. A prefix is always lowercased and followed by a double underscore `__`.

```python
content_settings.prefix_name__SETTINGS_NAME
```

### `type__` - Accessing Variable Type

This prefix allows you to access the type object of a setting. For example:

```python
content_settings.type__MAX_PRICE.help
```

This returns the value of the `help` attribute of the setting.

### `lazy__` - Get a Lazy/Proxy Object of the Setting

When a variable is used in class or function attributes, use a lazy object with the `lazy__` prefix:

```python
from decimal import Decimal
from content_settings.conf import content_settings

def update_price(request, max_price=content_settings.lazy__MAX_PRICE):
    new_price = Decimal(request.POST["price"])
    if new_price > max_price:
        raise ValueError("Price is too high")
    
    # ...
```

**Why use `lazy__`?**

Without the `lazy__` prefix:

```python
def update_price(request, max_price=content_settings.MAX_PRICE):
    ...
```

This works fine until you change the value of the variable in the Django Admin panel. Without `lazy__`, the value of `max_price` remains unchanged, which is unexpected. With `lazy__`, the value updates dynamically when the variable changes in the admin panel.

The `lazy__` prefix returns a proxy object that fetches the value each time it's accessed.

### `withtag__` - Dictionary of Settings with a Specific Tag

For this prefix, replace `SETTING_NAME` with `TAG_NAME`.

Example:

```python
all_main = content_settings.withtag__MAIN
```

`all_main` is a dictionary where keys are setting names, and values are setting values.

### `startswith__` - Dictionary of Settings Starting with a Specific Value

Works similarly to the `withtag__` prefix:

```python
all_main = content_settings.startswith__MAIN
```

`all_main` contains all settings whose names start with "MAIN" as a dictionary.

### Custom Prefixes

You can register your own prefix using the `conf.register_prefix` decorator. [Learn more in the article about Possible Extensions](extends.md).

## Assign Values

You can assign values directly in the code (not just in the Admin Panel):

```python
content_settings.IS_OPEN = "-"
assert content_settings.IS_OPEN is False
```

**Note**:

- Assigned values are always strings (`raw_value`), but the returned value matches the type of the setting.
- The assignment process validates the value, which may take time.
- Assigning a
