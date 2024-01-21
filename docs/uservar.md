# User Defined Variables

## Introduction

This article explores the concept of User Defined Types in the `django-content-settings` module. This functionality allows for the creation of variables directly within the Django admin panel, as opposed to solely in the code.

## Why User Defined Types?

Creating variables in the admin panel might seem redundant if variables are primarily used in code. However, there are several reasons why this feature can be beneficial:

1. **Access to a List of Variables**: You can access a list of all created variables using `conf.startswith` or `conf.withtag` functions, making it easy to work with variables based on certain criteria.
2. **Use in Template Variables**: Variables can be utilized in the values of template variables, allowing users to incorporate any variable into template settings.
3. **Flexibility for Developers**: Developers can first create new APIs and then establish their code bindings, providing a more flexible development process.

## Setting Up User Defined Types

To enable the creation of such variables, you need to set up a specific setting that lists all the types available for creation:

```python
CONTENT_SETTINGS_USER_DEFINED_TYPES=[
    (
        "line",
        "books.content_settings.PublicSimpleString",
        "Line (Public)",
    ),
    ("text", "content_settings.types.basic.SimpleText", "Text"),
    ("html", "content_settings.types.basic.SimpleHTML", "HTML"),
]
```

### Explanation

- **Setting Structure**: The setting is an array where each element is a tuple consisting of three parts:
  1. A unique slug stored in the database.
  2. The path to the type.
  3. The name of the type in the admin panel.

Once this setting is configured, you can start creating your own variables in the admin panel, which will have all the capabilities of standard variables created in the code.

## Overwriting User Defined Variables

It's important to note that if you decide to create a variable in the code that should overwrite a variable previously created in the admin panel, you will encounter a migration error. To avoid this, explicitly state that the code variable will overwrite the admin-created variable by setting `overwrite_user_defined=True`.

## Conclusion

User Defined Types in `django-content-settings` offer significant flexibility and customization for managing variables in Django applications. This feature empowers administrators to create and modify variables directly from the admin panel, while still providing the option for developers to override these variables in the code if needed.
