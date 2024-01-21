# Variable Types and Attributes

## Introduction

The `django-content-settings` module offers a variety of variable types, each encapsulating the logic related to that variable. This includes how a variable is converted, validated, displayed in the admin panel, and how permissions for reading and editing are managed.

## Basic Types

### SimpleString

The simplest type is `content_settings.types.base.SimpleString` *([source](https://github.com/occipital/django-content-settings/blob/master/content_settings/types/basic.py))*, which is a text string in the admin panel that converts to a string in Python.

```python
from content_settings.types.basic import SimpleString

TITLE = SimpleString(
    "Book Store",
    help="The title of the book store",
)
```

#### Attributes

- **default**: The first argument and the only one that can be passed without naming. It sets the default text value. *the default value for any type should always be string*
- **help** (default: None): Description of the variable displayed in the admin panel.
- **cls_field** (default: django.forms.CharField): The field class in the admin panel.
- **widget** (default: django.forms.TextInput): The widget for the field.
- **widget_attrs** (default: None): Dictionary of attributes used when creating the widget.

You can learn more about fields and widgets in [official Django Forms documentation](https://docs.djangoproject.com/en/dev/topics/forms/)

- **value_required** (default: False): Whether the field must be filled.
- **empty_is_none** (default: False): If the field is empty, returns None.
- **tags** (default: None): Array of tags associated with the variable for easier navigation in admin.
- **validators** (default: empty tuple): Additional validation functions.
- **version** (default: ""): we will talk more about this attribute in [caching](caching.md). Updating this value trigges updating db value to default value after db migration (`python manage.py migrate`).

Note: Validators are not used when converting text from the database to the variable object.

- **update_permission** and **fetch_permission**: Access rights for changing the variable in the admin panel (detailed in a separate article).
- **admin_preview_as** (default: PREVIEW_TEXT): when you change values in Django Admin text field you see preview of the converted object. This attribute shows how the preview will look like. It has the followig options and all of them can be found in constants `content_settings.PREVIEW_*`:
    - `PREVIEW_TEXT` - the value will be shown as plain text inside of pre html element
    - `PREVIEW_HTML` - the value will be shown as it is without esceping
    - `PREVIEW_PYTHON` - the value will be shown as Python object using `pformat` from `pprint`

### Other Basic Types (`content_settings.types.base`) *([source](https://github.com/occipital/django-content-settings/blob/master/content_settings/types/basic.py))*

- **SimpleText**: Similar to SimpleString, but the input field can contain multiple lines.
- **SimpleHTML**: Same as SimpleText, but with html preview in admin
- **URLString**: A SimpleString that validates the input as a URL.
- **EmailString**: A SimpleString that validates the input as a Email.
- **SimpleInt**: A SimpleString that converts to an integer.
- **SimpleDecimal**: A SimpleString that converts to a Decimal.
- **SimpleBool**: A SimpleString that converts to a boolean. 0 or empty is False, 1 is True.

## List Types (`content_settings.types.array`) *([source](https://github.com/occipital/django-content-settings/blob/master/content_settings/types/array.py))*

These types convert text to an array.

#### SimpleStringsList

- **split_lines** (default: \n): Character to split lines.
- **filter_empty** (default: True): Whether to include empty lines.
- **comment_starts_with** (default: `#`): Lines starting with this character are not added. Set to None to ignore.
- **filters** (default: None): Additional filters.

#### TypedStringsList

Converts each line of a string list to a specified type.

```python
from content_settings.types.base import SimpleInt
from content_settings.types.array import TypedStringsList

NUMBERS = TypedStringsList(line_type=SimpleInt())
```

another way for `NUMBERS` definition:

```python
class IntList(TypedStringsList):
    line_type=SimpleInt()

NUMBERS = IntList()
```

## Date and Time Types (`content_settings.types.datetime`) *([source](https://github.com/occipital/django-content-settings/blob/master/content_settings/types/datetime.py))*

- **DateTimeString**: Converts a string to a datetime object.
    - **input_formats**: List of accepted formats (default: Django's `DATETIME_INPUT_FORMATS`).
- **DateString**: Only converts to a date.
- **TimeString**: Only converts to a time.
- **SimpleTimedelta**: Converts a string like "1d 3h" to a timedelta object.

## Markups (`content_settings.types.markups`) *([source](https://github.com/occipital/django-content-settings/blob/master/content_settings/types/markup.py))*

- **SimpleYAML**: YAML text format to object (requires [pyyaml](https://pypi.org/project/PyYAML/) to be installed).
- **SimpleJSON**: JSON text format to object.
- **SimpleCSV**: CSV text format to object.
    - **csv_dialect** (default: unix): read more about dialects in the [python doc](https://docs.python.org/3/library/csv.html#csv.Dialect)
    - **csv_fields (required)** - a list of fieldnames, or dict name->type. The default value for types will be used. There is also an option to use `required` and `optional` for the default argument
    - **csv_fields_list_type** (default: `SimpleString(optional)`) - what will be default type for csv_fields is list of columns

```python
var = SimpleCSV(
    csv_fields={
        "name": SimpleString(required), # required to be
        "balance": SimpleDecimal("0"), # 0 by default
        "price": SimpleDecimal(optional), # price key is not exist in case of two columns row
    },
)
```
    
    

## Templates (`content_settings.types.template`) *([source](https://github.com/occipital/django-content-settings/blob/master/content_settings/types/template.py))*

Module introduces advanced variable types designed for template rendering and Python code evaluation using `CallToPythonMixin` for using setting variables as functions.

- **DjangoTemplate**: is used for rendering a Django template specified in the variable's value
    - **template_args_default**: (Optional) A dictionary that converts an array of arguments, with which the function is called, into a dictionary passed as context to the template. To set required arguments, import `required` from `content_settings.types.template` and use it as a value.
    - **template_static_data**: (Optional) A dictionary of additional values that can be passed to the template from global env (not as arguments to the function). It can also be a function
    - **template_static_includes** (default: `('CONTENT_SETTINGS', 'SETTINGS')`) - by default both `content_settings` and `settings` are included in context, but by adjusting this tuple you can change that.

Example:

```python
# content_settings.py
SHORT_DESCRIPTION = DjangoTemplate("""
<b>{{title}}</b><br>
{% if description %}
<i>{{description}}</i>
{% endif %}
    """,
    template_args_default={
        "title": "Undefined",
        "description": None,
    },
)

# in code

content_settings.SHORT_DESCRIPTION("Hello world", "your first line of code")

# returns:
# <b>Hello world</b><br>
# <i>your first line of code</i>
```

- **DjangoTemplateNoArgs**: the same as `DjangoTemplate` but without input arguments and return value without calling the attribute

```python
# content_settings.py
TITLE_IMG = DjangoTemplate("<img src='{{SETTINGS.STATIC_URL}}title.png' />")

# in code

content_settings.TITLE_IMG

# returns:
# /static/title.png
```

    - you can still pass input arguments `call` suffix, like `content_settings.TITLE_IMG__call`

- **DjangoModelTemplate**: is a specialized class for rendering templates for individual Django model objects
    - **model_queryset**: A query set of objects that can be used as an argument. The setting only takes the first element for preview purposes in the admin panel.
    - **obj_name**: The name under which the model object is passed to the template.
- **SimpleEval**: is designed to store Python code as the setting's value. When the function is called, the arguments dict is passed to the code execution.

Example:

```python
from content_settings.types.template import required

COMISSION = SimpleEval(
  "total * Decimal('0.2')",
  template_args_default={
    "total": required,
  },
  template_static_data={
    "Decimal": Decimal,
  }

)

# in code
content_settings.COMISSION(Decimal('100'))

# returns
Decimal("20")
```

- **SimpleEvalNoArgs**: the same as `SimpleEval` but without passing input args. It works the same as `DjangoTemplateNoArgs` and simply getting an attribute.

### Calling Functions in Template *([source](https://github.com/occipital/django-content-settings/blob/master/content_settings/templatetags/content_settings_extras.py))*

if you want create a callable setting, such a `DjangoTemplate` or `SimpleEval`, you can render the result of colling in your template using `content_settings_call` tag from `content_settings_extras` library:

```html
{% load content_settings_extras %}

<html>
    <head>
        <title>{{CONTENT_SETTINGS.TITLE}}</title>
    </head>
    <body>
        <header>
            <h1>Book List</h1>
        </header>
            {% for book in object_list %}
                {% content_settings_call "BOOK_RICH_DESCRIPTION" book _safe=True%}
            {% empty %}
                <li>No books found.</li>
            {% endfor %}
    </body>
</html>
```

## Mixins *([source](https://github.com/occipital/django-content-settings/blob/master/content_settings/types/mixins.py))*

Through mixin classes, additional functionality (such as additional validators) can be incorporated into your variable types.

#### Example

```python
from content_settings.types.mixins import mix, PositiveValidationMixin
from content_settings.types.basic import SimpleInt, SimpleDecimal

ROWS_PER_PAGE = mix(PositiveValidationMixin, SimpleInt)("10", help="how many rows are shown on one page")
MAX_PRICE = mix(PositiveValidationMixin, SimpleDecimal)("9.99", help="maximum allowed price in the store")
```

## context_defaults *([source](https://github.com/occipital/django-content-settings/blob/master/content_settings/context_managers.py))*

This feature allows for creating a context in which default values can be modified for variables created within that context.

#### Example

You can create three variables like this:

```python
from content_settings.types.basic import SimpleString
from content_settings.permissions import any

TITLE = SimpleString("Books", fetch_permission=any)
SUB_TITLE = SimpleString("Comics", fetch_permission=any)
AUTHOR = SimpleString("Kind", fetch_permission=any)
```

Alternatively, you can group them in a context where `fetch_permission` is `any` by default:

```python
from content_settings.types.basic import SimpleString
from content_settings.permissions import any
from content_settings.context_managers import context_defaults

with context_defaults(fetch_permission=any):
    TITLE = SimpleString("Books")
    SUB_TITLE = SimpleString("Comics")
    AUTHOR = SimpleString("Kind")
```

for settings tags you can use `set_add` or `set_remove` functions with `context_defaults`

```python
from content_settings.types.basic import SimpleString
from content_settings.context_managers import context_defaults, set_add

with context_defaults(tags=['main']):
    AUTHOR = SimpleString("Kind")
    with context_defaults(set_add(tags=["new"]))
        TITLE = SimpleString("Books")
        EDITOR = SimpleString("Editor", tags=["editor"])

    SUB_TITLE = SimpleString("Comics")
```

in the example above `AUTHOR` and `SUB_TITLE` have only one tag `main`, but `TITLE` has two tags `main` and `new`. But the `EDITOR` will have only one tag `editor`. Because context_default changes default values.

If you want to update initial values instead of default, you should set init attribute for context-process functions such as `set_add`

```python
from content_settings.types.basic import SimpleString
from content_settings.context_managers import context_defaults, set_add

with context_defaults(tags=['main']):
    AUTHOR = SimpleString("Kind")
    with context_defaults(set_add(tags=["new"], _init=True)) # update
        TITLE = SimpleString("Books")
        EDITOR = SimpleString("Editor", tags=["editor"])

    SUB_TITLE = SimpleString("Comics")
```

now everything remains the same except `EDITOR` var, which has all three tags `main`, `new`, and `editor`

shortcut for `set_add(tags=["new"], _init=True)` is `add_tags` which accepts str or iterable

```python
from content_settings.types.basic import SimpleString
from content_settings.context_managers import context_defaults, add_tags

with context_defaults(tags=['main']):
    AUTHOR = SimpleString("Kind")
    with context_defaults(add_tags("new")) # update
        TITLE = SimpleString("Books")
        EDITOR = SimpleString("Editor", tags=["editor"])

    SUB_TITLE = SimpleString("Comics")
```

the updated example works the same as the example before

---

These types and attributes provide a flexible and powerful way to handle different kinds of data within the `django-content-settings` module, ensuring robust and dynamic content management in Django applications.
