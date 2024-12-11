# User Defined Variables

## Introduction

The main concept of content settings is to allow you to define a constant in code that can be edited in the Django Admin panel. However, there might be a case when you need to create new content settings not in code but in the admin panel, and this is where user-defined types are used.

## How is it useful?

1. **Use in Template Variables**: If you have several template settings containing the same text, do not copy and paste the same text in each value - you can simply create your own content settings variable and use it for every template value.

2. **Flexibility for Developers**: You can have a view that fetches variables by tag (see [API](api.md#all-settings-that-matches-specific-conditions)), and by creating a new variable, you can add new data to the API response. Later, you can define the setting in code, which replaces the user-defined setting with a simple setting. On top of that, we have the prefix "withtag__", which allows you to get all of the settings with a specific tag.

## Setting Up User Defined Types

To enable the creation of such variables, you need to set up a specific setting that lists all the types available for creation:

```python
CONTENT_SETTINGS_USER_DEFINED_TYPES=[
    ("text", "content_settings.types.basic.SimpleText", "Text"),
    ("html", "content_settings.types.basic.SimpleHTML", "HTML"),
]
```

Read more about this setting [here](settings.md#content_settings_user_defined_types).

Having the Django setting set admin should see the "Add Content Settings" button at the top of the list of all available content settings (see [UI](ui.md#list-of-available-settings))

## Overwriting User-Defined Variables

It's important to note that if you decide to create a variable in the code that should overwrite a variable previously made in the admin panel, you will encounter a migration error. To avoid this, explicitly state that the code variable will overwrite the admin-created variable by setting `overwrite_user_defined=True`.

## Conclusion

User User-defined types in `django-content-settings` offer significant flexibility and customization for managing variables in Django applications. This feature empowers administrators to create and modify variables directly from the admin panel while still providing the option for developers to override these variables in the code if needed.

[![Stand With Ukraine](https://raw.githubusercontent.com/vshymanskyy/StandWithUkraine/main/banner-direct-single.svg)](https://stand-with-ukraine.pp.ua)