"""
Widgets that can be used in `widget` attribute of the content settings.

It includes all of the widgets from django.forms.widgets + several custom widgets.
"""

from django.forms.widgets import *


class LongInputMix:
    """
    Mixin that makes input maximum long
    """

    def __init__(self, attrs=None):
        attrs = attrs or {}
        style = attrs.pop("style", "")
        style = "width: calc(100% - 14px);" + style
        attrs["style"] = style
        super().__init__(attrs=attrs)


class LongTextInput(LongInputMix, TextInput):
    """
    Long text input
    """

    pass


class LongTextarea(LongInputMix, Textarea):
    """
    Long textarea
    """

    pass


class LongURLInput(LongInputMix, URLInput):
    """
    Long URL Input
    """


class LongEmailInput(LongInputMix, EmailInput):
    """
    Long Email Input
    """

    pass
