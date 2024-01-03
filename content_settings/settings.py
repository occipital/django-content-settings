from django.conf import settings


def get_setting(name, default=None):
    return getattr(settings, "CONTENT_SETTINGS_" + name, default)


try:
    import pkg_resources

    VERSION = pkg_resources.get_distribution("django-content-settings").version
except Exception:
    VERSION = "dev"


CHECKSUM_KEY_PREFIX = (
    get_setting("CHECKSUM_KEY_PREFIX", "CS_CHECKSUM_") + VERSION + "__"
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

VALUES_ONLY_FROM_DB = get_setting("VALUES_ONLY_FROM_DB", False)

CONTEXT = get_setting("CONTEXT", {})

CONTEXT_PROCESSORS = get_setting("CONTEXT_PROCESSORS", [])
