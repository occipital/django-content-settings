[![Stand With Ukraine](https://raw.githubusercontent.com/vshymanskyy/StandWithUkraine/main/banner-direct-single.svg)](https://stand-with-ukraine.pp.ua)

![Django Content Settings](img/title.png)

# Django Content Settings - the most advanced admin editable setting

The `django-content-settings` module is a versatile addition to the Django ecosystem, offering users the ability to easily create and manage editable variables directly from the Django admin panel. What sets this module apart is its ability to handle variables of any type without restricting their complexity. Thanks to an integrated caching system, these variables can be used efficiently in code, irrespective of their complexity.

With `django-content-settings` allows you to store variables with specific functionality in your code, that can be validated and previed in your django admin panel. The validators, previewers and all of the logic is stored in the setting definition.

*the project is in active development. [Those are the tickets left](https://github.com/occipital/django-content-settings/issues?q=is%3Aopen+is%3Aissue+label%3Av1) for releasing 1.0 version*

### Key Features

1. **Type-Agnostic Variable Creation**: Users can create variables of any type, making the module highly adaptable to various needs.
2. **Editability from Django Admin Panel**: Seamless integration with the Django admin panel allows for effortless editing of variables.
3. **Flaxable permission model**: Every setting can have own permission rule for view, edit, fetch in API and view changes history.
4. **Validation**: Every setting can have own validation not only for itself but for the other settings. So you can control so the setting update doesn't break the system.
5. **Preview**: Preview setting before apply and addition option to preview setting change right on site.
6. **Caching System**: Ensures high performance, negating the impact of variable complexity on code execution speed.

### Additional Admin Panel Functionalities

- **Change History**: Track and review the history of changes made to the variables.
- **Preview System**: Preview changes for different variable types before finalizing them.
- **Bulk Editing**: Facilitate the simultaneous editing of multiple variable types.
- **Permission System**: Control edit permissions for enhanced security and management.

### API Integration

The module comes with a built-in API system, enabling:

- **Reading of Individual or Group Variables**: Allows for flexible data retrieval.
- **Access Permissions**: Manage who can read the variables, ensuring data privacy and security.

### How does it look

- **Setup**. [Here](first.md) you can get step-by-step instruction.

- **Define the setting**. To do so you need to define constant in `content_settings.py` in your app

```python
# content_settings.py

from content_settings.types.basic import SimpleString

TITLE = SimpleString("Songs", help="The title of the site")
```

the code above defines a variable `TITLE`, with type `SimpleString` and default value `Songs`.

- **Migrate**. In order to be able to edit *raw value* in Django Admin

```bash
$ python manage.py migrate
```

Technically, you can *use setting* in code even without migration. The migration is need to make setting editable in admin panel

- **Use it in your project**. That is it. You can *use setting* `TITLE` in your code. 

```python

from content_settings.conf import content_settings

content_settings.TITLE
```

or use object `settings` that unites content settings and django settings in one place

```python

from content_settings.conf import settings

settings.TITLE
```

In template:

```html
<h2>{{CONTENT_SETTINGS.TITLE}}</h2>
```

Simple as that, we have a lot of *setting types* you can use `SimpleText`, `SimpleHTML`, `SimpleInt`, `SimpleBool`, `SimpleDecimal`, `DateTimeString`, `SimpleTimedelta`, `SimpleYAML`, `SimpleJSON`, `SimpleCSV`, `DjangoTemplate`, `DjangoModelTemplate`, `SimpleEval`, `SimpleExec` and so on... [Read more](types.md) about the types available for you.

# Whats next?

- [**Getting Started**](first.md) - this is a step-by-step guide to configure content settings in your project and add your first setting.
- [**Setting Types and Attributes**](types.md) - the guide of all available types and attributes, including some examples.
- [**Using Settings**](access.md) - multiple ways to access content settings in your project.
- [**Permissions**](permissions.md) - different settings can have different permissions for different settings' functionality.
- [**Defaults Context**](defaults.md) - allows you to group settings with common parameters, reducing redundancy and making your code cleaner and more maintainable.
- [**API & Views**](api.md) - how to organize access to content settings through the API
- [**User Interface for Django Admin**](ui.md) - the guide is for end users, not only developers. It explains how to use the Django Admin panel for content settings.
- [**How Caching is Organized**](caching.md) - we want to make sure your content settings work as fast as possible. The guide explains how it is organized and what you can configure.
- [**Available Django Settings**](settings.md) - reference all available Django settings for content settings.
- [**User Defined Settings**](uservar.md) - *experimental functionality* - how to give Django Admin users functionality for creation settings right from Django Admin UI.
- [**Cookbook**](cookbook.md) - several simple receipts you can use in your project.
- [**Frequently Asked Questions**](faq.md) - before asking questions, you might want to visit this section.
- [**Glossary**](glossary.md) - the concept of content settings introduces several new terms, which we collected in this article
- [**How to contribute**](contribute.md) - if you are willing to help - welcome to the team.
- [**Changelog**](changelog.md) - what was introduces in every version.
- [**Source Doc**](source.md) - we collect all the doc strings in one article for future reference.

It is also very fast thanks to our caching system. [Read more about it](caching.md).

Some fancy things you can find in our [cookbook](cookbook.md).