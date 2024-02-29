from .conf import content_settings as _content_settings, settings as _settings


def content_settings(request=None):
    return {"CONTENT_SETTINGS": _content_settings}


def settings(request=None):
    return {"SETTINGS": _settings}
