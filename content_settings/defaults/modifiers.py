"""
    Modifiers are functions that take kwargs and return updates for that dict.

    Modifiers are using in `DEFAULTS` second element of the tuple and as `defaults` arguments.
"""

from typing import Dict, Any, Callable, Set, Iterable

TModifier = Callable[[Dict[str, Any]], Dict[str, Any]]


class NotSet:
    """
    A reference to say that the value is not set. (Using None is not possible)
    """

    pass


class SkipSet(Exception):
    """
    For unite modifiers, to skip setting the value.
    """


def set_if_missing(**params: Any) -> TModifier:
    """
    Set key-value if it is not already set.
    """
    return lambda updates, kwargs: {
        k: v if k not in kwargs else NotSet for k, v in params.items()
    }


class unite(object):
    """
    unite is a base class for modifiers that uses to unite new_kwargs with existing kwargs.
    """

    def __init__(self, **kwargs) -> None:
        self.params = kwargs

    def __call__(
        self, updates: Dict[str, Any], kwargs: Dict[str, Any]
    ) -> Dict[str, Any]:
        result = {}
        for k, v in self.params.items():
            try:
                result[k] = self.process(
                    v, updates.get(k, NotSet), kwargs.get(k, NotSet)
                )
            except SkipSet:
                continue
        return result

    def process(self, value: Any, up: Any, kw: Any) -> Any:
        """
        returns value for the update dict. Where
        * `value` is the value from parameter of modifier
        * `up` is the current value in the update dict
        * `kw` is the current value in the settings kwargs
        """
        raise NotImplementedError("Subclass must implement process method")


class unite_set_add(unite):
    """
    modify set by adding new values
    """

    def process(
        self, value: Iterable[Any], up: Iterable[Any], kw: Iterable[Any]
    ) -> Set[Any]:
        return (
            set(value)
            | (set(up) if up is not NotSet else set())
            | (set(kw) if kw is not NotSet else set())
        )


class unite_set_remove(unite):
    """
    modify set by removing given values
    """

    def process(
        self, value: Iterable[Any], up: Iterable[Any], kw: Iterable[Any]
    ) -> Set[Any]:
        if up is NotSet or not up:
            raise SkipSet()

        return set(up) - set(value) | (set(kw) if kw is not NotSet else set())


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

    def process(self, value: Any, up: Any, kw: Any) -> str:
        if up is not NotSet:
            old_value = up
        elif kw is not NotSet:
            old_value = kw
        else:
            old_value = ""

        return self._format.format(new_value=value, old_value=old_value)


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
