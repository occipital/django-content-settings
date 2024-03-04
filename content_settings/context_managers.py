from contextlib import contextmanager, ContextDecorator
from .settings import CONTEXT, CONTEXT_PROCESSORS

CONTEXT_DEFAULTS_STACK = [CONTEXT]
CONTEXT_DEFAULTS_PROCESSORS_STACK = [CONTEXT_PROCESSORS]


class process:
    """
    the flag _init determines whether the processor should be applied for default values
    of initial (processed after default values)
    """

    init = False

    def __init__(self, **kwargs):
        if "_init" in kwargs:
            self.init = kwargs.pop("_init")
        self.kwargs = kwargs

    def process(self, kwargs):
        raise NotImplementedError()


class process_set(process):
    def process(self, kwargs):
        return {
            name: self.process_one(
                set()
                if kwargs.get(name) is None
                else (
                    set([kwargs[name]])
                    if isinstance(kwargs[name], str)
                    else set(kwargs[name])
                ),
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


class add_tags(set_add):
    def __init__(self, tags):
        super().__init__(tags=tags, _init=True)


class remove_tags(set_remove):
    def __init__(self, tags):
        super().__init__(tags=tags, _init=True)


class process_str(process):
    def process(self, kwargs):
        return {
            name: self.process_one(
                kwargs.get(name, ""),
                "" if value is None else str(value),
            )
            for name, value in self.kwargs.items()
        }


class str_append(process_str):
    def process_one(self, start, change):
        return start + change


class str_prepend(process_str):
    def process_one(self, start, change):
        return change + start


class str_format(process_str):
    def process_one(self, start, change):
        return change.format(start)


class help_format(str_format):
    def __init__(self, text):
        super().__init__(help=text, _init=True)


@contextmanager
def context_defaults(*args, **kwargs):
    CONTEXT_DEFAULTS_STACK.append(kwargs)
    CONTEXT_DEFAULTS_PROCESSORS_STACK.append(args)
    try:
        yield
    finally:
        CONTEXT_DEFAULTS_STACK.pop()
        CONTEXT_DEFAULTS_PROCESSORS_STACK.pop()


def context_defaults_kwargs(kwargs=None):
    init = True
    if kwargs is None:
        kwargs = {}
        init = False

    for processors, new_kwargs in zip(
        CONTEXT_DEFAULTS_PROCESSORS_STACK, CONTEXT_DEFAULTS_STACK
    ):
        for processor in processors:
            if processor.init != init:
                continue
            for name, value in processor.process(kwargs).items():
                kwargs[name] = value

        if not init:
            for name, value in new_kwargs.items():
                kwargs[name] = value

    return kwargs


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
