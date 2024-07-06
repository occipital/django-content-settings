# API & Views

## Simple Example

Sometimes, you need to organize access to your content settings by API for your front-end applications. You can do it yourself since you can access content settings in Python code, but we have a fetching view that can help you simplify organizing content settings into APIs.

All you need to do is to add fetching view into your `urls.py`

Here is a simple example:

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

The `names` attribute lists all of the settings that will be used in the API

also, the `FetchSettingsView` checks the permission, if the current user is allowed to read this particular setting by checking `fetch_permission` attribute of the setting. By default setting is not allowed to be fetched, so you need to update your setting. (more about permissions you can read [here](permissions.md))

```python
from content_settings import permissions # <-- Update

TITLE = SimpleString(
    "My Site",
    fetch_permission=permissions.any, # <-- Update
    help="The title of the site",
)

DESCRIPTION = SimpleString(
    "Isn't it cool?",
    fetch_permission=permissions.any, # <-- Update
    help="The Description of the site",
)
```

now any user can get access to your content setting `TITLE` and `DESCRIPTION` using `fetch/main/` API

```
$ curl http://127.0.0.1/fetch/main/
{"TITLE":"My Site","DESCRIPTION":"Isn't it cool?"}
```

## Other options of using `names` attribute

### All settings that matches specific conditions

Instead of setting the keys you can use specific function that can find all of the settings matches certain criteria

For example matching all settings that have specific tag

```python
from content_settings.views import FetchSettingsView, gen_hastag

FetchSettingsView.as_view(
    names=gen_hastag("general")
)
```

Or, for example, settengs that have specific prefix in their name

```python
from content_settings.views import FetchSettingsView, gen_hastag

FetchSettingsView.as_view(
    names=gen_startswith("GENERAL_")
)
```

Or even combine those, for example I want to have all of the settings that starts with "GENERAL_" and setting TITLE

```python
from content_settings.views import FetchSettingsView, gen_hastag

FetchSettingsView.as_view(
    names=[
        gen_startswith("GENERAL_"),
        "TITLE",
    ]
)
```

### Suffix

```python
FetchSettingsView.as_view(
    names=[
        "TITLE",
        "BOOKS__available_names",
    ]
),
```

### Define specific keys for the result JSON

when using tuple instead of name, first value will be used as a key

```python
FetchSettingsView.as_view(
    names=[
        "TITLE",
        ("NAMES", "BOOKS__available_names"),
    ]
),
```

in the example above, in the key "NAMES" `content_settings.BOOKS__available_names` will be stored. Can also be useful when you change the name in Python code, but still want old name to be available for API interface.

## FAQ

### What will happen if user doesn't have permission for fetching one of the setting?

The response status will still be 200, the response JSON will include only settings that user have permission to access, but addition header `X-Content-Settings-Errors` will be added that includes reasoning of not including other settings.

### What if I don't want to show error in headers?

Just set `show_error_headers` attribute to `True`.

For example:

```python
FetchSettingsView.as_view(
    names=[
        "TITLE",
        "DESCRIPTION",
    ],
    show_error_headers=False,
)

```

### I want to have my own view, but still check permission

to check permission you should use `can_fetch` method of the setting type.

You have two ways for getting a setting type by setting name.

Using a `type__` prefix

```python
content_settings.type__TITLE.can_fetch(user)
```

Using `get_type_by_name` from [caching module](source.md#caching):

```python
from content_settings.caching import get_type_by_name

get_type_by_name("TITLE").can_fetch(user)
```

### How can I redefine of how the JSON value looks like for the complex setting

* overwrite `SimpleString.json_view_value(self, value: Any, **kwargs)`. The function should return string in JSON format.
* set parameter `json_encoder: type = DjangoJSONEncoder` to JSON Serializer you want