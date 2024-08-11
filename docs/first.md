[![Stand With Ukraine](https://raw.githubusercontent.com/vshymanskyy/StandWithUkraine/main/banner-direct-single.svg)](https://stand-with-ukraine.pp.ua)

# Getting Started

## Installation and Initial Setup

### Step 1: Install the Module

To begin using `django-content-settings`, first install it using pip:

```bash
pip install django-content-settings
```

### Step 2: Update `settings.py` in Your Django Project

After installation, you need to add `content_settings` to the `INSTALLED_APPS` list in your Django project's `settings.py` file. The updated `INSTALLED_APPS` might look like this:

```python
INSTALLED_APPS = (
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.sites",
    "django.contrib.staticfiles",
    "django.contrib.messages",
    "content_settings", # <-- update
    "books",
)
```

### Step 3: Configure Templates Context Processor

For using variables in templates, add `content_settings.context_processors.content_settings` to the `context_processors` in the `TEMPLATES` configuration. Your `TEMPLATES` setting might look like this:

```python
TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "django.template.context_processors.request",
                "content_settings.context_processors.content_settings", # <-- update
            ],
        },
    },
]
```

Now, you can *use settings* in templates like this:

```html
<b>{{ CONTENT_SETTINGS.MY_VAR }}</b>
```

### Step 4 (optional): Configure Preview on Site

Add preview on site middleware `"content_settings.middlewares.preivew_on_site"` to the `settings.py` to be able to see the changes live, before applying those for all users.

```python
MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "content_settings.middlewares.preivew_on_site", # <-- update (after AuthenticationMiddleware)
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]
```

Now you can save settings in the preview object to see the effect online for one user. Check [the UI page](ui.md#preview-functionality) to understand how it looks.

### Step 5 (optional): API Access Configuration

To access variables through the API, update `urls.py` with the following line:

```python
path("content-settings/", FetchAllSettingsView.as_view()),
```

Your `urls.py` may look like this now:

```python
from django.urls import path, include
from django.contrib import admin

from content_settings.views import FetchAllSettingsView

urlpatterns = [
    path("admin/", admin.site.urls),
    path("content-settings/", FetchAllSettingsView.as_view()), # <-- update
]
```

The example above shows all of the variables in one end-point, but you can create end-points with subset of settings. Read more about it in [the API page](api.md).

### Stpe 6 (optional and experemental): Code highlight configuration

If you want to have code highlight for JSON/YAML/PY code using [Codemirror](https://codemirror.net/5/) - update setting.py

```python
from content_settings.defaults.collections import codemirror_all

CONTENT_SETTINGS_DEFAULTS = [
    *codemirror_all(),
]
```

... and it is not the only extension you can do for your settings. Check [the Possible Extensions page](extends.md) to learn more about how you can extend functionality of content settings.

[The Settings page](settings.md) contains collection of all available settings you can add in `settings.py` of your project to configure Content Settings.

## Creating Your First Variable

### Step 1: Define the Variable

Create a file named `content_settings.py` in any of your working apps, for example, `books/content_settings.py`. Add the following content:

```python
from content_settings.types.basic import SimpleString

TITLE = SimpleString(
    "Book Store",
    help="The title of the book store",
)
```

### Step 2: Run Migrations

Execute migrations to add *default value* to the database, allowing you to edit it subsequently.

```bash
python manage.py migrate
```

### Understanding the Code

- `TITLE`: *setting name* you will use in your code and admin panel.
- `SimpleString`: *setting type*, in this case, a simple string.
- `"Book Store"`: *setting default value*.
- `"The title of the book store"`: A description displayed in the admin panel.

## Usage in Code and Templates

### In Python Code

To *use setting* in Python code, such as in views:

```python
from content_settings.conf import content_settings
content_settings.TITLE
```

### In Templates

In Django templates, access it like this:

```html
<head>
<title>{{ CONTENT_SETTINGS.TITLE }}</title>
</head>
```

And that's it! You're now ready to use `django-content-settings` in your Django project, effectively managing editable variables through the admin panel and API.
