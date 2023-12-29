from django.http import HttpResponseNotFound, HttpResponseForbidden, JsonResponse
from content_settings.conf import content_settings

from .conf import ALL, FETCH_GROUPS


def fetch_one_group(request, group_name):
    ret = {}

    for name in FETCH_GROUPS[group_name]:
        setting = ALL[name]
        if not setting.fetch_permission or not setting.fetch_permission(request.user):
            continue
        value = getattr(content_settings, name)
        ret[name] = setting.json_view_value(request, value)

    return JsonResponse(ret)


def fetch_one_setting(request, name):
    settings_name = name.upper().replace("-", "_")
    if settings_name in FETCH_GROUPS:
        return fetch_one_group(request, settings_name)

    try:
        setting = ALL[settings_name]
    except KeyError:
        return HttpResponseNotFound("wrong name")

    if setting.fetch_permission is None:
        return HttpResponseNotFound("hidden")

    if not setting.fetch_permission(request.user):
        return HttpResponseForbidden("permission denied")

    value = getattr(content_settings, settings_name)

    return JsonResponse({settings_name: setting.json_view_value(request, value)})
