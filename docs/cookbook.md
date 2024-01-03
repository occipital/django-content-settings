![Django Content Settings](img/title_3.png)

# Cookbook

Here we will try to cover some of the cases that might be useful in your projects

### Grouping multiple settings by the same rule

So imagine you have a group of settings that have the same permission, and also you want to add a note to the helpline for those settings. You can set permissions and helpline for each seating separately, but you can also group them and assign those rules to the group.

```python
from content_settings.types.basic import SimpleString
from content_settings.permissions import superuser
from content_settings.context_mamagers import context_defaults, help_format

with context_defaults(help_format("{}. Only superuser can change that"), update_permission=superuser):
    SITE_TITLE = SimpleString("Book Store", help="title for the site")
    SITE_KEYWORDS = SimpleString("books, store, popular", help="head keywords")
```

The above settigs lines can be replaced without `context_defaults` as:

```python
# same imports

SITE_TITLE = SimpleString(
    "Book Store", 
    update_permission=superuser,
    help="title for the site. Only superuser can change that",
)
SITE_KEYWORDS = SimpleString(
    "books, store, popular",
    update_permission=superuser,
    help="head keywords. Only superuser can change that",
)
```

### Setting as class attribute (lazy settings)

Imagine you have a `content_settings.py`

```python
from content_settings.types.basic import SimpleInt

POSTS_PER_PAGE = SimpleInt(10, help="How many blog posts will be shown per page")
```

If you create a view.py

```python

from django.views.generic import ListView
from blog.models import Post
from content_settings.conf import content_settings


class PostListView(ListView):
    model = Post
    paginate_by = content_settings.POSTS_PER_PAGE
```

That would work, until you update `POSTS_PER_PAGE` in django admin and found out that update does not work.
What you should do instead is to set a lazy value to that attribute


```python
# same imports

class PostListView(ListView):
    model = Post
    paginate_by = content_settings.lazy__POSTS_PER_PAGE # <-- update
```

_I know that you can simply overwrite `get_paginate_by` function, I've just use it to show an idea_


### How to test setting change?

Use `content_settings_context` from `content_settings.context_managers`.

You can use it as test decorator:

```python
@content_settings_context(TITLE="New Book Store")
def test_get_simple_text_updated():
    resp = get_anonymous_client().get("/content-settings/fetch/title/")
    assert resp.status_code == 200
    assert resp.json() == {"TITLE": "New Book Store"}
```

or as context manager:

```python
def test_get_simple_text_updated_twice():
    client = get_anonymous_client()
    with content_settings_context(TITLE="New Book Store"):
        resp = client.get("/content-settings/fetch/title/")
        assert resp.status_code == 200
        assert resp.json() == {"TITLE": "New Book Store"}

    with content_settings_context(TITLE="SUPER New Book Store"):
        resp = client.get("/content-settings/fetch/title/")
        assert resp.status_code == 200
        assert resp.json() == {"TITLE": "SUPER New Book Store"}
```