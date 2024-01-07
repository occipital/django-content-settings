from django.http import HttpResponseNotFound, HttpResponseForbidden, JsonResponse
from django.views.generic import View
from content_settings.conf import content_settings

from .conf import ALL, split_attr


class FetchSettingsView(View):
    attrs = ()

    def get(self, request):
        ret = {}
        for val in self.attrs:
            prefix, name, suffix = split_attr(val)
            assert prefix is None, "prefix is not None"

            setting = ALL[name]
            if not setting.fetch_permission or not setting.fetch_permission(
                request.user
            ):
                continue
            if suffix is None:
                setting_name = name
            else:
                setting_name = f"{name}__{suffix}"
            value = getattr(content_settings, setting_name)
            ret[setting_name] = setting.json_view_value(request, value)

        return JsonResponse(ret)


def fetch_one_setting(request, name, suffix=None):
    settings_name = name.upper().replace("-", "_")

    try:
        setting = ALL[settings_name]
    except KeyError:
        return HttpResponseNotFound("wrong name")

    if setting.fetch_permission is None:
        return HttpResponseNotFound("hidden")

    if not setting.fetch_permission(request.user):
        return HttpResponseForbidden("permission denied")

    if suffix is not None:
        suffix = suffix.lower().replace("-", "_")
        settings_name = f"{settings_name}__{suffix}"

    value = getattr(content_settings, settings_name)

    return JsonResponse({settings_name: setting.json_view_value(request, value)})
