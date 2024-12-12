# Variable Types and Attributes

## Introduction

The `django-content-settings` module offers a variety of variable types, each encapsulating the logic related to that variable. This includes how a variable is converted, validated, displayed in the admin panel, and how permissions for reading and editing are managed.

## Basic Types

### SimpleString

The simplest type is `content_settings.types.base.SimpleString` *([source](source.md#class-simplestringbasesettingsource))*, which is a text string in the admin panel that converts to a string in Python.

```python
from content_settings.types.basic import SimpleString

TITLE = SimpleString(
    "Book Store",
    help="The title of the book store",
)
```

#### Attributes

- **default**: The first argument and the only one that can be passed without naming. It sets the default text value. *the default value for any type should always be string*
- **help** (default: `None`): Description of the variable displayed in the admin panel. (**help_text** can be used alternatively)
- **cls_field** (default: `django.forms.CharField`): The field class in the admin panel.
- **widget** (default: `django.forms.TextInput`): The widget for the field.
- **widget_attrs** (default: `None`): Dictionary of attributes used when creating the widget.

You can learn more about fields and widgets in [official Django Forms documentation](https://docs.djangoproject.com/en/dev/topics/forms/)

- **value_required** (default: `False`): Whether the field must be filled.
- **tags** (default: `None`): Array of tags associated with the variable for easier navigation in admin.
- **validators** (default: `()` *empty tuple*): Additional validation functions for the python object.
- **validators_raw** (default: `()` *empty tuple*): Additional validation functions for the raw text value.
- **version** (default: `""`): we will talk more about this attribute in [caching](caching.md). Updating this value triggers updating the db value to the default value after db migration (`python manage.py migrate`).

Note: Validators are not used when converting text from the database to the variable object.

- **update_permission**, **fetch_permission**, and **view_permission**: Access rights for the variable (detailed in a [separate article](permissions.md)).
- **admin_preview_as** (default: `PREVIEW.TEXT`): when you change values in Django Admin text field, you see a preview of the converted object. This attribute shows how the preview will look like. It has the following options and all of them can be found in constants `content_settings.PREVIEW_*`:
  - `PREVIEW.TEXT` - the value will be shown as plain text inside of the HTML element
  - `PREVIEW.HTML` - the value will be shown as it is without escaping
  - `PREVIEW.PYTHON` - the value will be shown as Python object using `pformat` from `pprint`
- **on_change** (default: `()`): list of functions to call when the setting is changed
- **on_change_commited** (default: `()`): list of functions to call when the setting is changed and committed

### Other Basic Types (`content_settings.types.base`) *([source](source.md#typesbasic))*

- **SimpleText**: Similar to SimpleString, but the input field can contain multiple lines.
- **SimpleHTML**: Same as SimpleText, but with HTML preview in admin. _In the template, there is no need to use the `|safe` filter for that type of variable._
- **SimplePassword**: Same as SimpleString, but hides the value of the input under the password input. If you want to hide the possibility of seeing certain values for the user, consider using the `view_permission` attribute.
- **URLString**: A SimpleString that validates the input as a URL.
- **EmailString**: A SimpleString that validates the input as an Email.
- **SimpleInt**: A SimpleString that converts to an integer.
- **SimpleDecimal**: A SimpleString that converts to a Decimal.
- **SimpleBool**: A SimpleString that converts to a boolean. The set of available values for True and False you can change in tuples `yeses` (by default: `("yes", "true", "1", "+", "ok")`) and `noes` (by default: `("no", "not", "false", "0", "-", "")`) _case insensitive_

## List Types (`content_settings.types.array`) *([source](source.md#typesarray))*

These types convert text to an array.

#### SimpleStringsList

- **split_lines** (default: `"\n"`): Character to split lines.
- **filter_empty** (default: `True`): Whether to include empty lines.
- **comment_starts_with** (default: `"#"`): Lines starting with this character are not added. Set to None to ignore.
- **filters** (default: `None`): Additional filters.

#### TypedStringsList

Converts each line of a string list to a specified type.

```python
from content_settings.types.base import SimpleInt
from content_settings.types.array import TypedStringsList

NUMBERS = TypedStringsList(line_type=SimpleInt())
```

Another way for `NUMBERS` definition:

```python
class IntList(TypedStringsList):
    line_type = SimpleInt()

NUMBERS = IntList()
```

## Date and Time Types (`content_settings.types.datetime`) *([source](source.md#typesdatetime))*

- **DateTimeString**: Converts a string to a datetime object.
  - **input_formats**: List of accepted formats (default: Django's `DATETIME_INPUT_FORMATS`).
- **DateString**: Only converts to a date.
- **TimeString**: Only converts to a time.
- **SimpleTimedelta**: Converts a string like "1d 3h" to a timedelta object.

## Markups (`content_settings.types.markups`) *([source](source.md#typesmarkup))*

- **SimpleYAML**: YAML text format to object (requires [pyyaml](https://pypi.org/project/PyYAML/) to be installed).
- **SimpleJSON**: JSON text format to object.
- **SimpleCSV**: CSV text format to object.
  - **csv_dialect** (default: unix): Read more about dialects in the [Python documentation](https://docs.python.org/3/library/csv.html#csv.Dialect).
  - **csv_fields** (required): A list of field names, or a dict name->type. The default value for types will be used. There is also an option to use `required` and `optional` for the default argument.
  - **csv_fields_list_type** (default: `SimpleString(optional)`): Specifies the default type for CSV fields when the field list is not explicitly defined.

```python
var = SimpleCSV(
    csv_fields={
        "name": SimpleString(required), # required field
        "balance": SimpleDecimal("0"), # default balance is 0
        "price": SimpleDecimal(optional), # price key does not exist in case of two columns row
    },
)
```

## Mixins *([source](source.md#typesmixins))*

Through mixin classes, additional functionality (such as additional validators) can be incorporated into your variable types.

#### Example

```python
from content_settings.types.mixins import mix, PositiveValidationMixin
from content_settings.types.basic import SimpleInt, SimpleDecimal

ROWS_PER_PAGE = mix(PositiveValidationMixin, SimpleInt)("10", help="how many rows are shown on one page")
MAX_PRICE = mix(PositiveValidationMixin, SimpleDecimal)("9.99", help="maximum allowed price in the store")
```

### Available Mixins

- **MinMaxValidationMixin** - Adds a validator that ensures the result value is greater or/and lower than the specified limits. It adds attributes `min_value` and `max_value`.
- **EmptyNoneMixin** - Sets the value to None if it is empty.
- **PositiveValidationMixin** - Shortcut for `MinMaxValidationMixin` to ensure the value is positive.
- **ProcessorsMixin** - Used to post-process the generated Python object value. It adds an additional attribute to your type: `processors: Iterable[TCallableStr, ...] = ()`. Here is a small example that truncates text using the [shorten function](https://docs.python.org/3/library/textwrap.html#textwrap.shorten).

```python
import textwrap

def shorten(value):
    return textwrap.shorten(value, width=20, placeholder='...')

SHORT_STR = mix(ProcessorsMixin, SimpleString)("This is string", processors=(shorten,))
```

- **GiveProcessorsMixin** - Used to post-process the setting value. The main difference with `ProcessorsMixin` is that the value will be processed every time the setting attribute is requested. The additional attribute is `give_processors: Iterable[Union[TCallableStr, Tuple[Optional[str], TCallableStr]], ...] = ()`. Similar to `ProcessorsMixin.processors`, you can add functions to `give_processors`, or add tuples with two arguments: a suffix as a string and a function.

```python
import textwrap

def shorten(value):
    return textwrap.shorten(value, width=20, placeholder='...')

SHORT_STR = mix(GiveProcessorsMixin, SimpleString)("This is string", give_processors=(shorten,))

# is the same as
SHORT_STR = mix(GiveProcessorsMixin, SimpleString)("This is string", give_processors=((None, shorten),))

# you can define suffix and define a give processor for that suffix only
SHORT_STR = mix(GiveProcessorsMixin, SimpleString)("This is string", suffixes={"copy": lambda x: x}, give_processors=(("copy", shorten),))
```

[![Stand With Ukraine](https://raw.githubusercontent.com/vshymanskyy/StandWithUkraine/main/banner-direct-single.svg)](https://stand-with-ukraine.pp.ua)

