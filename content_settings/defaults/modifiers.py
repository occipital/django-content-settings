"""
    Modifiers are functions that take kwargs and return updates for that dict.

    Modifiers are using in `DEFAULTS` second element of the tuple and as `defaults` arguments.
"""

from typing import Dict, Any, Callable, Set, Iterable

TModifier = Callable[[Dict[str, Any]], Dict[str, Any]]


def set_if_missing(**new_kwargs: Any) -> TModifier:
    """
    Set key-value if it is not already set.
    """
    return lambda kwargs: {k: v for k, v in new_kwargs.items() if k not in kwargs}


class unite(object):
    """
    unite is a base class for modifiers that uses to unite new_kwargs with existing kwargs.
    """

    skip_if_not_set = False

    def __init__(self, **kwargs) -> None:
        self.new_kwargs = kwargs

    def __call__(self, kwargs: Dict[str, Any]) -> Dict[str, Any]:
        result = {}
        for k, v in self.new_kwargs.items():
            if k in kwargs:
                result[k] = self.process(v, kwargs[k])
            elif self.skip_if_not_set:
                continue
            else:
                result[k] = v
        return result

    def process(self, new_value: Any, old_value: Any) -> Any:
        """
        Process new_value and old_value and return new value.
        """
        raise NotImplementedError("Subclass must implement this method")


class unite_set_add(unite):
    """
    modify set by adding new values
    """

    def process(self, new_value: Iterable[Any], old_value: Iterable[Any]) -> Set[Any]:
        return set(new_value) | set(old_value)


class unite_set_remove(unite):
    """
    modify set by removing given values
    """

    skip_if_not_set = True

    def process(self, new_value: Iterable[Any], old_value: Iterable[Any]) -> Set[Any]:
        return set(old_value) - set(new_value)


def add_tags(tags: Iterable[str]) -> TModifier:
    """
    add tags
    """
    return unite_set_add(tags=tags)


def remove_tags(tags: Iterable[str]) -> TModifier:
    """
    remove tags
    """
    return unite_set_remove(tags=tags)


def add_tag(tag: str) -> TModifier:
    """
    add tag
    """
    return unite_set_add(tags={tag})


def remove_tag(tag: str) -> TModifier:
    """
    remove tag
    """
    return unite_set_remove(tags={tag})


class unite_str(unite):
    def __init__(self, _format: str = "{new_value}\n{old_value}", **kwargs) -> None:
        self._format = _format
        super().__init__(**kwargs)

    def process(self, new_value: str, old_value: str) -> str:
        return self._format.format(new_value=new_value, old_value=old_value)


def help_prefix(prefix: str) -> TModifier:
    """
    add prefix to help
    """
    return unite_str("{new_value}<br>{old_value}", help=prefix)


def help_suffix(suffix: str) -> TModifier:
    """
    add suffix to help
    """
    return unite_str("{old_value}<br>{new_value}", help=suffix)
