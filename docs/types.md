[![Stand With Ukraine](https://raw.githubusercontent.com/vshymanskyy/StandWithUkraine/main/banner-direct-single.svg)](https://stand-with-ukraine.pp.ua)

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
- **help** (default: None): Description of the variable displayed in the admin panel. (**help_text** can be used alternatively)
- **cls_field** (default: django.forms.CharField): The field class in the admin panel.
- **widget** (default: django.forms.TextInput): The widget for the field.
- **widget_attrs** (default: None): Dictionary of attributes used when creating the widget.

You can learn more about fields and widgets in [official Django Forms documentation](https://docs.djangoproject.com/en/dev/topics/forms/)

- **value_required** (default: False): Whether the field must be filled.
- **tags** (default: None): Array of tags associated with the variable for easier navigation in admin.
- **validators** (default: empty tuple): Additional validation functions for the python object.
- **validators_raw** (default: empty tuple): Additional validation functions for the raw text value.
- **version** (default: ""): we will talk more about this attribute in [caching](caching.md). Updating this value trigges updating db value to default value after db migration (`python manage.py migrate`).

Note: Validators are not used when converting text from the database to the variable object.

- **update_permission**, **fetch_permission**, **view_permission** and **view_history_permission**: Access rights for the variable (detailed in a [separate article](permissions.md)).
- **admin_preview_as** (default: PREVIEW.TEXT): when you change values in Django Admin text field you see preview of the converted object. This attribute shows how the preview will look like. It has the followig options and all of them can be found in constants `content_settings.PREVIEW_*`:
    - `PREVIEW.TEXT` - the value will be shown as plain text inside of pre html element
    - `PREVIEW.HTML` - the value will be shown as it is without esceping
    - `PREVIEW.PYTHON` - the value will be shown as Python object using `pformat` from `pprint`
- **on_change** (default: empty tuple): list of functions to call when the setting is changed
- **on_change_commited** (default: empty tuple): list of functions to call when the setting is changed and commited

### Other Basic Types (`content_settings.types.base`) *([source](source.md#typesbasic))*

- **SimpleText**: Similar to SimpleString, but the input field can contain multiple lines.
- **SimpleHTML**: Same as SimpleText, but with html preview in admin. _In the template no need to use `|safe` filter for that type of variable._
- **SimplePassword**: Same as SimpleString, but hides the value of the input under the password input. If you want hide the possiblity to see certain values for the user consider using `view_permission` attribute.
- **URLString**: A SimpleString that validates the input as a URL.
- **EmailString**: A SimpleString that validates the input as a Email.
- **SimpleInt**: A SimpleString that converts to an integer.
- **SimpleDecimal**: A SimpleString that converts to a Decimal.
- **SimpleBool**: A SimpleString that converts to a boolean. The set of avalaibale values for True and False you can change in tuples `yeses` (by default: `("yes", "true", "1", "+", "ok")`) and `noes` (by default: `("no", "not", "false", "0", "-", "")`) _case insensetive_

## List Types (`content_settings.types.array`) *([source](source.md#typesarray))*

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

#### SplitByFirstLine

split a given text value into multiple values using a splitter that defined inside of the value. The result of splitting will be converted using type inside of `split_type` attribute, each value can be given under same name suffix (but lowercased), but also the returned value can be chosen by the function `split_default_chooser` attribute. The first line will be used as a splitter if value from `split_default_key` attribute is in this line. It may sound confusing, but let me show you an example:

```python
from content_settings.types.array import SplitByFirstLine

MY_VAR = SplitByFirstLine(
    split_default_key="MAIN",
    split_type=SimpleDecimal()
)

# now the variable will works as simple Decimal, with extra suffix __main that returns the same value
# but if you update the value in admin to:
"""=== MAIN ===
10.67
=== SECOND ===
4.12
"""
# your variable will work a bit different
content_settings.MY_VAR == Decimal("10.67")
content_settings.MY_VAR__main == Decimal("10.67")
content_settings.MY_VAR__second == Decimal("4.12")

# the first line in the value === MAIN === defines the splitter rule, which means the following value will work the same
"""!!! MAIN !!!
10.67
!!! SECOND !!!
4.12
"""
```

It has a big variety of attributes:

- **split_type** - the type which will be used for each value. You can use a dict to set a specific type for each key
- **split_default_key** - the key which will be used for the first line
- **split_default_chooser** - the function which will be used for chosing default value
- **split_not_found** - what should be done if the required key not found. `NOT_FOUND.DEFAULT` - return default value, `NOT_FOUND.KEY_ERROR` raise an exception and `NOT_FOUND.VALUE` return value from **split_not_found_value**
- **split_key_validator** - function that validates a key. You can use a function `split_validator_in` for validator value
- **split_key_validator_failed** - two passible values `SPLIT_FAIL.IGNORE`(default) and `SPLIT_FAIL.RAISE`. What should the system do if validation is failed. `SPLIT_FAIL.IGNORE` - just use line with unvalid key as value for the previous key. `SPLIT_FAIL.RAISE` - raise `ValidationError`

#### SplitTranslation

same as `SplitByFirstLine` but the default value will be chosen based on current django translation `django.utils.translation.get_language`


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

- **MinMaxValidationMixin** - adds a validator that the result value is bigger or/and lower. It adds attributes `min_value` and `max_value`
- **EmptyNoneMixin** - set value to None it is an empty value
- **PositiveValidationMixin** - shortcut to for `MinMaxValidationMixin` to make sure the value is positive
- **ProcessorsMixin** - to post process generated py-object value. It adds an additional attribute to your type `processors: Iterable[TCallableStr, ...] = ()`. Here is a small example that can make a truncate text using function [shorten function](https://docs.python.org/3/library/textwrap.html#textwrap.shorten)

```python
import textwrap

def shorten(value):
    return textwrap.shorten(value, width=20, placeholder='...')

SHORT_STR = mix(ProcessorsMixin, SimpleString)("This is string", processors=(shorten,))
```

- **GiveProcessorsMixin** - to post process setting value. The main difference with `ProcessorsMixin` - the value will be processed every time when you request the setting attribute. Additional attribute is `give_processors: Iterable[Union[TCallableStr, Tuple[Optional[str], TCallableStr]], ...] = ()`. In the same way as for `ProcessorsMixin.processors` you can add functions in the `give_processors`, but you can also add tuple with two arguments suffix as a string and function. Here are some of the examples:

```python
import textwrap

def shorten(value):
    return textwrap.shorten(value, width=20, placeholder='...')

SHORT_STR = mix(GiveProcessorsMixin, SimpleString)("This is string", give_processors=(shorten,))

# is the same as 
SHORT_STR = mix(GiveProcessorsMixin, SimpleString)("This is string", give_processors=((None, shorten),))

# you can define suffix and define give processor for the suffix only
SHORT_STR = mix(GiveProcessorsMixin, SimpleString)("This is string", suffixes={"copy": lambda x: x}, give_processors=(("copy", shorten),))
```

