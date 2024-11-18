# API & Views

## Simple Example - FetchAllSettingsView

Sometimes, you need to organize access to your content settings via API for your front-end applications. While you can access content settings directly in Python code, the module provides a fetching view that simplifies exposing content settings through APIs.

Add the fetching view to your `urls.py`:

```python
from django.urls import path
from content_settings.views import FetchAllSettingsView

urlpatterns = [
    path(
        "fetch/all/",
        FetchAllSettingsView.as_view(),
        name="fetch_all_info",
    ),
]
```

The API call will return all registered content settings that the user has permission to fetch (based on the `fetch_permission` attribute, explained later in the article).

## Group of Settings to Fetch - FetchSettingsView

If you want to limit the fetched settings to specific names, use the `FetchSettingsView`.

Example:

```python
from django.urls import path
from content_settings.views import FetchSettingsView

urlpatterns = [
    path(
        "fetch/main/",
        FetchSettingsView.as_view(
            names=[
                "TITLE",
                "DESCRIPTION",
            ]
        ),
        name="fetch_main_info",
    ),
]
```

The `names` attribute specifies the settings included in the API. `FetchSettingsView` checks permissions for each setting using the `fetch_permission` attribute. By default, settings are not fetchable, so you need to update the settings' `fetch_permission` attribute. [Learn more about permissions here](permissions.md).

```python
from content_settings import permissions  # <-- Update

TITLE = SimpleString(
    "My Site",
    fetch_permission=permissions.any,  # <-- Update
    help="The title of the site",
)

DESCRIPTION = SimpleString(
    "Isn't it cool?",
    fetch_permission=permissions.any,  # <-- Update
    help="The description of the site",
)
```

Now any user can access the `TITLE` and `DESCRIPTION` settings using the `fetch/main/` API.

```bash
$ curl http://127.0.0.1/fetch/main/
{"TITLE":"My Site","DESCRIPTION":"Isn't it cool?"}
```

## Other Options for Using the `names` Attribute

### Fetch All Settings Matching Specific Conditions

Instead of specifying setting names directly, you can use a function to fetch all settings that meet certain criteria.

#### Example: Matching All Settings with a Specific Tag

```python
from content_settings.views import FetchSettingsView, gen_hastag

FetchSettingsView.as_view(
    names=gen_hastag("general")
)
```

#### Example: Matching All Settings with a Specific Prefix

```python
from content_settings.views import FetchSettingsView, gen_startswith

FetchSettingsView.as_view(
    names=gen_startswith("GENERAL_")
)
```

#### Example: Combining Criteria

Fetch all settings that start with `"GENERAL_"` and also include the setting `TITLE`.

```python
from content_settings.views import FetchSettingsView, gen_startswith

FetchSettingsView.as_view(
    names=[
        gen_startswith("GENERAL_"),
        "TITLE",
    ]
)
```

### Using a Suffix

```python
FetchSettingsView.as_view(
    names=[
        "TITLE",
        "BOOKS__available_names",
    ],
)
```

### Define Specific Keys for the Result JSON

You can customize the keys in the resulting JSON by using a tuple in the `names` list. The first value in the tuple will be the key.

```python
FetchSettingsView.as_view(
    names=[
        "TITLE",
        ("NAMES", "BOOKS__available_names"),
    ],
)
```

In this example, the key `"NAMES"` will store the value of `content_settings.BOOKS__available_names`. This is useful if you change the setting name in Python but want to retain the old name in the API interface.

## FAQ

### What Happens if a User Lacks Permission to Fetch a Setting?

The response will still have a status of `200`. The JSON response will include only the settings the user is allowed to access. An additional header, `X-Content-Settings-Errors`, will provide details about excluded settings.

### How Can I Hide Errors from the Response Headers?

Set the `show_error_headers` attribute to `False`.

Example:

```python
FetchSettingsView.as_view(
    names=[
        "TITLE",
        "DESCRIPTION",
    ],
    show_error_headers=False,
)
```

### How Can I Create a Custom View That Still Checks Permissions?

To check permissions, use the `can_fetch` method of the setting type. You can retrieve the setting type by name in two ways:

#### Using the `type__` Prefix

```python
content_settings.type__TITLE.can_fetch(user)
```

#### Using `get_type_by_name` from the Caching Module

```python
from content_settings.caching import get_type_by_name

get_type_by_name("TITLE").can_fetch(user)
```

### How Can I Customize the JSON Representation for Complex Settings?

- Overwrite the `SimpleString.json_view_value(self, value: Any, **kwargs)` method. The method should return a string in JSON format.
- Use the `json_encoder` parameter to specify a custom JSON serializer (default: `DjangoJSONEncoder`).

[![Stand With Ukraine](https://raw.githubusercontent.com/vshymanskyy/StandWithUkraine/main/banner-direct-single.svg)](https://stand-with-ukraine.pp.ua)
