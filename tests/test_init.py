from datetime import date
import pytest

from content_settings.types.basic import ValidationError

from content_settings.conf import content_settings
from content_settings.models import ContentSetting
from content_settings.caching import get_raw_value, set_populated

pytestmark = [pytest.mark.django_db(transaction=True)]


def test_simple_text():
    assert content_settings.TITLE == "Book Store"


def test_unknown_setting_name():
    with pytest.raises(AttributeError):
        content_settings.UNKNOWN_SETTING


def test_setting_simple_text():
    assert content_settings.TITLE == "Book Store"


def test_update_simple_text():
    assert content_settings.TITLE == "Book Store"

    setting = ContentSetting.objects.get(name="TITLE")
    setting.value = "New Title"
    setting.save()

    set_populated(False)

    assert content_settings.TITLE == "New Title"


def test_startswith():
    assert content_settings.startswith__IS_ == {"IS_OPEN": True, "IS_CLOSED": False}


def test_withtag():
    assert content_settings.withtag__GENERAL == {
        "TITLE": "Book Store",
        "DESCRIPTION": "Book Store is the best book store in the world",
    }


def test_get_raw_value():
    assert get_raw_value("TITLE") == "Book Store"
    assert get_raw_value("IS_OPEN") == "1"


def test_assign_value():
    content_settings.TITLE = "New Title"
    assert content_settings.TITLE == "New Title"


def test_assign_value_to_wrong_version():
    from content_settings.models import ContentSetting

    ContentSetting.objects.filter(name="TITLE").update(version="WRONG")
    with pytest.raises(AssertionError):
        content_settings.TITLE = "New Title"


def test_assign_value_creates_new_setting():
    from content_settings.models import ContentSetting

    ContentSetting.objects.filter(name="TITLE").delete()

    content_settings.TITLE = "New Title"

    assert ContentSetting.objects.get(name="TITLE").value == "New Title"
    assert content_settings.TITLE == "New Title"


def test_assert_prefix_error():
    with pytest.raises(AssertionError):
        content_settings.startswith__TITLE = "1"


def test_assign_bool_value():
    content_settings.IS_OPEN = "+"
    assert content_settings.IS_OPEN is True


def test_assign_non_valid_value():
    with pytest.raises(ValidationError):
        content_settings.IS_OPEN = "123"


def test_to_raw_processor():
    content_settings.OPEN_DATE = date(2023, 1, 1)
    assert content_settings.OPEN_DATE == date(2023, 1, 1)

    assert ContentSetting.objects.get(name="OPEN_DATE").value == "2023-01-01"


def test_to_raw_processor_suffixes():
    content_settings.OPEN_DATE__tuple = (2023, 1, 1)
    assert content_settings.OPEN_DATE == date(2023, 1, 1)

    assert ContentSetting.objects.get(name="OPEN_DATE").value == "2023-01-01"
