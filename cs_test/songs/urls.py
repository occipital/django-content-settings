from django.urls import path
from django.views.generic import TemplateView
from django.http import HttpResponse

from content_settings.conf import content_settings
from content_settings.views import FetchSettingsView, gen_hastag
from content_settings.context_managers import content_settings_context

from .models import Artist


def math(request, multi=content_settings.lazy__DAYS_WITHOUT_FAIL):
    a = int(request.GET.get("a", 1))
    with content_settings_context(DAYS_WITHOUT_FAIL="17"):
        b = int(request.GET.get("b", 1)) * multi
    return HttpResponse(f"{a} + {b} = {a + b}")


urlpatterns = [
    path(
        "",
        TemplateView.as_view(
            template_name="songs/index.html",
            extra_context={"artists": Artist.objects.all()},
        ),
        name="index",
    ),
    path("math/", math, name="math"),
    path("fetch/main/", FetchSettingsView.as_view(names=gen_hastag("main"))),
]
