from django.conf import settings

from . import __version__


def get_setting(name, default=None):
    return getattr(settings, "CONTENT_SETTINGS_" + name, default)


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

CACHE_BACKEND = get_setting("CACHE_BACKEND", "default")

CACHE_TIMEOUT = get_setting("CACHE_TIMEOUT", 60 * 60 * 24)

CACHE_SPLITER = get_setting("CACHE_SPLITER", "::")

VALUES_ONLY_FROM_DB = get_setting("VALUES_ONLY_FROM_DB", False) and not settings.DEBUG

DEFAULTS = get_setting("DEFAULTS", [])

USER_DEFINED_TYPES = get_setting("USER_DEFINED_TYPES", [])

ADMIN_CHECKSUM_CHECK_BEFORE_SAVE = get_setting(
    "ADMIN_CHECKSUM_CHECK_BEFORE_SAVE", False
)

CHAIN_VALIDATE = get_setting("CHAIN_VALIDATE", True)

UI_DOC_URL = get_setting(
    "UI_DOC_URL", "https://django-content-settings.readthedocs.io/en/0.18/ui/"
)

assert isinstance(USER_DEFINED_TYPES, list), "USER_DEFINED_TYPES must be a list"
assert len(USER_DEFINED_TYPES) == len(
    set([val[0] for val in USER_DEFINED_TYPES])
), "USER_DEFINED_TYPES must have unique slugs"
for i, val in enumerate(USER_DEFINED_TYPES):
    assert len(val) == 3, f"USER_DEFINED_TYPES[{i}] must be a tuple of 3 elements"
    assert all(
        [isinstance(v, str) for v in val]
    ), f"USER_DEFINED_TYPES[{i}] must be a tuple of 3 strings"

    slug, imp_line, name = val
    assert len(slug) < 50, f"USER_DEFINED_TYPES[{i}][0] must be less than 50 chars"
