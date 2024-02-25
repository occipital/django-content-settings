[![Stand With Ukraine](https://raw.githubusercontent.com/vshymanskyy/StandWithUkraine/main/banner-direct-single.svg)](https://stand-with-ukraine.pp.ua)

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

### I have an endless running command and I want to keep all of the settings updated within that script

In order to do so you need manually check updates inside of the endless loop. Use `check_update` function from `content_settings.caching` module for that.

```python
from django.core.management.base import BaseCommand
from content_settings.caching import check_update

class Command(BaseCommand):
    def handle(self, *args, **options):
        while True:
            check_update()

            # your stuff
```

### I want to have all of the celery tasks updated with a celery/huey/other task

It is done automatically.

### Changin variable should trigger a procedure, for example data sync.

You can add `post_save` handled for `models.ContentSetting` and check which variable was changed.

The important thing to notice here is that `content_settings.VARIABLE` woudn't have a new value in that handler, as the new value appears in the system only after `caching.check_update()` - for django views it is in the beginnging of the next request.

In order to get a new value you can have a couple use cases.

Case #1 - manually conver raw data into object.

```python
from django.db.models.signals import post_save
from django.dispatch import receiver
from content_settings.models import ContentSetting

@receiver(post_save, sender=ContentSetting)
def process_variable_update(instance, created, **kwargs):
    if instance.name != 'VARIABLE':
        continue
    val = content_settings.type__VARIABLE.give_python(instance.value)

    # process value
```

Case #2 - use `content_settings_context` from `context_managers`. One was created to tests and it is used in admin-panel for preview variables which use other variables in change view, but you can use it in real code

```python
# same imports
from content_settings.context_managers import content_settings_context

@receiver(post_save, sender=ContentSetting)
def process_variable_update(instance, created, **kwargs):
    if instance.name != 'VARIABLE':
        continue

    with content_settings_context(VARIABLE=instance.value):
        val = content_settings.VARIABLE

    # process value
```

### What if I had a SimpleText variable, but after some project iterations, I realized I needed a template? Should I go back and change all of the variables from `VARNAME` to `VARNAME()`?

No, if your template has no input arguments you can use mixin `GiveCallMixin` or use NoArgs types such as `DjangoTemplateNoArgs` and `SimpleEvalNoArgs`.

If you have an oposite situation use `MakeCallMixin`