from django import template
from content_settings.conf import content_settings
from django.utils.html import escape

register = template.Library()


@register.simple_tag
def content_settings_call(name, *args, **kwargs):
    safe = kwargs.pop("_safe", False)
    result = getattr(content_settings, name)(*args, **kwargs)
    return result if safe else escape(result)
