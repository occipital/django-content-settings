from django.urls import path
from django.views.generic import TemplateView, ListView

from .models import Book
from content_settings.views import FetchSettingsView


class BookListView(ListView):
    model = Book
    template_name = "books/list.html"


app_name = "books"
urlpatterns = [
    path("", TemplateView.as_view(template_name="books/index.html"), name="index"),
    path("list/", BookListView.as_view(), name="list"),
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
]
