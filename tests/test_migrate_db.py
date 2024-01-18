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


def test_update_version_value():
    cs = ContentSetting.objects.get(name="TITLE")
    cs.version += "2"
    cs.save()

    assert set_initial_values_for_db() == [("TITLE", "update")]


def test_overwrite_user_defined_allowed():
    ContentSetting.objects.filter(name="TITLE").update(
        user_defined_type="line", value="WOW Store"
    )

    assert set_initial_values_for_db(apply=True) == [("TITLE", "update")]

    cs = ContentSetting.objects.get(name="TITLE")
    assert not cs.user_defined_type
    assert cs.value == "Book Store"


def test_overwrite_user_defined_not_allowed():
    ContentSetting.objects.filter(name="DESCRIPTION").update(
        user_defined_type="line", value="WOW Store"
    )

    with pytest.raises(AssertionError):
        set_initial_values_for_db(apply=True)
