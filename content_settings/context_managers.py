from contextlib import ContextDecorator


class content_settings_context(ContextDecorator):
    def __init__(self, **values) -> None:
        self.raise_errors = values.pop("_raise_errors", True)
        super().__init__()
        self.values_to_update = values
        self.prev_values = {}

    def __enter__(self):
        from content_settings.caching import set_new_value

        for name, new_value in self.values_to_update.items():
            try:
                self.prev_values[name] = set_new_value(name, new_value)
            except:
                if self.raise_errors:
                    raise

    def __exit__(self, *exc):
        from content_settings.caching import set_new_value

        for name, new_value in self.prev_values.items():
            set_new_value(name, new_value)
