[![Stand With Ukraine](https://raw.githubusercontent.com/vshymanskyy/StandWithUkraine/main/banner-direct-single.svg)](https://stand-with-ukraine.pp.ua)

# Using Variables in your project

## Introduction

This article describes how to use settings created with the `django-content-settings` module in various contexts such as code, templates, and API.

## Creating a Variable

Let's start by creating a `MAX_PRICE` variable, which we will use for price validation:

```python
from content_settings.types.basic import SimpleDecimal

MAX_PRICE = SimpleDecimal("9.99", help="maximum allowed price in the store")
```

By default, if not altered in the admin panel, `MAX_PRICE` will return `Decimal("9.99")`.

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

### Using Lazy Objects

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

### Accessing Variable Type

To get a reference to the variable type, use the `type__` prefix:

```python
content_settings.type__MAX_PRICE.fetch_permission
```

## Access in Templates

Using variables in templates is straightforward. If you've added `content_settings.context_processors.content_settings` to your `context_processors`, you can access `content_settings.conf.content_settings` using `{{CONTENT_SETTINGS}}`.

```html
<b>Max Price:</b> {{ CONTENT_SETTINGS.MAX_PRICE }}
```

## Access Through API

If you've included fetching views in your `urls.py`, it might look like this:

```python
from django.urls import path, include
from django.contrib import admin
from content_settings.views import FetchSettingsView

urlpatterns = [
    path("admin/", admin.site.urls),
    path("books/", include("books.urls")),
    path("fetch/main/", FetchSettingsView.as_view(names=[
        "TITLE",
        "BOOKS__available_names",
    ]), name="fetch_main"),
    path("fetch/home-detail/", FetchSettingsView.as_view(names=[
        "DESCRIPTION",
        "OPEN_DATE",
        "TITLE",
    ]), name="fetch_home_detail"),
]
```

The API allows only read access to data. By default, variables are not accessible through the API. To make a variable available, add the `fetch_permission` attribute:

```python
from content_settings.types.basic import SimpleText
from content_settings import permissions

DESCRIPTION = SimpleText(
    "The best book store in the world",
    fetch_permission=permissions.any,
)
```

### Fetching Multiple Variables

Fetching the group `home-detail` via API:

```bash
curl http://127.0.0.1:8000/fetch/home-detail/
```

The result will be:

```json
{
    "DESCRIPTION": "The best book store in the world",
    "TITLE": "Book Store"
}
```

When requesting a group, permissions for each variable are checked separately, and if insufficient, the variable will not be included in the response. 
