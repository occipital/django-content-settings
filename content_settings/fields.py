"""
Fields that can be used in `cls_field` attribute of the content settings.

It includes all of the fields from django.forms.fields + several custom fields.
"""

from django.forms.fields import *


StripCharField = CharField


class NoStripCharField(CharField):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.strip = False
