"""
context managers for the content settings, but not all `defaults` context manager can be found in `content_settings.defaults.context.defaults`
"""

from contextlib import ContextDecorator


class content_settings_context(ContextDecorator):
    """
    context manager that overwrites settings in the context.

    `**kwargs` for the context manager are the settings to overwrite, where key is a setting name and value is a raw value of the setting.

    outside of the content_settings module can be used for testing.

    `_raise_errors: bool = True` - if False, then ignore errors when applying value of the setting.
    """

    def __init__(self, **values) -> None:
        self.raise_errors = values.pop("_raise_errors", True)
        super().__init__()
        self.values_to_update = values
        self.prev_values = {}
        self.prev_types = {}

    def __enter__(self):
        from content_settings.caching import set_new_value, set_new_type

        for name, new_value in self.values_to_update.items():
            if isinstance(new_value, tuple):
                new_value, *type_define = new_value
                try:
                    self.prev_types[name] = set_new_type(name, *type_define)
                except:
                    if self.raise_errors:
                        raise
            try:
                self.prev_values[name] = set_new_value(name, new_value)
            except:
                if self.raise_errors:
                    raise

    def __exit__(self, *exc):
        from content_settings.caching import (
            set_new_value,
            replace_user_type,
            delete_user_value,
            delete_value,
        )

        for name, new_value in self.prev_values.items():
            if name in self.prev_types:
                if self.prev_types[name] is None:
                    delete_user_value(name)
                    continue
                replace_user_type(name, self.prev_types[name])
            if new_value is None:
                delete_value(name)
            else:
                set_new_value(name, new_value)
