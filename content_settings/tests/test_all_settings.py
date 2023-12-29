import pytest


pytestmark = [
    pytest.mark.django_db,
]

from content_settings.conf import content_settings, ALL
from content_settings.caching import reset_all_values


@pytest.mark.parametrize("name", ALL.keys())
def test_admin_fields(name):
    reset_all_values()
    value = getattr(content_settings, name)
    setting = ALL[name]
    raw_value = setting.default
    assert setting.get_admin_preview_value(raw_value, name)
    assert setting.get_help()


@pytest.mark.parametrize("name", ALL.keys())
def test_validate_default(name):
    reset_all_values()
    setting = ALL[name]
    raw_value = setting.default
    setting.validate_value(raw_value)
