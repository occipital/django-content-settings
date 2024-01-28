from django.http import HttpResponseNotFound, HttpResponseForbidden, HttpResponse
from django.views.generic import View
from content_settings.conf import content_settings

from .conf import ALL, split_attr, content_settings
from .caching import get_type_by_name


def gen_startswith(startswith):
    def _(request):
        for name in dir(content_settings):
            if name.startswith(startswith):
                yield name

    return _


def gen_hastag(tag):
    def _(request):
        for name in dir(content_settings):
            if tag in get_type_by_name(name).get_tags():
                yield name

    return _


class FetchSettingsView(View):
    attrs = ()

    def get(self, request):
        ret = []
        for val in self.attrs(request) if callable(self.attrs) else self.attrs:
            prefix, name, suffix = split_attr(val)
            assert prefix is None, "prefix is not None"

            cs_type = get_type_by_name(name)
            if cs_type is None:
                continue

            if not cs_type.can_fetch(request.user):
                continue
            if suffix is None:
                setting_name = name
            else:
                setting_name = f"{name}__{suffix}"
            value = getattr(content_settings, setting_name)
            ret.append(
                (
                    setting_name,
                    cs_type.json_view_value(
                        value, suffix=suffix, request=request, name=name
                    ),
                )
            )

        return HttpResponse(
            "{" + (",".join(f'"{name}":{value}' for name, value in ret)) + "}",
            content_type="application/json",
        )


def fetch_one_setting(request, name, suffix=None):
    settings_name = name.upper().replace("-", "_")
    cs_type = get_type_by_name(settings_name)
    if cs_type is None:
        return HttpResponseNotFound("value not found")

    if not cs_type.can_fetch(request.user):
        return HttpResponseForbidden("permission denied")

    if suffix is not None:
        suffix = suffix.lower().replace("-", "_")
        settings_name = f"{settings_name}__{suffix}"

    value = getattr(content_settings, settings_name)

    return HttpResponse(
        f'{{"{settings_name}":{cs_type.json_view_value(value, suffix=suffix, request=request, name=name)}}}',
        content_type="application/json",
    )
