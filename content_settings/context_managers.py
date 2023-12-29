from contextlib import contextmanager, ContextDecorator

CONTEXT_DEFAULTS_STACK = []
CONTEXT_DEFAULTS_PROCESSORS_STACK = []


class process:
    def __init__(self, **kwargs):
        self.kwargs = kwargs

    def process(self, kwargs):
        raise NotImplementedError()


class process_set(process):
    def process(self, kwargs):
        return {
            name: self.process_one(
                kwargs.get(name, set()),
                set([value]) if isinstance(value, str) else set(value),
            )
            for name, value in self.kwargs.items()
        }


class set_add(process_set):
    def process_one(self, start, change):
        return start | change


class set_remove(process_set):
    def process_one(self, start, change):
        return start - change


@contextmanager
def context_defaults(*args, **kwargs):
    CONTEXT_DEFAULTS_STACK.append(kwargs)
    CONTEXT_DEFAULTS_PROCESSORS_STACK.append(args)
    try:
        yield
    finally:
        CONTEXT_DEFAULTS_STACK.pop()
        CONTEXT_DEFAULTS_PROCESSORS_STACK.pop()


def context_defaults_kwargs():
    kwargs = {}

    for processors, new_kwargs in zip(
        CONTEXT_DEFAULTS_PROCESSORS_STACK, CONTEXT_DEFAULTS_STACK
    ):
        for processor in processors:
            for name, value in processor.process(kwargs).items():
                kwargs[name] = value

        for name, value in new_kwargs.items():
            kwargs[name] = value

    return kwargs


class content_settings_context(ContextDecorator):
    def __init__(self, **values) -> None:
        super().__init__()
        self.values_to_update = values
        self.prev_values = {}

    def __enter__(self):
        from content_settings.caching import set_new_value

        for name, new_value in self.values_to_update.items():
            self.prev_values[name] = set_new_value(name, new_value)

    def __exit__(self, *exc):
        from content_settings.caching import set_new_value

        for name, new_value in self.prev_values.items():
            set_new_value(name, new_value)
