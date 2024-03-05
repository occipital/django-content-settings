from django import template

from content_settings.models import UserTagSetting

register = template.Library()


@register.simple_tag(takes_context=True)
def content_settings_user_tags(context, *args, **kwargs):
    user = context["request"].user
    return list(UserTagSetting.objects.filter(user=user).values_list("name", "tag"))
