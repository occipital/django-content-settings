# some job urls declared in api/urls.py
from django.urls import path
from .views import fetch_one_setting

app_name = "content_settings"
urlpatterns = [
    path("fetch/<str:name>/", fetch_one_setting, name="fetch_one_setting"),
]
