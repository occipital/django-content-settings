import pytest
from unittest.mock import patch

from django.test import Client
from django.core.cache import cache

from content_settings.models import ContentSetting
from content_settings.caching import TRIGGER

pytestmark = [pytest.mark.django_db(transaction=True)]


def test_changing_value_updates_cache():

    resp = Client().get("/books/fetch/all/")
    assert resp.status_code == 200
    assert resp.json()["TITLE"] == "Book Store"

    var = ContentSetting.objects.get(name="TITLE")
    var.value = "New Title"
    var.save()

    resp = Client().get("/books/fetch/all/")
    assert resp.status_code == 200
    assert resp.json()["TITLE"] == "New Title"


def test_updating_value_do_not_update_cache():

    resp = Client().get("/books/fetch/all/")
    assert resp.status_code == 200
    assert resp.json()["TITLE"] == "Book Store"

    ContentSetting.objects.filter(name="TITLE").update(value="New Title")

    resp = Client().get("/books/fetch/all/")
    assert resp.status_code == 200
    assert resp.json()["TITLE"] == "Book Store"


def test_removing_cache_does_not_update_value():

    resp = Client().get("/books/fetch/all/")
    assert resp.status_code == 200
    assert resp.json()["TITLE"] == "Book Store"

    ContentSetting.objects.filter(name="TITLE").update(value="New Title")
    cache.delete(TRIGGER.cache_key)

    resp = Client().get("/books/fetch/all/")
    assert resp.status_code == 200
    assert resp.json()["TITLE"] == "Book Store"

    assert cache.get(TRIGGER.cache_key) is None


def test_reupdating_cache_updates_value():

    resp = Client().get("/books/fetch/all/")
    assert resp.status_code == 200
    assert resp.json()["TITLE"] == "Book Store"

    ContentSetting.objects.filter(name="TITLE").update(value="New Title")
    cache.set(TRIGGER.cache_key, "123")

    resp = Client().get("/books/fetch/all/")
    assert resp.status_code == 200
    assert resp.json()["TITLE"] == "New Title"

    assert cache.get(TRIGGER.cache_key) == "123"


def test_py_object_conversion_calls_only_once():
    resp = Client().get("/books/fetch/all/")
    assert resp.status_code == 200

    with patch("tests.books.content_settings.to_py_object") as mock_to_py_object:
        resp = Client().get("/books/fetch/all/")
        assert resp.status_code == 200
        assert mock_to_py_object.call_count == 0


def test_py_object_conversion_calls_only_once_after_update():

    resp = Client().get("/books/fetch/all/")
    assert resp.status_code == 200
    assert resp.json()["TITLE"] == "Book Store"

    ContentSetting.objects.filter(name="BOOKS").update(value="")
    cache.set(TRIGGER.cache_key, "123")

    with patch(
        "tests.books.content_settings.to_py_object", side_effect=lambda v: v
    ) as mock_to_py_object:
        resp = Client().get("/books/fetch/all/")
        assert resp.status_code == 200
        assert mock_to_py_object.call_count == 1

    with patch(
        "tests.books.content_settings.to_py_object", side_effect=lambda v: v
    ) as mock_to_py_object:
        resp = Client().get("/books/fetch/all/")
        assert resp.status_code == 200
        assert mock_to_py_object.call_count == 0


def test_py_object_does_not_get_called_if_different_value_was_set():

    resp = Client().get("/books/fetch/all/")
    assert resp.status_code == 200
    assert resp.json()["TITLE"] == "Book Store"

    ContentSetting.objects.filter(name="TITLE").update(value="New Title")
    cache.set(TRIGGER.cache_key, "123")

    with patch(
        "tests.books.content_settings.to_py_object", side_effect=lambda v: v
    ) as mock_to_py_object:
        resp = Client().get("/books/fetch/all/")
        assert resp.status_code == 200
        assert mock_to_py_object.call_count == 0
