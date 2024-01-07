import pytest

from django.test import Client
from django.contrib.auth import get_user_model

from content_settings.models import ContentSetting
from content_settings.context_managers import content_settings_context

pytestmark = [pytest.mark.django_db(transaction=True)]


def get_anonymous_client():
    return Client()


def get_authenticated_client():
    user, created = get_user_model().objects.get_or_create(username="testuser")
    if created:
        user.set_password("testpassword")
        user.save()
    client = Client()
    client.login(username="testuser", password="testpassword")
    return client


def get_staff_client():
    user, created = get_user_model().objects.get_or_create(
        username="teststaff", is_staff=True
    )
    if created:
        user.set_password("testpassword")
        user.save()
    client = Client()
    client.login(username="teststaff", password="testpassword")
    return client


def test_get_simple_text():
    client = get_anonymous_client()
    resp = client.get("/content-settings/fetch/title/")
    assert resp.status_code == 200
    assert resp.json() == {"TITLE": "Book Store"}

    var = ContentSetting.objects.get(name="TITLE")
    var.value = "New Title"
    var.save()

    resp = client.get("/content-settings/fetch/title/")
    assert resp.status_code == 200
    assert resp.json() == {"TITLE": "New Title"}


def test_fetch_group_signle_value():
    client = get_anonymous_client()
    resp = client.get("/content-settings/fetch/home/")
    assert resp.status_code == 200
    assert resp.json() == {"TITLE": "Book Store"}


def test_fetch_group_multiple_values():
    client = get_anonymous_client()
    resp = client.get("/content-settings/fetch/home-detail/")
    assert resp.status_code == 200
    assert resp.json() == {
        "DESCRIPTION": "Book Store is the best book store in the world",
        "TITLE": "Book Store",
    }

    client = get_staff_client()
    resp = client.get("/content-settings/fetch/home-detail/")
    assert resp.status_code == 200
    assert resp.json() == {
        "DESCRIPTION": "Book Store is the best book store in the world",
        "OPEN_DATE": "2023-01-01",
        "TITLE": "Book Store",
    }


@pytest.mark.parametrize(
    "client,name,status_code",
    [
        ["anonymous", "title", 200],
        ["authenticated", "title", 200],
        ["anonymous", "open-date", 403],
        ["authenticated", "open-date", 403],
        ["staff", "open-date", 200],
        ["staff", "OPEN-DATE", 200],
        ["staff", "OPEN_DATE", 200],
        ["anonymous", "home-detail", 200],
        ["authenticated", "home-detail", 200],
        ["staff", "home-detail", 200],
    ],
)
def test_fetch_permissions(client, name, status_code):
    if client == "anonymous":
        client = get_anonymous_client()
    elif client == "authenticated":
        client = get_authenticated_client()
    elif client == "staff":
        client = get_staff_client()
    else:
        raise ValueError("Invalid client type")

    resp = client.get(f"/content-settings/fetch/{name}/")
    assert resp.status_code == status_code


@content_settings_context(TITLE="New Book Store")
def test_get_simple_text_updated():
    client = get_anonymous_client()
    resp = client.get("/content-settings/fetch/title/")
    assert resp.status_code == 200
    assert resp.json() == {"TITLE": "New Book Store"}


def test_get_simple_text_updated_twice():
    client = get_anonymous_client()
    with content_settings_context(TITLE="New Book Store"):
        resp = client.get("/content-settings/fetch/title/")
        assert resp.status_code == 200
        assert resp.json() == {"TITLE": "New Book Store"}

    with content_settings_context(TITLE="SUPER New Book Store"):
        resp = client.get("/content-settings/fetch/title/")
        assert resp.status_code == 200
        assert resp.json() == {"TITLE": "SUPER New Book Store"}
