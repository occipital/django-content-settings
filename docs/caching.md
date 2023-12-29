![Django Content Settings](img/title_8.png)

# How Caching is Organized

## Introduction

This article aims to explain the caching system implemented in the `django-content-settings` module, detailing its structure and the elements that can be controlled by the user. The code related to caching is located in the `content_settings.caching` module *([source](https://github.com/occipital/django-content-settings/blob/master/content_settings/caching.py))* and in the `content_settings.signals` module *([source](https://github.com/occipital/django-content-settings/blob/master/content_settings/signals.py))*.

## Caching Mechanism

### Django's Standard Caching Backend

- **Usage**: `django-content-settings` utilizes Django's standard caching backend. For more details, refer to Django's official documentation.
- **Operation**: The cache stores an MD5 hash of all string values of the variables (the values stored in the database).
- **Key Composition**: The cache key is composed of three elements:
  - **Prefix**: Defined by the `CONTENT_SETTINGS_CHECKSUM_KEY_PREFIX` setting in the project's `settings.py`.
  - **Package Version**: The current version of the `django-content-settings` package.
  - **MD5 Hash**: An MD5 hash of all variable versions.

### Cache Functionality

- **Purpose**: The cache acts as a signal to update values rather than storing the values themselves.
- **Process**: When a new request is made, the worker first checks if the version it holds is the latest. If the hash value has changed, the worker queries the database to determine which specific value was modified and converts it into an object again.
- **Storage**: All converted objects are stored in a global variable and are converted once at the process's startup or when a change is detected in the database values.

### Version Management

- **Importance**: The version indicates the handler's version, ensuring that the current values in the database can be safely read by the process.
- **Update Scenarios**: Updating the version is sensible in two cases:
  1. To reset values to their default settings.
  2. When the format of a variable's type has been changed.

### Migration and Version Update

- **Behavior**: If the version value is updated, the migration process will reset the database values to their default settings. This approach ensures that the system can handle changes in variable types or default values effectively.

## Summary

The caching system in `django-content-settings` is designed to optimize performance and maintain consistency. It ensures that variable values are updated efficiently and that the system can adapt to changes in variable types or default settings. This detailed explanation provides an insight into how caching is strategically utilized within the module to enhance the functionality and reliability of the content settings in Django applications.
