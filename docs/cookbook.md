# Cookbook

This section covers practical use cases for the `django-content-settings` module that might be useful in your projects.

---

### Grouping Multiple Settings by the Same Rule

Suppose you have a group of settings with the same permission and want to append a note to the help text for those settings. While you can configure each setting individually, grouping them simplifies the process.

```python
from content_settings.types.basic import SimpleString
from content_settings.permissions import superuser
from content_settings.defaults.context import defaults
from content_settings.defaults.modifiers import help_suffix

with defaults(help_suffix("Only superuser can change that"), update_permission=superuser):
    SITE_TITLE = SimpleString("Book Store", help="title for the site.")
    SITE_KEYWORDS = SimpleString("books, store, popular", help="head keywords.")
```

The above code can be replaced with individual configurations as follows:

```python
# same imports

SITE_TITLE = SimpleString(
    "Book Store", 
    update_permission=superuser,
    help="title for the site.<br>Only superuser can change that",
)
SITE_KEYWORDS = SimpleString(
    "books, store, popular",
    update_permission=superuser,
    help="head keywords.<br>Only superuser can change that",
)
```

---

### Setting as a Class Attribute (Lazy Settings)

Consider the following `content_settings.py`:

```python
from content_settings.types.basic import SimpleInt

POSTS_PER_PAGE = SimpleInt(10, help="How many blog posts will be shown per page")
```

In a `views.py`:

```python
from django.views.generic import ListView
from blog.models import Post
from content_settings.conf import content_settings


class PostListView(ListView):
    model = Post
    paginate_by = content_settings.POSTS_PER_PAGE
```

The above will work until you update `POSTS_PER_PAGE` in the Django admin, at which point the change won’t reflect. Instead, use a lazy value:

```python
# same imports

class PostListView(ListView):
    model = Post
    paginate_by = content_settings.lazy__POSTS_PER_PAGE  # <-- update
```

---

### How to Test Setting Changes

Use `content_settings_context` from `content_settings.context_managers` to test setting changes.

#### As a Decorator:

```python
@content_settings_context(TITLE="New Book Store")
def test_get_simple_text_updated():
    assert content_settings.TITLE == "New Book Store"
```

#### As a Context Manager:

```python
def test_get_simple_text_updated_twice():
    client = get_anonymous_client()
    with content_settings_context(TITLE="New Book Store"):
        assert content_settings.TITLE == "New Book Store"

    with content_settings_context(TITLE="SUPER New Book Store"):
        assert content_settings.TITLE == "SUPER New Book Store"
```

---

### Handling Endless Running Commands

If you have an endless running command and want to keep settings updated, manually check updates inside the loop. Use `check_update` from `content_settings.caching`.

```python
from django.core.management.base import BaseCommand
from content_settings.caching import check_update

class Command(BaseCommand):
    def handle(self, *args, **options):
        while True:
            check_update()

            # your logic
```

---

### Ensuring Celery/Huey Tasks Have Updated Settings

This is handled automatically.

---

### Triggering a Procedure When a Variable Changes

To trigger an action, such as data synchronization, when a setting changes, add a `post_save` signal handler for `models.ContentSetting`.

#### Case #1: Manually Convert Raw Data

```python
from django.db.models.signals import post_save
from django.dispatch import receiver
from content_settings.models import ContentSetting

@receiver(post_save, sender=ContentSetting)
def process_variable_update(instance, created, **kwargs):
    if instance.name != 'VARIABLE':
        return
    val = content_settings.type__VARIABLE.give_python(instance.value)

    # process value
```

#### Case #2: Use `content_settings_context`

```python
# same imports
from content_settings.context_managers import content_settings_context

@receiver(post_save, sender=ContentSetting)
def process_variable_update(instance, created, **kwargs):
    if instance.name != 'VARIABLE':
        return

    with content_settings_context(VARIABLE=instance.value):
        val = content_settings.VARIABLE

    # process value
```

---

### Upgrading a Variable from SimpleText to Template

If you previously used a `SimpleText` variable and later need a template, you don’t have to update all references from `VARNAME` to `VARNAME()`.

Use `GiveCallMixin` or `NoArgs` types such as `DjangoTemplateNoArgs` or `SimpleEvalNoArgs`. For the opposite scenario, use `MakeCallMixin`.

---

### Using `DjangoModelTemplate` Without Directly Importing a Model

If you cannot import a model to assign a query to `template_model_queryset`, use `DjangoTemplate` with `gen_args_call_validator`.

```python
def getting_first_profile():
    from accounts.models import Profile

    return Profile.objects.first()

NEW_SETTING = DjangoTemplate(
    "{{object.name}}",
    validators=[gen_args_call_validator(getting_first_profile)],
    template_args_default={'object': require}
)
```

[![Stand With Ukraine](https://raw.githubusercontent.com/vshymanskyy/StandWithUkraine/main/banner-direct-single.svg)](https://stand-with-ukraine.pp.ua)
