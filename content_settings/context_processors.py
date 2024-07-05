"""
the module contains context processors for the django templates.
"""

from .conf import content_settings as _content_settings


def content_settings(request=None):
    """
    context processor for the django templates that provides content_settings object into template as CONTENT_SETTINGS.
    """
    return {"CONTENT_SETTINGS": _content_settings}
