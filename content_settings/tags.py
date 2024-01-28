from .settings import TAG_CHANGED


def changed(cs_type, value):
    return set() if value == cs_type.default else set([TAG_CHANGED])
