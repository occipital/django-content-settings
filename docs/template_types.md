# Templates

The most powerful part of Content Settings, where the raw value of your content settings is used to generate the actual value within your project.

The module introduces advanced variable types for template rendering and Python code evaluation, utilizing `CallToPythonMixin` to allow setting variables to be used as functions. The implementation of this mixin is explained here using the `SimpleFunc` type. However, in a real-world project, you may want to use more advanced types like `DjangoTemplate`, `DjangoModelTemplate`, `SimpleEval`, and more. Feel free to skip the explanation of `CallToPythonMixin` if you only need an overview of practical templates.

---

## CallToPythonMixin - Explanation (Can Be Skipped)

This mixin has two important methods you may want to override:

- `prepare_python_call`: Prepares the Python object and returns a dictionary used as `kwargs` for calling the attribute.
- `python_call`: This method is called when the user invokes the setting as a function.

If you don't want to override these methods, you can use attributes:

- **call_func**: Defines a function that will be executed when the user calls the attribute. By default, it is `lambda *args, prepared=None, **kwargs: prepared(*args, **kwargs)`.
- **call_prepare_func**: A function that processes values from Django Admin and stores them for use. By default, it is `lambda value: value`.
- **call_func_argument_name**: The argument name for the prepared value (default: `"prepared"`).

Using `call_prepare_func` and `call_func` together can boost performance.

### Example: `SimpleFunc`

The simplest use of `CallToPythonMixin` with a text value:

```python
class SimpleFunc(CallToPythonMixin, SimpleText):
    admin_preview_as = PREVIEW.PYTHON
```

#### Example 1: Logic Within Call

```python
THE_FUNC = SimpleFunc(
    "Welcome {name}",
    call_func=lambda name, prepared: prepared.format(name=name),
    validators=(call_validator("Alex"),),
)
```

Usage:

```python
print(content_settings.THE_FUNC("Alex"))
# Output: Welcome Alex
```

#### Example 2: Pre-processing Before Use

```python
THE_FUNC = SimpleFunc(
    "Welcome {name}",
    call_prepare_func=lambda value: value.format,
    validators=(call_validator(name="Alex"),),
)
```

Usage remains the same:

```python
print(content_settings.THE_FUNC(name="Alex"))
# Output: Welcome Alex
```

#### Example 3: Using Non-Text Input

```python
THE_SUM_FUNC = mix(CallToPythonMixin, SimpleInt)(
    "10",
    call_func=lambda value, prepared: prepared + value,
    validators=(call_validator(20),),
)
```

Usage:

```python
print(content_settings.THE_SUM_FUNC(12))
# Output: 22
```

These are basic examples, mainly for understanding how template types work.

---

## Types

### `DjangoTemplate` (`SimpleCallTemplate`)

Converts a raw value into a Django template and returns a function that takes arguments as context and returns the rendered value.

Example:

```python
WELCOME_TEXT = DjangoTemplate("Hi, {{name}}")
```

Usage:

```python
content_settings.WELCOME_TEXT() # Output: Hi,
content_settings.WELCOME_TEXT(name="Alex") # Output: Hi, Alex
```

You can define **default arguments**:

```python
WELCOME_TEXT = DjangoTemplate("Hi, {{name}}", template_args_default={"name": "Alex"})
```

**Required Arguments**:

```python
from content_settings.types import required
WELCOME_TEXT = DjangoTemplate("Hi, {{name}}", template_args_default={"name": required})
```

To render in a Django template:

```html
{% load content_settings_extras %}
<b>{% content_settings_call "WELCOME_TEXT" "Bob" %}</b>
```

---

### `DjangoTemplateNoArgs` (`GiveCallMixin`, `DjangoTemplate`)

Similar to `DjangoTemplate`, but doesn't require calling to render. The value is rendered automatically:

```python
AVATAR = DjangoTemplateNoArgs("""<img src="{{SETTINGS.STATIC_URL}}test.png" />""")
content_settings.AVATAR # Output: <img src="/static/test.png" />
```

---

### `DjangoModelTemplate` (`DjangoModelTemplateMixin`, `DjangoTemplate`)

Similar to `DjangoTemplate`, but accepts a model object as the first argument.

```python
from django.contrib.auth.models import User

WELCOME_TEXT = DjangoModelTemplate("Hi, {{object.username}}", template_model_queryset=User.objects.all())
```

Usage:

```python
cur_user = User.objects.get(id=1)
content_settings.WELCOME_TEXT(cur_user)
```

---

### `SimpleEval` (`SimpleCallTemplate`)

Stores Python code as the setting's value. When called, arguments are passed to the code execution. Similar to `DjangoTemplate`, `SimpleEval` compiles the code before use.

```python
THE_PRICE = SimpleEval('100 + addition', template_args_default={"addition": 0})
content_settings.THE_PRICE() # Output: 100
content_settings.THE_PRICE(20) # Output: 120
```

To extend the context:

```python
from content_settings.types.template import required
from decimal import Decimal

COMMISSION = SimpleEval(
    "total * Decimal('0.2')",
    template_args_default={"total": required},
    template_static_data={"Decimal": Decimal},
)
content_settings.COMMISSION(Decimal('100')) # Output: Decimal("20")
```

---

### `SimpleExec` (`SystemExec`, `SimpleCallTemplate`)

Uses `exec` instead of `eval` to execute Python code. Always returns a dictionary with the executed context. Configure `template_return` to control what part of the context to return:

Options for `template_return`:
- `None`: Returns the entire context.
- `str`: Returns a specific variable from the context.
- `dict`: Returns specific keys from the context.
- `list` or `tuple`: List of keys to return.
- `function`: A function that returns a dictionary with default values.

#### Example with `template_return`:

```python
THE_VALUE = SimpleExec("""
result = 5
""", template_return="result")
content_settings.THE_VALUE() # Output: 5
```

---

## Calling Functions in Template

To render a callable setting like `DjangoTemplate` or `SimpleEval` in a template:

```html
{% load content_settings_extras %}
{% content_settings_call "WELCOME_TEXT" "Bob" %}
```

---

## Validators for Templates

### `call_validator`

Validates the function by calling it without exceptions for specific arguments.

```python
from content_settings.types.validators import call_validator

PLUS_ONE = SimpleEval(
    "1 + val",
    validators=(call_validator(), call_validator(0), call_validator(-1), call_validator(100)),
    template_args_default={"val": 3},
)
```

### `result_validator`

Use this validator to ensure the result meets specific criteria.

```python
from content_settings.types.validators import result_validator

PLUS_ONE = SimpleEval(
    "1 + val",
    validators=(result_validator(lambda val: isinstance(val, int), "The result should be an int", 100)),
    template_args_default={"val": 3},
)
```

---

## Setting Evaluation and Flexibility

Template settings provide a powerful mechanism for evaluating logic within a project, allowing easy switching between flexible user-defined calculations and more stable default values. Using mixins like `MakeCallMixin`, you can maintain backward compatibility with callable settings, even as their underlying types change.

---

[![Stand With Ukraine](https://raw.githubusercontent.com/vshymanskyy/StandWithUkraine/main/banner-direct-single.svg)](https://stand-with-ukraine.pp.ua)
