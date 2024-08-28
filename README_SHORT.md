# Django Content Settings - the most advanced admin editable setting

The `django-content-settings` module is a versatile addition to the Django ecosystem, offering users the ability to easily create and manage editable variables directly from the Django admin panel. What sets this module apart is its ability to handle variables of any type without restricting their complexity. Thanks to an integrated caching system, these variables can be used efficiently in code, irrespective of their complexity.

### Key Features

1. **Type-Agnostic Variable Creation**: Users can create variables of any type, making the module highly adaptable to various needs.
2. **Editability from Django Admin Panel**: Seamless integration with the Django admin panel allows for effortless editing of variables.
3. **Flexible permission model**: Every setting can have its own permission rule for viewing, editing, fetching in API, and viewing changes history.
4. **Preview**: Preview the setting before applying and the option to preview the setting changes right on site.
5. **Caching System**: Ensures high performance, negating the impact of variable complexity on code execution speed.
6. **Export & Import**: Massively dump configuration into a file and massively load configuration from the file using UI or/and commands.

### Additional Admin Panel Functionalities

- **Change History**: Track and review the history of changes made to the variables.
- **Preview System**: Preview changes for different variable types before finalizing them.
- **Bulk Editing**: Facilitate the simultaneous editing of multiple variable types.
- **Permission System**: Control edit permissions for enhanced security and management.
- **Tags Navigation**: Every setting has a set of tags, which allows you to organize flexible navigation even with 1000 settings in the system.

For the full documentation, please visit [here](https://django-content-settings.readthedocs.io/).

### How does it look

- **Setup**. [Here](https://django-content-settings.readthedocs.io/en/master/first/) you can get step-by-step instruction.

- **Define the setting**. To do so you need to define constant in `content_settings.py` in your app

```python
# content_settings.py

from content_settings.types.basic import SimpleString

TITLE = SimpleString("Songs", help="The title of the site")
```

the code above defines a variable `TITLE`, with type `SimpleString` and default value `Songs`.

- **Migrate**. In order to be able to edit data in Django Admin

```bash
$ python manage.py migrate
```

_Technically, you can use variable in code even without migration. The migration is need to make variable editable in admin panel_

- **Use it in your project**. That is it. You can the variable `TITLE` in your code. 

```python

from content_settings.conf import content_settings

content_settings.TITLE
```

In template:

```html
<h2>{{CONTENT_SETTINGS.TITLE}}</h2>
```

### Quick Look

You should be able to quickly see how it works using `cs_test` project in the [repository](https://github.com/occipital/django-content-settings/t). You need to have [poetry](https://python-poetry.org/) installed.

```bash

$ git clone https://github.com/occipital/django-content-settings.git
$ cd django-content-settings
$ make init
$ make cs-test-migrate
$ make cs-test
```

the open `http://localhost:8000/admin/` in your browser and you should see the django admin panel.

the admin user is `admin` with password `1`.

# Whats next?

- [**Getting Started**](https://django-content-settings.readthedocs.io/en/master/first/) - this is a step-by-step guide to configure content settings in your project and add your first setting.
- [**Setting Types and Attributes**](https://django-content-settings.readthedocs.io/en/master/types/) - the guide of all available types and attributes, including some examples.
- [**Template Types**](https://django-content-settings.readthedocs.io/en/master/template_types/) - the most powerful part of content settings - Templates. Where setting raw value is a text, but setting value is a function.
- [**Using Settings**](https://django-content-settings.readthedocs.io/en/master/access/) - multiple ways to access content settings in your project.
- [**Permissions**](https://django-content-settings.readthedocs.io/en/master/permissions/) - different settings can have different permissions for different settings' functionality.
- [**Defaults Context**](https://django-content-settings.readthedocs.io/en/master/defaults/) - allows you to group settings with common parameters, reducing redundancy and making your code cleaner and more maintainable.
- [**API & Views**](https://django-content-settings.readthedocs.io/en/master/api/) - how to organize access to content settings through the API
- [**User Interface for Django Admin**](https://django-content-settings.readthedocs.io/en/master/ui/) - the guide is for end users, not only developers. It explains how to use the Django Admin panel for content settings.
- [**How Caching is Organized**](https://django-content-settings.readthedocs.io/en/master/caching/) - we want to make sure your content settings work as fast as possible. The guide explains how it is organized and what you can configure.
- [**Available Django Settings**](https://django-content-settings.readthedocs.io/en/master/settings/) - reference all available Django settings for content settings.
- [**User Defined Settings**](https://django-content-settings.readthedocs.io/en/master/uservar/) - *experimental functionality* - how to give Django Admin users functionality for creation settings right from Django Admin UI.
- [**Possible Extensions**](https://django-content-settings.readthedocs.io/en/master/extends/) - *wip* - all of the ways how you can extend the basic content settings functionality.
- [**Cookbook**](https://django-content-settings.readthedocs.io/en/master/cookbook/) - several simple receipts you can use in your project.
- [**Frequently Asked Questions**](https://django-content-settings.readthedocs.io/en/master/faq/) - before asking questions, you might want to visit this section.
- [**Glossary**](https://django-content-settings.readthedocs.io/en/master/glossary/) - the concept of content settings introduces several new terms, which we collected in this article
- [**How to contribute**](https://django-content-settings.readthedocs.io/en/master/contribute/) - if you are willing to help - welcome to the team.
- [**Changelog**](https://django-content-settings.readthedocs.io/en/master/changelog/) - what was introduces in every version.
- [**Source Doc**](https://django-content-settings.readthedocs.io/en/master/source/) - we collect all the doc strings in one article for future reference.