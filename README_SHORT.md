# Django Content Settings - The Most Advanced Admin Editable Setting

The `django-content-settings` module is a versatile addition to the Django ecosystem, allowing users to easily create and manage editable variables directly from the Django admin panel. What sets this module apart is its capability to handle variables of any type, without limiting their complexity. Thanks to an integrated caching system, these variables can be used efficiently in code, regardless of their complexity.

For the full documentation, please visit [here](https://django-content-settings.readthedocs.io/).

`django-content-settings` allows you to store variables with specific functionality in your code that can be validated and previewed in your Django admin panel. Validators, previewers, and all associated logic are defined in the setting configuration.

### Key Features

1. **Type-Agnostic Variable Creation**: Create variables of any type, making the module highly adaptable to diverse needs. [Learn more about basic types](https://django-content-settings.readthedocs.io/en/master/types/) and [template types](https://django-content-settings.readthedocs.io/en/master/template_types/).
2. **Flexible Permission Model**: Define custom permission rules for viewing, editing, fetching in APIs, and viewing the change history of each setting. [Learn more about the available API](https://django-content-settings.readthedocs.io/en/master/api/).
3. **Preview Functionality**: Preview settings before applying them, with the option to view changes directly on the site.
4. **Export & Import**: Export and import configurations in bulk using the UI or command-line tools.
5. **Editability via Django Admin Panel**: Seamlessly edit variables directly within the Django admin panel. [See how the Django Admin interface looks](https://django-content-settings.readthedocs.io/en/master/ui/).
6. **Caching System**: Optimized performance ensures variable complexity does not impact execution speed. [Learn more about caching and speed optimization](https://django-content-settings.readthedocs.io/en/master/caching/).
7. **Extensions**: Leverage a wide array of configuration options and extension points. [Explore available extensions](https://django-content-settings.readthedocs.io/en/master/extends/).

### Additional Admin Panel Functionalities

- **Change History**: Track and review changes made to variables.
- **Preview System**: Preview changes for different variable types before applying them.
- **Bulk Editing**: Edit multiple variables simultaneously.
- **Permission System**: Implement granular edit permissions for enhanced security and management.
- **Tags Navigation**: Organize settings with tags, enabling flexible navigation even with 1,000+ settings in the system.

[Learn more about these features here](https://django-content-settings.readthedocs.io/en/master/ui/).

### How It Works

- **Setup**: Follow the [step-by-step instructions here](https://django-content-settings.readthedocs.io/en/master/first/).

- **Define the Setting**: Add a constant in `content_settings.py` within your app.

```python
# content_settings.py

from content_settings.types.basic import SimpleString

TITLE = SimpleString("Songs", help="The title of the site")
```

The code above defines a variable `TITLE` with the type `SimpleString` and the default value `"Songs"`.

- **Migrate**: Run migrations to enable editing raw values in the Django Admin panel.

```bash
$ python manage.py migrate
```

You can use the setting in your code without running migrations, but migrations are required to make the setting editable in the admin panel.

- **Use It in Your Project**: Access the `TITLE` setting in your code.

```python
from content_settings.conf import content_settings

content_settings.TITLE
```

In a template:

```html
<h2>{{ CONTENT_SETTINGS.TITLE }}</h2>
```

[Learn more about accessing settings](https://django-content-settings.readthedocs.io/en/master/access/).

### Quick Look

You can quickly explore the functionality using the `cs_test` project in the [repository](https://github.com/occipital/django-content-settings). Ensure you have [Poetry](https://python-poetry.org/) installed.

```bash
$ git clone https://github.com/occipital/django-content-settings.git
$ cd django-content-settings
$ make init
$ make cs-test-migrate
$ make cs-test
```

Open `http://localhost:8000/admin/` in your browser to access the Django admin panel.

- Username: `admin`
- Password: `1`

# What's Next?

- [**Getting Started**](https://django-content-settings.readthedocs.io/en/master/first/): Step-by-step guide to configuring content settings in your project and adding your first setting.
- [**Setting Types and Attributes**](https://django-content-settings.readthedocs.io/en/master/types/): Guide to all available basic types and attributes, with examples.
- [**Template Types**](https://django-content-settings.readthedocs.io/en/master/template_types/): The most powerful feature of content settings, where raw values are text, but the setting value is a function.
- [**Using Settings**](https://django-content-settings.readthedocs.io/en/master/access/): Explore multiple ways to access content settings in your project.
- [**Permissions**](https://django-content-settings.readthedocs.io/en/master/permissions/): Define distinct permissions for different settings' functionality.
- [**Defaults Context**](https://django-content-settings.readthedocs.io/en/master/defaults/): Group settings with common parameters to reduce redundancy and maintain cleaner code.
- [**API & Views**](https://django-content-settings.readthedocs.io/en/master/api/): Organize access to content settings via APIs.
- [**User Interface for Django Admin**](https://django-content-settings.readthedocs.io/en/master/ui/): End-user guide to using the Django Admin panel for content settings.
- [**How Caching is Organized**](https://django-content-settings.readthedocs.io/en/master/caching/): Ensure fast and efficient content settings performance, with configurable options.
- [**Available Django Settings**](https://django-content-settings.readthedocs.io/en/master/settings/): Reference all available Django settings for content settings.
- [**User-Defined Settings**](https://django-content-settings.readthedocs.io/en/master/uservar/): *Experimental functionality* for allowing Django Admin users to create settings directly from the UI.
- [**Possible Extensions**](https://django-content-settings.readthedocs.io/en/master/extends/): *WIP* - Extend the basic functionality of content settings.
- [**Cookbook**](https://django-content-settings.readthedocs.io/en/master/cookbook/): Practical recipes for using content settings in your project.
- [**Frequently Asked Questions**](https://django-content-settings.readthedocs.io/en/master/faq/): Answers to common questions.
- [**Glossary**](https://django-content-settings.readthedocs.io/en/master/glossary/): Definitions of terms introduced by the concept of content settings.
- [**How to Contribute**](https://django-content-settings.readthedocs.io/en/master/contribute/): Guidelines for contributing to the project.
- [**Changelog**](https://django-content-settings.readthedocs.io/en/master/changelog/): Overview of updates introduced in each version.
- [**Source Doc**](https://django-content-settings.readthedocs.io/en/master/source/): Compilation of docstrings for future reference.