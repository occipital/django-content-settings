from .settings import TAG_CHANGED
from .store import cs_has_app, get_app_name


def changed(name, cs_type, value):
    return set() if value == cs_type.default else set([TAG_CHANGED])


def app_name(name, cs_type, value):
    return set([get_app_name(name)]) if cs_has_app(name) else set()
