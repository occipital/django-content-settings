from django.urls import path
from django.views.generic import TemplateView, ListView

from .models import Book
from content_settings.views import FetchSettingsView, gen_hastag, gen_startswith


class BookListView(ListView):
    model = Book
    template_name = "books/list.html"


app_name = "books"
urlpatterns = [
    path("", TemplateView.as_view(template_name="books/index.html"), name="index"),
    path("list/", BookListView.as_view(), name="list"),
    path(
        "simple-html/",
        TemplateView.as_view(template_name="books/simple.html"),
        name="simple-html",
    ),
    path(
        "fetch/main/",
        FetchSettingsView.as_view(
            attrs=[
                "TITLE",
                "BOOKS__available_names",
            ]
        ),
        name="fetch_main",
    ),
    path(
        "fetch/home-detail/",
        FetchSettingsView.as_view(
            attrs=[
                "DESCRIPTION",
                "OPEN_DATE",
                "TITLE",
            ]
        ),
        name="fetch_home_detail",
    ),
    path(
        "fetch/home/",
        FetchSettingsView.as_view(
            attrs=[
                "TITLE",
            ]
        ),
        name="fetch_home_detail",
    ),
    path(
        "fetch/is/",
        FetchSettingsView.as_view(attrs=gen_startswith("IS_")),
        name="fetch_is",
    ),
    path(
        "fetch/general/",
        FetchSettingsView.as_view(attrs=gen_hastag("general")),
        name="fetch_is",
    ),
    path(
        "fetch/all/",
        FetchSettingsView.as_view(
            attrs=[
                "CUSTOM_TITLE",
                "PREFIX",
                "PREFIX_UPDATED",
                "COMPANY_DESCRIPTION",
                "BOOKS",
                "BOOKS__available_names",
                "TITLE",
            ]
        ),
        name="fetch_all",
    ),
]
