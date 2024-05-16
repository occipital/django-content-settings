import pytest

from content_settings.conf import content_settings, settings
from content_settings.models import ContentSetting
from content_settings.caching import reset_all_values, get_raw_value

pytestmark = [pytest.mark.django_db(transaction=True)]


def test_simple_text():
    assert content_settings.TITLE == "Book Store"


def test_unknown_setting_name():
    with pytest.raises(AttributeError):
        content_settings.UNKNOWN_SETTING


def test_setting_simple_text():
    assert settings.TITLE == "Book Store"


def test_update_simple_text():
    setting = ContentSetting.objects.get(name="TITLE")
    setting.value = "New Title"
    setting.save()

    reset_all_values()

    assert content_settings.TITLE == "New Title"


def test_setting_update_simple_text():
    setting = ContentSetting.objects.get(name="TITLE")
    setting.value = "New Title"
    setting.save()

    reset_all_values()

    assert settings.TITLE == "New Title"


def test_startswith():
    assert content_settings.startswith__IS_ == {"IS_OPEN": True, "IS_CLOSED": False}
    assert content_settings.startswith("IS_") == {"IS_OPEN": True, "IS_CLOSED": False}


def test_setting_startswith():
    assert settings.startswith__IS_ == {"IS_OPEN": True, "IS_CLOSED": False}
    assert settings.startswith("IS_") == {"IS_OPEN": True, "IS_CLOSED": False}


def test_withtag():
    assert content_settings.withtag__GENERAL == {
        "TITLE": "Book Store",
        "DESCRIPTION": "Book Store is the best book store in the world",
    }
    assert content_settings.withtag("general") == {
        "TITLE": "Book Store",
        "DESCRIPTION": "Book Store is the best book store in the world",
    }


def test_setting_withtag():
    assert settings.withtag__GENERAL == {
        "TITLE": "Book Store",
        "DESCRIPTION": "Book Store is the best book store in the world",
    }
    assert settings.withtag("general") == {
        "TITLE": "Book Store",
        "DESCRIPTION": "Book Store is the best book store in the world",
    }


def test_setting_django():
    assert settings.STATIC_URL == "/static/"


def test_get_raw_value():
    assert get_raw_value("TITLE") == "Book Store"
    assert get_raw_value("IS_OPEN") == "1"
