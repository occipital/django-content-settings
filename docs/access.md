# Using Variables in Your Project

## Introduction

This article describes how to use settings created with the `django-content-settings` module in various contexts, such as code, templates, and APIs.

## Creating a Variable

Let's start by creating a `MAX_PRICE` variable, which we will use for price validation:

```python
from content_settings.types.basic import SimpleDecimal

MAX_PRICE = SimpleDecimal("9.99", help="Maximum allowed price in the store")
```

By default, if not altered in the admin panel, `MAX_PRICE` will return `Decimal("9.99")`.

## Accessing Variables in Templates

Using variables in templates is straightforward. If you've added `content_settings.context_processors.content_settings` to your `context_processors`, you can access `content_settings.conf.content_settings` using `{{ CONTENT_SETTINGS }}`.

```html
<b>Max Price:</b> {{ CONTENT_SETTINGS.MAX_PRICE }}
```

## Accessing Variables Through API

The content settings app has built-in views you can use to provide access to your variables through the API.

Below is an example of how you can use it in your `urls.py`:

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

In this way, you define an API that provides access to two variables, `TITLE` and `DESCRIPTION`. Read more about APIs [here](api.md).

The next step is to define permissions for the setting, i.e., who is allowed to read it. The `fetch_permission` attribute is responsible for that:

```python
from content_settings.types.basic import SimpleText

DESCRIPTION = SimpleText(
    "The best bookstore in the world",
    fetch_permission="any",  # <-- update
)
```

More about permissions can be found [here](permissions.md).

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

## Prefix System

The `content_settings` object has a system of prefixes, which can be read as "functions under the setting." A prefix is always lowercased with the following double-underscore (`__`).

```python
content_settings.prefix_name__SETTINGS_NAME
```

### `type__` - Accessing Variable Type

This prefix is the simplest way to access the settings type object. For example:

```python
content_settings.type__MAX_PRICE.help
```

Returns the value of the `help` attribute of the setting.

### `lazy__` - Get a Lazy/Proxy Object of the Setting

In cases where a variable is used in class or function attributes, you should use a lazy object with the `lazy__` prefix:

```python
from decimal import Decimal
from content_settings.conf import content_settings

def update_price(request, max_price=content_settings.lazy__MAX_PRICE):
    new_price = Decimal(request.POST["price"])
    if new_price > max_price:
        raise ValueError("Price is too high")
    
    # ...
```

**Why is that?**

If you don't use the `lazy__` prefix and just use the variable directly:

```python
def update_price(request, max_price=content_settings.MAX_PRICE):
    ...
```

everything would work as expected, until you decide to change the value of the variable in the Django admin panel. In the example above (without `lazy`), the value of `max_price` will remain unchanged, which is undesirable and unexpected. In the lazy-prefix example, the value will be updated when the variable in Django admin changes.

The lazy-prefix returns not the value itself but a proxy object that retrieves the value every time you access it.

### `withtag__` - Dictionary with All Settings with a Specific Tag

*For this prefix, instead of `SETTING_NAME`, use `TAG_NAME`.*

Example:

```python
all_main = content_settings.withtag__MAIN
```

`all_main` is a dictionary where the setting name is the key and the setting value is the value.

### `startswith__` - Dictionary with All Settings Starting with a Specific Value

*Works in the same way as the `withtag__` prefix.*

```python
all_main = content_settings.startswith__MAIN
```

`all_main` contains all of the settings whose names start with "MAIN," as a dictionary where the setting name is the key and the setting value is the value.

### Custom Prefix

You can register your own prefix using the `store.register_prefix` decorator. Read more about it in the [article about Possible Extensions](extends.md).

## Assigning Values

You can assign a value directly in the code (not only in the Admin Panel):

```python
content_settings.IS_OPEN = "-"
assert content_settings.IS_OPEN is False
```

This is not how `django-content-settings` was intended to be used, so keep in mind:

* The assigned value is always a string (`raw_value`), but the returned value has the type of the setting.
* The assignment process includes value validation, which can take some time.
* Assigning the value updates the database value as well as the cache.
* For user-defined values, you can also define creation attributes that will be used in case the type setting is not created:

```python
content_settings.IS_OPEN = ("-", "bool")
```

[![Stand With Ukraine](https://raw.githubusercontent.com/vshymanskyy/StandWithUkraine/main/banner-direct-single.svg)](https://stand-with-ukraine.pp.ua)

