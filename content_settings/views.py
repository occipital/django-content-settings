"""
Those are the views can be used in the Integration with the Project.
"""

from django.http import HttpResponseNotFound, HttpResponseForbidden, HttpResponse
from django.views.generic import View
from django.utils.translation import gettext as _
from content_settings.conf import content_settings

from .conf import ALL, split_attr, content_settings
from .caching import get_type_by_name


def gen_startswith(startswith: str):
    """
    for names attribute of FetchSettingsView, to find settings by name starts with `startswith`
    """

    def _(request):
        for name in dir(content_settings):
            if name.startswith(startswith):
                yield name

    return _


def gen_hastag(tag: str):
    """
    for names attribute of FetchSettingsView, to find settings by tag
    """

    def _(request):
        for name in dir(content_settings):
            if tag in get_type_by_name(name).get_tags():
                yield name

    return _


def gen_all():
    """
    for names attribute of FetchSettingsView, to find all settings
    """

    def _(request):
        for name in dir(content_settings):
            yield name

    return _


class FetchSettingsView(View):
    """
    A View for featching settings from the content settings.

    Use attribute `names` to define the names of the settings to fetch.

    ```
    FetchSettingsView.as_view(
        names=[
            "DESCRIPTION",
            "OPEN_DATE",
            "TITLE",
        ]
    )
    ```

    Suffix can be used in names

    ```
    FetchSettingsView.as_view(
        names=[
            "TITLE",
            "BOOKS__available_names",
        ]
    ),
    ```

    function for getting names by specific conditions can be used

    ```
    FetchSettingsView.as_view(names=gen_hastag("general")),
    ```

    or combinations of them

    ```
    FetchSettingsView.as_view(names=(gen_startswith("IS_"), "TITLE")),
    ```

    """

    names = ()
    show_error_headers = True

    def get_names(self, request):
        if callable(self.names):
            yield from self.names(request)
        else:
            for value in self.names:
                if callable(value):
                    yield from value(request)
                else:
                    yield value

    def get(self, request):
        ret = []
        errors = []
        for val in self.get_names(request):
            if isinstance(val, tuple):
                key, val = val
            else:
                key = val

            prefix, name, suffix = split_attr(val)
            assert prefix is None, "prefix is not None"

            cs_type = get_type_by_name(name)
            if cs_type is None:
                errors.append(f"{key}: not found")
                continue

            if not cs_type.can_fetch(request.user):
                errors.append(f"{key}: permission denied")
                continue

            value = getattr(content_settings, val)
            ret.append(
                (
                    key,
                    cs_type.json_view_value(
                        value, suffix=suffix, request=request, name=name
                    ),
                )
            )

        return HttpResponse(
            "{" + (",".join(f'"{name}":{value}' for name, value in ret)) + "}",
            content_type="application/json",
            headers=(
                {"X-Content-Settings-Errors": ";".join(errors)}
                if errors and self.show_error_headers
                else {}
            ),
        )


class FetchAllSettingsView(FetchSettingsView):
    names = staticmethod(gen_all())
