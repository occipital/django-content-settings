# Getting Started

## Installation and Initial Setup

---

### Step 1: Install the Module

To begin using `django-content-settings`, first install it using pip:

```bash
$ pip install django-content-settings
```

---

### Step 2: Update `settings.py` in Your Django Project

Add `content_settings` to the `INSTALLED_APPS` list in your Django project’s `settings.py` file:

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

---

### Step 3: Configure Templates Context Processor

To use settings in templates, add `content_settings.context_processors.content_settings` to the `context_processors` in your `TEMPLATES` configuration:

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

Now you can access content settings in templates like this:

```html
<b>{{ CONTENT_SETTINGS.MY_VAR }}</b>
```

---

### Step 4 (Optional): Configure Preview on Site

To preview changes before applying them to all users, add the `"content_settings.middlewares.preview_on_site"` middleware to your `settings.py`:

```python
MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "content_settings.middlewares.preview_on_site", # <-- update
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]
```

And activate preview in the settings of your project by setting.

```python
CONTENT_SETTINGS_PREVIEW_ON_SITE_SHOW = True
```

This enables saving settings in a preview object to see the effect online for a single user. Check the [UI page](ui.md#preview-functionality) for details.

---

### Step 5 (Optional): API Access Configuration

To access variables via API, update `urls.py`:

```python
path("content-settings/", FetchAllSettingsView.as_view()),
```

Your updated `urls.py` might look like this:

```python
from django.urls import path, include
from django.contrib import admin

from content_settings.views import FetchAllSettingsView

urlpatterns = [
    path("admin/", admin.site.urls),
    path("content-settings/", FetchAllSettingsView.as_view()), # <-- update
]
```

This example exposes all variables at one endpoint. For more control, you can create endpoints for specific subsets of settings. Learn more in the [API page](api.md).

---

### Step 6 (Optional and Experimental): Code Highlight Configuration

To enable code highlighting for JSON, YAML, or Python code using [CodeMirror](https://codemirror.net/5/), update `settings.py`:

```python
from content_settings.defaults.collections import codemirror_all

CONTENT_SETTINGS_DEFAULTS = [
    *codemirror_all(),
]
```

For other extensions, check the [Possible Extensions page](extends.md).

For a complete list of available settings, visit the [Settings page](settings.md).

---

## Creating Your First Variable

---

### Step 1: Define the Variable

Create a file named `content_settings.py` in one of your apps (e.g., `books/content_settings.py`) and add:

```python
from content_settings.types.basic import SimpleString

TITLE = SimpleString(
    "Book Store",
    help="The title of the book store",
)
```

---

#### Understanding the Code

- **`TITLE`**: The setting name, used in code and the admin panel.
- **`SimpleString`**: The setting type (a simple string in this case).
- **`"Book Store"`**: The setting’s default value.
- **`"The title of the book store"`**: A description displayed in the admin panel.

---

### Step 2: Run Migrations

Run migrations to add the default value to the database, enabling editing via the admin panel:

```bash
$ python manage.py migrate
```

---

## Usage in Code and Templates

---

### In Python Code

Access settings in Python code like this:

```python
from content_settings.conf import content_settings
content_settings.TITLE
```

---

### In Templates

Access settings in Django templates like this:

```html
<head>
<title>{{ CONTENT_SETTINGS.TITLE }}</title>
</head>
```

---

And that's it! You're now ready to use `django-content-settings` to manage editable variables efficiently through the Django admin panel or API.

[![Stand With Ukraine](https://raw.githubusercontent.com/vshymanskyy/StandWithUkraine/main/banner-direct-single.svg)](https://stand-with-ukraine.pp.ua)
