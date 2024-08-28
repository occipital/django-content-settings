# Templates

The most powerful part of Content Setting, where the raw value of your content settings is a string that is used for generating actual value in the project.

Module introduces advanced variable types designed for template rendering and Python code evaluation using `CallToPythonMixin` for using setting variables as functions. I'll explain the mixing implanation on `SimpleFunc` type, but in the actual project you may want to use more advanced types such as `DjangoTemplate`, `DjangoModelTemplate`, `SimpleEval` and so on. It is ok to skip the explanation of the `CallToPythonMixin`.

## CallToPythonMixin - the explanation that can be skipped

The mixin has two most important methods you may want to redefine:

* `prepare_python_call` - the function gets py object as an attribute and returns a dict that will be used in kwargs of the attribute call
* `python_call` - is the function that would be called when the user calls a function that is returned by the attribute

If you don't want to overwrite the method, you can use attributes.

* `call_func` - the function would be called when the user uses an attribute (uses by `python_call`). It accepts all of the args and kwargs passed to the function when it is called + one more kwarg, by default "prepared", with the value returned by `prepare_python_call`. By default it is `lambda *args, prepared=None, **kwargs: prepared(*args, **kwargs)`
* `call_prepare_func` - a function that prepares value from Django admin and stores it in the context of python value, By default it is `lambda value: value`
* `call_func_argument_name` - the name of the attribute for the prepared value. By default, "prepared"

With the combination of `call_prepared_func` and `call_func` you can get a performance boost when you using it in code.

- **SimpleFunc**: The simplest use of `CallToPythonMixin` with text value. The definition of the type is super simple:

```python
class SimpleFunc(CallToPythonMixin, SimpleText):
 admin_preview_as: PREVIEW = PREVIEW.PYTHON
```

The first example is when all of the logic is inside of the actual call:

```python
THE_FUNC = SimpleFunc(
    "Welcome {name}",
 call_func=lambda name, prepared: prepared.format(name=name),
 validators=(call_validator("Aex"),),
)
```

in the code it would be:

```python
print(content_settings.THE_FUNC("Alex"))
# Welcome Alex
```

*Make sure you add a `call_validator` so the function has a preview in Django Admin*

The second example illustrates using of some kind of preparation before using:

```python
THE_FUNC = SimpleFunc(
    "Welcome {name}",
 call_prepare_func=lambda value: value.format
 validators=(call_validator(name="Aex"),),
)
``` 

In the code, it would be almost the same as in the first example:

```python
print(content_settings.THE_FUNC(name="Alex"))
# Welcome Alex
```

*In the second example, the preparation function would be called when the type is defined or the value is updated*

The third example is a bonus one, in case you want to use not only text value as in input.

```python
THE_SUM_FUNC = mix(CallToPythonMixin, SimpleInt)(
    "10",
 call_func=lambda value, prepared: prepared + value,
 validators=(call_validator(20),),
)
```

*In that case, the value is an int, so it will be parsed and validated by `SimpleInt` class*

In the code, it is still the same.

```python
print(content_settings.THE_SUM_FUNC(12))
# 22
```

Those are very basic examples; you might not use those, but it can be helpful to understand how the other template types are working.

## Types

