from django import template
from django.utils.html import escape
from django.utils.safestring import SafeString
from django.utils.safestring import mark_safe

from content_settings.conf import content_settings

register = template.Library()


@register.simple_tag
def content_settings_call(name, *args, **kwargs):
    safe = kwargs.pop("_safe", False)
    var = getattr(content_settings, name)
    result = var(*args, **kwargs)
    return (
        mark_safe(result) if safe or isinstance(result, SafeString) else escape(result)
    )
