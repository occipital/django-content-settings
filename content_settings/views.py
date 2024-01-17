from django.http import HttpResponseNotFound, HttpResponseForbidden, JsonResponse
from django.views.generic import View
from content_settings.conf import content_settings

from .conf import ALL, split_attr
from .caching import get_type_by_name


class FetchSettingsView(View):
    attrs = ()

    def get(self, request):
        ret = {}
        for val in self.attrs:
            prefix, name, suffix = split_attr(val)
            assert prefix is None, "prefix is not None"

            cs_type = get_type_by_name(name)
            if cs_type is None:
                continue

            if not cs_type.fetch_permission or not cs_type.fetch_permission(
                request.user
            ):
                continue
            if suffix is None:
                setting_name = name
            else:
                setting_name = f"{name}__{suffix}"
            value = getattr(content_settings, setting_name)
            ret[setting_name] = cs_type.json_view_value(request, value)

        return JsonResponse(ret)


def fetch_one_setting(request, name, suffix=None):
    settings_name = name.upper().replace("-", "_")
    cs_type = get_type_by_name(settings_name)
    if cs_type is None:
        return HttpResponseNotFound("value not found")

    if cs_type.fetch_permission is None:
        return HttpResponseNotFound("hidden")

    if not cs_type.fetch_permission(request.user):
        return HttpResponseForbidden("permission denied")

    if suffix is not None:
        suffix = suffix.lower().replace("-", "_")
        settings_name = f"{settings_name}__{suffix}"

    value = getattr(content_settings, settings_name)

    return JsonResponse({settings_name: cs_type.json_view_value(request, value)})
