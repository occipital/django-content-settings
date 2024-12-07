import pytest


pytestmark = [
    pytest.mark.django_db,
]

from content_settings.conf import content_settings, ALL
from content_settings.caching import populate, set_populated


@pytest.mark.parametrize(
    "name", [name for name in ALL.keys() if not ALL[name].constant]
)
def test_admin_fields(name):
    set_populated(False)
    value = getattr(content_settings, name)
    setting = ALL[name]
    raw_value = setting.default
    assert setting.get_admin_preview_value(raw_value, name) is not None
    assert setting.get_help() is not None


@pytest.mark.parametrize("name", ALL.keys())
def test_validate_default(name):
    set_populated(False)
    setting = ALL[name]
    raw_value = setting.default
    setting.validate_value(raw_value)
