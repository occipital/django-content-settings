import pytest
from unittest.mock import patch

from django.test import Client
from django.core.cache import cache

from content_settings.models import ContentSetting
from content_settings.caching import TRIGGER

pytestmark = [pytest.mark.django_db(transaction=True)]


def test_changing_value_updates_cache():
    """
    post save triggers the cache update
    """
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
    """
    updating value does not update the cache
    """
    resp = Client().get("/books/fetch/all/")
    assert resp.status_code == 200
    assert resp.json()["TITLE"] == "Book Store"

    ContentSetting.objects.filter(name="TITLE").update(value="New Title")

    resp = Client().get("/books/fetch/all/")
    assert resp.status_code == 200
    assert resp.json()["TITLE"] == "Book Store"


def test_removing_cache_does_not_update_value():
    """
    if the cache is not set, the value should not be updated from DB
    """
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
    """
    updateing cache triggers receiving values from DB
    """
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
    """
    if the value was not changed, the py object should not be called with every request
    """
    resp = Client().get("/books/fetch/all/")
    assert resp.status_code == 200

    with patch("tests.books.content_settings.to_py_object") as mock_to_py_object:
        resp = Client().get("/books/fetch/all/")
        assert resp.status_code == 200
        assert mock_to_py_object.call_count == 0


def test_py_object_conversion_calls_only_once_after_update():
    """
    if the value was changed to different value, the py object should not be called
    """
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
    """
    if the value was changed to different value, the py object should not be called
    """

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


def test_fetching_all_values_triggers_db_access_only_once():
    """
    fetching all values triggers the DB access only once
    """

    with patch("content_settings.caching.get_db_objects") as mock_get_db_objects:
        resp = Client().get("/books/fetch/all/")
        assert resp.status_code == 200
        assert mock_get_db_objects.call_count == 1


def test_contants_do_not_fetch_from_db():
    """
    constants do not fetch from DB
    """

    with patch(
        "content_settings.caching.get_db_objects", return_value={}
    ) as mock_get_db_objects:
        resp = Client().get("/books/fetch/constants/")
        assert resp.status_code == 200
        assert resp.json()["AUTHOR"] == "Alexandr Lyabah"
        assert mock_get_db_objects.call_count == 0


"""
TODO:
- access to limited API (not fetch all) - triggers only limited amount of py objects
"""