Below, we will show you some examples of template types you can use in your code. You can find the full list in the [source doc](source.md#typestemplate).

### DjangoTemplate(SimpleCallTemplate)

The most basic one converts raw value into template and value into a function that takes all of the kwargs into template context and returns the rendered value.

Example:

```python
WELCOME_TEXT = DjangoTemplate("Hi, {{name}}")
```

In the code, you can do the following:

```python
content_settings.WELCOME_TEXT() # Hi,
content_settings.WELCOME_TEXT(name="Alex") # Hi, Alex
content_settings.WELCOME_TEXT(last="L") # Hi,
```

**You can also define default arguments**. Example:

```python
WELCOME_TEXT = DjangoTemplate("Hi, {{name}}", template_args_default={"name": "Alex"})
```

In the code:

```python
content_settings.WELCOME_TEXT() # Hi, Alex
content_settings.WELCOME_TEXT("Bob") # Hi, Bob
content_settings.WELCOME_TEXT(name="Bob") # Hi, Bob
```

**You can make required arguments**. Example:

```python
from content_settings.types import required
WELCOME_TEXT = DjangoTemplate("Hi, {{name}}", template_args_default={"name": required})
```

In the code:

```python
content_settings.WELCOME_TEXT() # ValidationError
content_settings.WELCOME_TEXT("Bob") # Hi, Bob
content_settings.WELCOME_TEXT(name="Bob") # Hi, Bob
```

**In the template you can use both content_settings or settings**. Example:

```python
AVATAR = DjangoTemplate("<img src='{{SETTINGS.STATIC_URL}}{{name}}.png' />")
WELCOME_TEXT = DjangoTemplate("Welcome {{name}} in our project {{CONTENT_SETTINGS.TITLE}}")
```

**How to render DjangoTemplate setting in your template?**

You need to use `content_settings_call` template tag from `content_settings_extras` tags library. Example:

```html
{% load content_settings_extras %}

<b>{% content_settings_call "WELCOME_TEXT" "Bob" %}</b>
```

it is the same as:

```python
content_settings.WELCOME_TEXT("Bob")
```

**How does preview work?**

By default, rendering for the preview will be taken from the first validator, and by default, the validator will call the setting without arguments.

You can assign and add more validators using `call_validator`

```python
from content_settings.types import required
from content_settings.types.validators import call_validator

WELCOME_TEXT = DjangoTemplate("Hi, {{name}}", template_args_default={"name": required}, validators=(call_validator("Test Name"),))
```

`DjangoTemplate` attributes are inherited from `SimpleCallTemplate`, see [docscring](source.md#class-simplecalltemplatecalltopythonmixin-staticdatamixin-simpletextsource)

- **template_args_default**: (Optional) A dictionary that converts an array of arguments, with which the function is called, into a dictionary passed as context to the template. To set required arguments, import `required` from `content_settings.types.template` and use it as a value.
- **template_static_data**: (Optional) A dictionary of additional values that can be passed to the template from global env (not as arguments to the function). It can also be a function
- **template_static_includes** (default: `('CONTENT_SETTINGS', 'SETTINGS')`) - by default, both `content_settings` and `settings` are included in context, but by adjusting this tuple, you can change that.

`SimpleCallTemplate` is not covered here, but it is a base for `SimpleEval` and `SimpleExec`, which are covered here.

### DjangoTemplateHTML(HTMLMixin, DjangoTemplate)

Same as `DjangoTemplate` but will be rendered and previewed as HTML. In the template, it will be rendered as safe.

### DjangoTemplateNoArgs(GiveCallMixin, DjangoTemplate)

Same as `DjangoTemplate`, but it does not require calling for rendering. Example:

```python
AVATAR = DjangoTemplateNoArgs("""<img src="{{SETTINGS.STATIC_URL}}test.png" />""")
```

In code, you don't need to call the function to render the template. Instead, the template will be rendered every time you get access to the setting attribute:

```python
content_settings.AVATAR # <img src="/static/test.png" />
```

### DjangoTemplateNoArgsHTML(HTMLMixin, DjangoTemplateNoArgs)

Same as `DjangoTemplateNoArgs` but will be rendered and previewed as HTML. In the template, it will be rendered as safe.

### DjangoModelTemplate(DjangoModelTemplateMixin, DjangoTemplate)

It is the same as `DjangoTemplate`, but it takes the first argument as a model object. The optimization here is a preview that will be rendered from the first object of the given query set in the attribute `template_model_queryset`

For example:

```python
from django.contrib.auth.models import User

WELCOME_TEXT = DjangoModelTemplate("Hi, {{object.username}}", template_model_queryset=User.objects.all())
```

You can define the name of the object in the context. In our case, we want it to be "user," so the type definition can be changed using the `template_object_name` attribute:

```python
from django.contrib.auth.models import User

WELCOME_TEXT = DjangoModelTemplate("Hi, {{user.username}}", template_model_queryset=User.objects.all(), template_object_name="user")
```

From `template_model_queryset`, we can use a function to control import order:

```python
def first_user():
    from django.contrib.auth.models import User

    return User.objects.all().first()


WELCOME_TEXT = DjangoModelTemplate("Hi, {{user.username}}", template_object_name="user", template_model_queryset=first_user)
```

Nothing unusual in the code:

```python
cur_user = User.objects.get(id=1)
content_settings.WELCOME_TEXT(cur_user)
```

### DjangoModelTemplateHTML(DjangoModelTemplate)

Same as `DjangoModelTemplate` but for HTML rendering

### SimpleEval(SimpleCallTemplate)

Designed to store Python code as the setting's value. When the function is called, the argument dict is passed to the code execution. Same as in the `DjangoTemplate` type, `SimpleEval` is compiled before use, so the speed of using it is fast enough.

`SimpleEval` is based on `SimpleCallTemplate`, the same as `DjangoTemplate`, so it has all the same attributes such as `template_args_default`

Let me show a couple of examples:

```python
THE_PRICE = SimpleEval('100')
content_settings.THE_PRICE # 100

THE_PRICE = SimpleEval('100 + addition', template_args_default={"addition": 0})
content_settings.THE_PRICE() # 100
content_settings.THE_PRICE(20) # 120

THE_LOGO_LINK = SimpleEval('SETTINGS.STATIC_URL + "logo.png"')
content_settings.THE_LOGO_LINK() # /static/logo.png
```

the text of the value will be interpreted using builtin [`eval`](https://docs.python.org/3/library/functions.html#eval) function with it restrictions. If you want to use `exec` function, you should use `SimpleExec` which will be covered later.

If you want to extend context, you can use the `template_static_data` attribute from `SimpleCallTemplate`. For example:

```python
from content_settings.types.template import required

COMMISSION = SimpleEval(
  "total * Decimal('0.2')",
 template_args_default={
    "Total": required,
 },
 template_static_data={
    "Decimal": Decimal,
 }

)

# in code
content_settings.COMMISSION(Decimal('100')) # Decimal("20")
```

### SimpleEvalNoArgs(GiveCallMixin, SimpleEval)

It is the same as `SimpleEval`, but the setting value is not callable but already evaluated. Similar to `DjangoTemplateNoArgs`

### DjangoModelEval(DjangoModelTemplateMixin, SimpleEval)

Same as `SimpleEval` but uses one value as a model object. Similar to `DjangoModelTemplate`

### SimpleExec(SystemExec, SimpleCallTemplate)

Similar to the `SimpleEval` but use [`exec`](https://docs.python.org/3/library/functions.html#exec) instead of `eval`. Parent class `SystemExec` is responsable for calling `exec` function.

Since the `exec` doesn't return the value but generates (or extends) the context - the setting value always returns the dict, and the `template_return` attribute shows what will be in the dict.

There are four options for what `template_return` can be:

* `None` (by default) - the full context will be returned
* `str` - the name of the variable that  will be returned
* `dict` - only keys from the given dict is taken from the context and values of the dict are used as defaults
* `list` or `tuple` - list of keys from the context
* `function` - that returns dict with default values

On top of that `SimpleEval` has several additional attributes:

* `template_bultins`, responsible for limiting builtin env. By default it is `"BUILTINS_SAFE"` all functions except `memoryview`, `open`, `input` and `import`. If you want to include import use `"BUILTINS_ALLOW_IMPORT"`, if you don't want to use any limitation - just assign `None` to the attribute.
* `template_raise_return_error`, by setting this attribute to True missed values in the context raises `ValidationError`, otherwise returns `None`

Those are simple examples of using different `template_return` attribute:

```python
# Return the whole context
THE_VALUE = SimpleExec("""
result = 5
""")

content_settings.THE_VALUE()["result"] # 5

# We want only one value from the context be returned
THE_VALUE = SimpleExec("""
result = 5
""", template_return="result")

content_settings.THE_VALUE() # 5

# We want to return 2 values fees and final
# but gets one argument price
THE_PRICE = SimpleExec("""
fee = price // 3
final = price - fee
""",
 template_return=["fee", "final"],
 template_args_default={"price": required}
)

content_settings.THE_PRICE(25) # {"fee": 8, "final": 17}
```

### SimpleExecNoArgs(GiveCallMixin, SimpleExec)

Same as `SimpleExec`, but the setting value is not callable, but already evaluated. Similar to `DjangoTemplateNoArgs`

### DjangoModelExec(DjangoModelTemplateMixin, SimpleExec)

Same as `SimpleExec` but uses one value as a model object. Similar to `DjangoModelTemplate`

### SimpleExecNoCompile(SystemExec, StaticDataMixin, SimpleText)

It works in the same way as `SimpleExecNoArgs` but it executes the code only once for creation py object, where `SimpleExecNoArgs` compiled once and executes everytime when you access the variable.

*It is a more natural way to go, but at the same time more dangures, as it keeps all of the globals in the context of the first execution. You should be aware of it when you use it*

## Calling Functions in Template *([source](source.md#templatetagscontent_settings_extras))*

If you want to create a callable setting, such as `DjangoTemplate` or `SimpleEval`, you can render the result of calling in your template using `content_settings_call` tag from `content_settings_extras` library:

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

Or you can call function and not use it for rendering:


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
 {% content_settings_call "IS_BOOK_SHOWN" book as is_book_shown %}

 {% if is_book_shown %}
 {{book}}
 {% endif %}
 {% empty %}
                <li>No books found.</li>
 {% endfor %}
    </body>
</html>
```

## How to build validators

The calidators is important part of Exec and Eval types as user has almost endless flexibility in defining resulted value. In order to limit user you should use validators.

Moreover, validators are also used for admin preview because in admin preview, you need to show how the result of the function call should look.

### Call Validator

The most simple is `call_validator` from `types. validators`. It just validates that the function is called without exceptions for specific arguments.

```python
PLUS_ONE = SimpleEval(
    "1+val",
 validators=(
 call_validator(),
 ),
 template_args_default={"val": 3},
)
```

That would create a validator for calling without arguments. The preview should look like that

```
>>> PLUS_ONE()
<<< 4
```

The good news here is that if the variables doesn't have required arguments - the system generates such empty validator automatically, so the example bellow is the same as the example above.

```python
PLUS_ONE = SimpleEval(
    "1+val",
 template_args_default={"val": 3},
)
```

If you  want to test a function call with different arguments - just pass those arguments to the function `call_validator`

```python
from content_settings.types.validators import call_validator

PLUS_ONE = SimpleEval(
    "1+val",
 validators=(
 call_validator(),
 call_validator(0),
 call_validator(-1),
 call_validator(100),
 ),
 template_args_default={"val": 3},
)
```

The preview will look like the following:

```
>>> PLUS_ONE()
<<< 4
>>> PLUS_ONE(0)
<<< 1
>>> PLUS_ONE(-1)
<<< 0
>>> PLUS_ONE(100)
<<< 101
```

That would help you not only to veryfy the setting value but to see how the result of the value should look like.

### Result Validator

With call_validator you can preview the result, but what if you need to validate the result somehow. Use `result_validator`

```python
from content_settings.types.validators import call_validator, result_validator

PLUS_ONE = SimpleEval(
    "1+val",
 validators=(
 call_validator(),
 result_validator(lambda val: isinstance(value, int), "The result should be int", 100)
 ),
 template_args_default={"val": 3},
)
```

in the example function will be called with one argument 100, and if the result is not it - the error message will be shown: "The result should be int."

### Custom Validator

You can create your own validator. It is a function that accepts a function as the only argument.

```python

def is_int(func):
    if not isinstance(func(), int):
        raise ValidationError("The result should be int")

PLUS_ONE = SimpleEval(
    "1+val",
 validators=(
 is_int
 ),
 template_args_default={"val": 3},
)
```

Even if you have one custom validator - the systems add one validator with no arguments just for preview, so your preview should look like this:

```
>>> PLUS_ONE()
<<< 4
```

Your custom validator will be executed as well, but the execution won't be shown. In case of the fail validation - the error will be shown in the preview:

```
>>> PLUS_ONE()
<<< '4'
>>> PLUS_ONE(???)
ERROR!!! ['The result should be int']
```

"???" sign instead of arguments tells us that we don't know which arguments were used to call the function. If you want to provide those arguments, you should use a different exception.

```python

from content_settings.types.validators import PreviewValidationError

def is_int(func):
    if not isinstance(func(5), int):
        raise PreviewValidationError("5", "The result should be int")
```

The function takes as a first argument - string representation of the passed arguments. This is what the result might look like:

```
>>> PLUS_ONE()
<<< '4'
>>> PLUS_ONE(5)
ERROR!!! ['The result should be int']
```

If you want to show valid call without exception you should use `PreviewValidator`, so the final version of your validator should look like

```python
from content_settings.types.validators import PreviewValidationError, PreviewValidator

def is_int(func):
 ret = func(5)
    if not isinstance(ret, int):
        raise PreviewValidationError("5", "The result should be int")
    return PreviewValidator("5", ret)
```

## Setting Evaluation

Another advantage of the template settings is evaluation. Imagine the following.

* In the first iteration, you want a lot of flexibility for defining service fees by the user, so your setting definition can be

```python
SERVICE_FEE_PERCENT = DjangoModelEval(
    "5 if user.id in [1, 67] else 10",
 template_object_name="user",
 template_model_queryset=User.objects.all(),
)

# in code
content_settings.SERVICE_FEE_PERCENT(user)
```

* later on, when you have the fee settle, and you don't want that kind of flexibility, you may change the type for the setting

```python
SERVICE_FEE_PERCENT = SimpleInt("10")

# in code
content_settings.SERVICE_FEE_PERCENT # 10
```

But if you don't want to change the code, you can make it mixin with `MakeCallMixin`

```python
SERVICE_FEE_PERCENT = mix(MakeCallMixin, SimpleInt)("10")

# in code
content_settings.SERVICE_FEE_PERCENT(user) # 10
```

You have a simpler variable but still callable for back compatibility

* as the last step, you don't want to have this setting even editable - you set `contant=True` for the setting. In that case, the constant will be removed from the DB, and only the default value is used

```python
SERVICE_FEE_PERCENT = mix(MakeCallMixin, SimpleInt)("10", constant=True)

# in code
content_settings.SERVICE_FEE_PERCENT(user) # 10
```

[![Stand With Ukraine](https://raw.githubusercontent.com/vshymanskyy/StandWithUkraine/main/banner-direct-single.svg)](https://stand-with-ukraine.pp.ua)