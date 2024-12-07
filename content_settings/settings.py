# update docs/settings.md

from django.conf import settings

from . import __version__


def get_setting(name, default=None):
    return getattr(settings, "CONTENT_SETTINGS_" + name, default)


PRECACHED_PY_VALUES = get_setting("PRECACHED_PY_VALUES", False)

PREVIEW_ON_SITE_HREF = get_setting("PREVIEW_ON_SITE_HREF", "/")

PREVIEW_ON_SITE_SHOW = get_setting("PREVIEW_ON_SITE_SHOW", True)

UPDATE_DB_VALUES_BY_MIGRATE = get_setting("UPDATE_DB_VALUES_BY_MIGRATE", True)

TAGS = get_setting(
    "TAGS",
    [],
)

TAG_CHANGED = get_setting("TAG_CHANGED", "changed")

CHECKSUM_KEY_PREFIX = (
    get_setting("CHECKSUM_KEY_PREFIX", "CS_CHECKSUM_") + __version__ + "__"
)

CHECKSUM_USER_KEY_PREFIX = (
    get_setting("CHECKSUM_KEY_PREFIX", "CS_USER_CHECKSUM_") + __version__ + "__"
)

USER_TAGS = get_setting(
    "USER_TAGS",
    {
        "favorites": ("⭐", "⚝"),
        "marked": ("💚", "♡"),
    },
)

CACHE_TRIGGER = get_setting(
    "CACHE_TRIGGER", "content_settings.cache_triggers.VersionChecksum"
)
if isinstance(CACHE_TRIGGER, str):
    CACHE_TRIGGER = {
        "backend": CACHE_TRIGGER,
    }
elif isinstance(CACHE_TRIGGER, dict) and "backend" not in CACHE_TRIGGER:
    CACHE_TRIGGER = {
        "backend": "content_settings.cache_triggers.VersionChecksum",
        **CACHE_TRIGGER,
    }

VALUES_ONLY_FROM_DB = get_setting("VALUES_ONLY_FROM_DB", False) and not settings.DEBUG

VALIDATE_DEFAULT_VALUE = get_setting("VALIDATE_DEFAULT_VALUE", settings.DEBUG)

DEFAULTS = get_setting("DEFAULTS", [])

ADMIN_CHECKSUM_CHECK_BEFORE_SAVE = get_setting(
    "ADMIN_CHECKSUM_CHECK_BEFORE_SAVE", False
)

CHAIN_VALIDATE = get_setting("CHAIN_VALIDATE", True)

UI_DOC_URL = get_setting(
    "UI_DOC_URL", "https://django-content-settings.readthedocs.io/en/0.25/ui/"
)

CHECK_UPDATE_CELERY = get_setting("CHECK_UPDATE_CELERY", True)

CHECK_UPDATE_HUEY = get_setting("CHECK_UPDATE_HUEY", True)

USER_DEFINED_TYPES = get_setting("USER_DEFINED_TYPES", [])

assert isinstance(
    USER_DEFINED_TYPES, list
), "CONTENT_SETTINGS_USER_DEFINED_TYPES must be a list"
assert len(USER_DEFINED_TYPES) == len(
    set([val[0] for val in USER_DEFINED_TYPES])
), "CONTENT_SETTINGS_USER_DEFINED_TYPES must have unique slugs"
for i, val in enumerate(USER_DEFINED_TYPES):
    assert (
        len(val) == 3
    ), f"CONTENT_SETTINGS_USER_DEFINED_TYPES[{i}] must be a tuple of 3 elements"
    assert all(
        [isinstance(v, str) for v in val]
    ), f"CONTENT_SETTINGS_USER_DEFINED_TYPES[{i}] must be a tuple of 3 strings"

    slug, imp_line, name = val
    assert (
        len(slug) < 50
    ), f"CONTENT_SETTINGS_USER_DEFINED_TYPES[{i}][0] must be less than 50 chars"
