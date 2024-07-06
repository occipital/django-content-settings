"""
the functions that can be used for `CONTENT_SETTINGS_TAGS` and generate tags for the content settings based on setting name, type and value.
"""

from .settings import TAG_CHANGED
from .store import cs_has_app, get_app_name
from .types import BaseSetting
from typing import Set


def changed(name: str, cs_type: BaseSetting, value: str) -> Set[str]:
    """
    returns a tag `changed` if the value of the setting is different from the default value.

    the name of the tag can be changed in `CONTENT_SETTINGS_TAG_CHANGED` django setting.
    """
    return set() if value == cs_type.default else set([TAG_CHANGED])


def app_name(name: str, cs_type: BaseSetting, value: str) -> Set[str]:
    """
    returns a tag with the name of the app that uses the setting.
    """
    return set([get_app_name(name)]) if cs_has_app(name) else set()
