[![Stand With Ukraine](https://raw.githubusercontent.com/vshymanskyy/StandWithUkraine/main/banner-direct-single.svg)](https://stand-with-ukraine.pp.ua)

# Using Variables in your project

## Introduction

This article describes how to use settings created with the `django-content-settings` module in various contexts, such as code, templates, and API.

## Creating a Variable

Let's start by creating a `MAX_PRICE` variable, which we will use for price validation:

```python
from content_settings.types.basic import SimpleDecimal

MAX_PRICE = SimpleDecimal("9.99", help="maximum allowed price in the store")
```

By default, if not altered in the admin panel, `MAX_PRICE` will return `Decimal("9.99")`.

## Access in Templates

Using variables in templates is straightforward. If you've added `content_settings.context_processors.content_settings` to your `context_processors`, you can access `content_settings.conf.content_settings` using `{{CONTENT_SETTINGS}}`.

```html
<b>Max Price:</b> {{ CONTENT_SETTINGS.MAX_PRICE }}
```

## Access Through API

The content setting app has built-in views you can use to provide access to your variables through the API.

Below you can find an example of how you can use it in your `urls.py`:

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

In such a way, you define API that provides access to two variables, TITLE and DESCRIPTION. Read more about APIs [here](api.md).

The next step is to define permissions for the setting, in other words - who is allowed to read it. `fetch_permission` attribute is responsible for that:

```python
from content_settings.types.basic import SimpleText

DESCRIPTION = SimpleText(
    "The best book store in the world",
 fetch_permission="any", # <-- update
)
```

More about permissions, you can read [here](permissions.md).

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

The `content_settings` object has a system of prefixes, which can be read as "function under the setting". Prefix is always lowercased with the following double-underscore `__`

```python
content_settings.prefix_name__SETTINGS_NAME
```

### `type__` - Accessing Variable Type

The most simple one to access the settings type object. For example:

```python
content_settings.type__MAX_PRICE.help
```

Returns the value of the help attribute of the setting.

### `lazy__` - get a lazy/proxy object of the setting

In cases where a variable is used in class or function attributes, you should use a lazy object with a `lazy__` prefix:

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

Let's not use `lazy__` prefix and just use the variable as it is:

```python
def update_price(request, max_price=content_settings.MAX_PRICE):
 ...
```

everything would work as with lazy-prefix, until you decide to change value of the variable in Django Admin panel. In the example above (without lazy), the value of `max_price` will remain unchanged, which is bad and unexpected. In the lazy-prefix example the value would be changed together with changing variable in django admin.

Lazy-prefix returns not the value but the proxy object that returns the value every time you access it.

### `withtag__` - dict with all settings with the specific tag

*for this prefix, instead of SETTING_NAME use TAG_NAME*

Example:

```python
all_main = content_settings.withtag__MAIN
```

`all_main` is a dict with setting name as a key and setting value as a value

### `startswith__` - dict with all settings starts with specific value

*work in the same way as withtag-prefix*

```python
all_main = content_settings.startswith__MAIN
```

`all_main` contains all of the settings with name starts with "MAIN" as a dict with setting name as a key and setting value as a value.

### Own prefix

You can register your own prefix using the `conf.register_prefix` decorator. Read more about it in [article about Possible Extensions](extends.md).