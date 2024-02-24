# Django Content Settings - the most advanced admin editable setting

The `django-content-settings` module is a versatile addition to the Django ecosystem, offering users the ability to easily create and manage editable variables directly from the Django admin panel. What sets this module apart is its ability to handle variables of any type without restricting their complexity. Thanks to an integrated caching system, these variables can be used efficiently in code, irrespective of their complexity.

### Key Features

1. **Type-Agnostic Variable Creation**: Users can create variables of any type, making the module highly adaptable to various needs.
2. **Editability from Django Admin Panel**: Seamless integration with the Django admin panel allows for effortless editing of variables.
3. **Flaxable permission model**: Every setting can have own permission rule for view, edit, fetch in API and view changes history.
4. **Preview**: Preview setting before apply and addition option to preview setting change right on site.
5. **Caching System**: Ensures high performance, negating the impact of variable complexity on code execution speed.

For the full documentation, please visit [here](https://django-content-settings.readthedocs.io/).

[▶️ YouTube Video with dive deep ~ 2h](https://youtu.be/RNYmvv_G5zs) 

### How does it look

- **Setup**. [Here](https://django-content-settings.readthedocs.io/en/latest/first/) you can get step-by-step instruction.

- **Define the setting**. To do so you need to define constant in `content_settings.py` in your app

```python
# content_settings.py

from content_settings.types.basic import SimpleString

TITLE = SimpleString("Songs", help="The title of the site")
```

the code above defines a variable `TITLE`, with type `SimpleString` and default value `Songs`.

- **Migrate**. In order to be able to edit data in Django Admin

```bash
$ python manage.py migrate
```

_Technically, you can use variable in code even without migration. The migration is need to make variable editable in admin panel_

- **Use it in your project**. That is it. You can the variable `TITLE` in your code. 

```python

from content_settings.conf import content_settings

content_settings.TITLE
```

In template:

```html
<h2>{{CONTENT_SETTINGS.TITLE}}</h2>
```

In API:

```bash
$ curl http://127.0.0.1/content-settings/fetch/title/
```

Ok, I lied, in order to use in API you need to update permission from the setting:

```python
# content_settings.py

from content_settings.types.basic import SimpleString
from content_settings import permissions

TITLE = SimpleString(
    "Songs",
    fetch_permission=permissions.any,
    help="The title of the site",
)
```

Simple as that, we have a lot of types for settings you can use `SimpleText`, `SimpleHTML`, `SimpleInt`, `SimpleBool`, `SimpleDecimal`, `DateTimeString`, `SimpleTimedelta`, `SimpleYAML`, `SimpleJSON`, `SimpleCSV`, `DjangoTemplate`, `DjangoModelTemplate`, `SimpleEval`, `SimpleExec` and so on... [Read more](https://django-content-settings.readthedocs.io/en/latest/types/) about the types available for you.

It is also very fast thanks to our caching system. [Read more about it](https://django-content-settings.readthedocs.io/en/latest/caching/).

Some fancy things you can find in our [cookbook](https://django-content-settings.readthedocs.io/en/latest/cookbook/).