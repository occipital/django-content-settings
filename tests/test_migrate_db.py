import pytest

from content_settings.conf import set_initial_values_for_db
from content_settings.models import ContentSetting

pytestmark = [pytest.mark.django_db(transaction=True)]


def test_init():
    assert set_initial_values_for_db() == []
    assert not ContentSetting.objects.filter(name="AUTHOR").exists()


def test_create_value():
    ContentSetting.objects.filter(name="TITLE").delete()
    assert set_initial_values_for_db() == [("TITLE", "create")]


def test_created_constant():
    ContentSetting.objects.create(name="AUTHOR", value="John Doe")
    assert set_initial_values_for_db() == [("AUTHOR", "delete")]


def test_created_unkown():
    ContentSetting.objects.create(name="UNKWONW", value="John Doe")
    assert set_initial_values_for_db() == [("UNKWONW", "delete")]
