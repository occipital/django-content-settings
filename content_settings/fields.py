"""
Fields that can be used in `cls_field` attribute of the content settings.

It includes all of the fields from django.forms.fields + several custom fields.
"""

from django.forms.fields import *
from django.forms.fields import CharField as BaseCharField


class StripCharField(CharField):
    """
    CharField that strips the value. (default Django CharField)
    """


class NoStripCharField(CharField):
    """
    CharField that does not strip the value.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.strip = False
