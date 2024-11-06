import pytest

from django.test import Client
from django.contrib.auth import get_user_model

from content_settings.models import ContentSetting
from content_settings.context_managers import content_settings_context

from tests import testing_settings_full

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

    resp = client.get("/books/fetch/all/")
    assert resp.status_code == 200
    assert resp.json()["TITLE"] == "Book Store"

    var = ContentSetting.objects.get(name="TITLE")
    var.value = "New Title"
    var.save()

    resp = client.get("/books/fetch/all/")
    assert resp.status_code == 200
    assert resp.json()["TITLE"] == "New Title"


def test_get_simple_text_after_reassign():
    from content_settings.conf import content_settings

    client = get_anonymous_client()

    resp = client.get("/books/fetch/all/")
    assert resp.status_code == 200
    assert resp.json()["TITLE"] == "Book Store"

    content_settings.TITLE = "New Title"

    resp = client.get("/books/fetch/all/")
    assert resp.status_code == 200
    assert resp.json()["TITLE"] == "New Title"


def test_fetch_group_single_value():
    client = get_anonymous_client()
    resp = client.get("/books/fetch/home/")
    assert resp.status_code == 200
    assert resp.json() == {"TITLE": "Book Store"}


def test_fetch_group_multiple_values():
    client = get_anonymous_client()
    resp = client.get("/books/fetch/home-detail/")
    assert resp.status_code == 200
    assert resp.json() == {
        "DESCRIPTION": "Book Store is the best book store in the world",
        "TITLE": "Book Store",
    }

    assert resp.headers["X-Content-Settings-Errors"] == "OPEN_DATE: permission denied"

    client = get_staff_client()
    resp = client.get("/books/fetch/home-detail/")
    assert resp.status_code == 200
    assert resp.json() == {
        "DESCRIPTION": "Book Store is the best book store in the world",
        "OPEN_DATE": "2023-01-01",
        "TITLE": "Book Store",
    }


def test_fetch_group_suffix():
    client = get_anonymous_client()
    resp = client.get("/books/fetch/main/")
    assert resp.status_code == 200
    assert resp.json() == {
        "TITLE": "Book Store",
        "BOOKS__available_names": ["Kateryna", "The Poplar", "The Night of Taras"],
    }


def test_fetch_group_with_keys():
    client = get_anonymous_client()
    resp = client.get("/books/fetch/main-simple/")
    assert resp.status_code == 200
    assert resp.json() == {
        "TITLE": "Book Store",
        "BOOKS": ["Kateryna", "The Poplar", "The Night of Taras"],
    }


@content_settings_context(TITLE="New Book Store")
def test_get_simple_text_updated():
    client = get_anonymous_client()

    resp = client.get("/books/fetch/all/")
    assert resp.status_code == 200
    assert resp.json()["TITLE"] == "New Book Store"


def test_get_simple_text_updated_twice():
    client = get_anonymous_client()
    with content_settings_context(TITLE="New Book Store"):
        resp = client.get("/books/fetch/all/")
        assert resp.status_code == 200
        assert resp.json()["TITLE"] == "New Book Store"

    with content_settings_context(TITLE="SUPER New Book Store"):
        resp = client.get("/books/fetch/all/")
        assert resp.status_code == 200
        assert resp.json()["TITLE"] == "SUPER New Book Store"


@pytest.mark.skipif(not testing_settings_full, reason="Testing only with full settings")
def test_context_user_defined():
    client = get_anonymous_client()
    resp = client.get("/books/fetch/general/")
    assert resp.status_code == 200
    assert "USER_TITLE" not in resp.json()

    with content_settings_context(
        USER_TITLE=("My New Title", "line", set(["general"]))
    ):
        resp = client.get("/books/fetch/general/")
        assert resp.status_code == 200
        assert resp.json()["USER_TITLE"] == "My New Title"

    client = get_anonymous_client()
    resp = client.get("/books/fetch/general/")
    assert resp.status_code == 200
    assert "USER_TITLE" not in resp.json()


def test_fetch_suffix():
    client = get_anonymous_client()
    resp = client.get("/books/fetch/all-extended/")
    assert resp.status_code == 200
    assert resp.json()["BOOKS__available_names"] == [
        "Kateryna",
        "The Poplar",
        "The Night of Taras",
    ]


def test_fetch_tags():
    client = get_anonymous_client()
    resp = client.get("/books/fetch/general/")
    assert resp.json() == {
        "DESCRIPTION": "Book Store is the best book store in the world",
        "TITLE": "Book Store",
    }

    cs = ContentSetting.objects.get(name="DESCRIPTION")
    cs.value = "New Description"
    cs.save()

    resp = client.get("/books/fetch/general/")
    assert resp.json() == {"DESCRIPTION": "New Description", "TITLE": "Book Store"}


def test_fetch_startswith():
    client = get_anonymous_client()
    resp = client.get("/books/fetch/is/")

    # is open should not be match as it is without permissions
    assert resp.json() == {"IS_CLOSED": False}


def test_fetch_startswith_and_title():
    client = get_anonymous_client()
    resp = client.get("/books/fetch/is-and-title/")

    # is open should not be match as it is without permissions
    assert resp.json() == {"IS_CLOSED": False, "TITLE": "Book Store"}
