"""
    Modifiers are functions that take kwargs and return updates for that dict.

    Modifiers are using in `DEFAULTS` second element of the tuple and as `defaults` arguments.
"""

from typing import Dict, Any, Callable, Set, Iterable, Tuple

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
    Set key-value pairs in the updates dictionary if they are not already set in kwargs. This modifier is used for all `**kwargs` attributes for `defaults` context.

    Args:
        **params: Arbitrary keyword arguments representing key-value pairs to set.
    """
    return lambda updates, kwargs: {
        k: v if k not in kwargs else NotSet for k, v in params.items()
    }


class unite(object):
    """
    unite is a base class for modifiers that unites kwargs passed in arguments with kwargs already collected and kwargs passed in the definition of the settings type.

    All child classes should implement `process` method.

    Args:
        **kwargs: Arbitrary keyword arguments representing key-value pairs to unite.
    """

    def __init__(self, **kwargs) -> None:
        self.params = kwargs

    def __call__(
        self, updates: Dict[str, Any], kwargs: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Unites the provided updates and kwargs dictionaries with the parameters.

        Args:
            updates: The dictionary with already collected kwargs from default context.
            kwargs: The kwargs passed in the definition of the settings type.

        Returns:
            A dictionary with united key-value pairs.
        """
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
        Returns value for the update dictionary.

        Args:
            value: The value from the parameter of the modifier.
            up: The current value in the update dictionary.
            kw: The current value in the settings kwargs.

        Returns:
            The processed value to be set in the update dictionary.
        """
        raise NotImplementedError("Subclass must implement process method")


class unite_empty_not_set(unite):
    """
    unite, that is used for removing elements from the object. For example - making a smaller set or removing text from a string.

    It adds an additional parameter `_empty_not_set: bool = True` that answers the question - should we remove value from updates if it is empty.

    Args:
        _empty_not_set: A boolean indicating whether to remove empty values from updates.
        **kwargs: Arbitrary keyword arguments representing key-value pairs to unite.
    """

    empty_not_set: bool = True

    def __init__(self, _empty_not_set: bool = True, **kwargs) -> None:
        self.empty_not_set = _empty_not_set
        super().__init__(**kwargs)

    def __call__(self, *args, **kwargs) -> Dict[str, Any]:
        """
        Unites the provided updates and kwargs dictionaries with the parameters, removing empty values if specified.

        Args:
            *args: Positional arguments.
            **kwargs: Keyword arguments.

        Returns:
            A dictionary with united key-value pairs, with empty values removed if specified.
        """
        ret = super().__call__(*args, **kwargs)
        if not self.empty_not_set:
            return ret
        return {k: v if v else NotSet for k, v in ret.items()}


class unite_set_add(unite):
    """
    unite that modifies a set by adding new values in it.
    """

    def process(
        self, value: Iterable[Any], up: Iterable[Any], kw: Iterable[Any]
    ) -> Set[Any]:
        return (
            set(value)
            | (set(up) if up is not NotSet else set())
            | (set(kw) if kw is not NotSet else set())
        )


class unite_set_remove(unite_empty_not_set):
    """
    unite that modifies a set by removing given values.

    """

    def process(
        self, value: Iterable[Any], up: Iterable[Any], kw: Iterable[Any]
    ) -> Set[Any]:
        if up is NotSet or not up:
            raise SkipSet()

        return set(up) - set(value) | (set(kw) if kw is not NotSet else set())


class unite_tuple_add(unite):
    """
    unite that modifies a tuple by adding new values in it.
    """

    def process(
        self, value: Iterable[Any], up: Iterable[Any], kw: Iterable[Any]
    ) -> Tuple[Any]:
        if up is not NotSet:
            old_value = up
        elif kw is not NotSet:
            old_value = kw
        else:
            old_value = ()
        return tuple(value) + tuple(old_value)


class unite_dict_update(unite):
    """
    unite that modifies a dictionary by updating it with new values.
    """

    def process(
        self, value: Dict[str, Any], up: Dict[str, Any], kw: Dict[str, Any]
    ) -> Dict[str, Any]:
        return {
            **(up if up is not NotSet else {}),
            **value,
            **(kw if kw is not NotSet else {}),
        }


def add_tags(tags: Iterable[str], **kwargs) -> TModifier:
    """
    add tags to the setting
    """
    return unite_set_add(tags=tags, **kwargs)


def remove_tags(tags: Iterable[str], **kwargs) -> TModifier:
    """
    Removes tags from the update context.
    """
    return unite_set_remove(tags=tags, **kwargs)


def add_tag(tag: str, **kwargs) -> TModifier:
    """
    same as `add_tags` but only one.
    """
    return unite_set_add(tags={tag}, **kwargs)


def remove_tag(tag: str, **kwargs) -> TModifier:
    """
    same as `remove_tags` but only one.
    """
    return unite_set_remove(tags={tag}, **kwargs)


class unite_str(unite):
    """
    unite that modifies a string by formatting it.

    Args:
        _format: A string to format the value use `{new_value}` as a placeholder for the passed value in kwargs and `{old_value}` as a placeholder for the value in the update context.
        **kwargs: Arbitrary keyword arguments.
    """

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


def add_admin_head(
    css: Iterable[str] = (),
    js: Iterable[str] = (),
    css_raw: Iterable[str] = (),
    js_raw: Iterable[str] = (),
) -> TModifier:
    """
    add css and js to the admin head

    * css -> admin_head_css
    * js -> admin_head_js
    * css_raw -> admin_head_css_raw
    * js_raw -> admin_head_js_raw
    """
    return unite_tuple_add(
        **({"admin_head_css": css} if css else {}),
        **({"admin_head_js": js} if js else {}),
        **({"admin_head_css_raw": css_raw} if css_raw else {}),
        **({"admin_head_js_raw": js_raw} if js_raw else {}),
    )


class add_widget_class(unite_dict_update):
    """
    add widget class or classes splited by space.
    """

    def __init__(self, class_name: str):
        super().__init__(widget_attrs={"class": class_name})

    def process(
        self, value: Dict[str, Any], up: Dict[str, Any], kw: Dict[str, Any]
    ) -> Dict[str, Any]:
        ret = super().process(value, up, kw)
        if up is NotSet and kw is NotSet:
            return ret

        ret["class"] = " ".join(
            set(value["class"].split())
            | (
                set(up["class"].split())
                if up is not NotSet and "class" in up
                else set()
            )
            | (
                set(kw["class"].split())
                if kw is not NotSet and "class" in kw
                else set()
            )
        )
        return ret


def update_widget_attrs(**kwargs) -> TModifier:
    """
    update widget attrs
    """
    return unite_dict_update(widget_attrs=kwargs)
