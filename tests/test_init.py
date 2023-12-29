import pytest

from content_settings.conf import content_settings
from content_settings.models import ContentSetting
from content_settings.caching import reset_all_values

pytestmark = [pytest.mark.django_db(transaction=True)]


def test_simple_text():
    assert content_settings.TITLE == "Book Store"


def test_update_simple_text():
    setting = ContentSetting.objects.get(name="TITLE")
    setting.value = "New Title"
    setting.save()

    reset_all_values()

    assert content_settings.TITLE == "New Title"
