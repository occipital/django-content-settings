"""
the module is used for collecting information.

the `APP_NAME_STORE` a dict `setting_name: app_name` is used to store the name of the app that uses the setting. Which later on can be used in `tags.app_name` to generate a tag with the name of the app.
"""

from typing import Callable, Dict, List

from .types import BaseSetting

APP_NAME_STORE: Dict[str, str] = {}  # setting_name: app_name

ADMIN_HEAD_CSS: List[str] = []
ADMIN_HEAD_JS: List[str] = []
ADMIN_HEAD_CSS_RAW: List[str] = []
ADMIN_HEAD_JS_RAW: List[str] = []

PREFIXSES: Dict[str, Callable] = {}


def add_app_name(cs_name: str, app_name: str) -> None:
    """
    add the name of the app that uses the setting.
    """
    APP_NAME_STORE[cs_name] = app_name


def cs_has_app(cs_name: str) -> bool:
    """
    check if the setting has an app name.
    """
    return cs_name in APP_NAME_STORE


def get_app_name(cs_name: str) -> str:
    """
    get the name of the app that uses the setting.
    """
    return APP_NAME_STORE[cs_name]


def add_admin_head_css(css_url: str) -> None:
    """
    add a css url to the admin head.
    """
    if css_url not in ADMIN_HEAD_CSS:
        ADMIN_HEAD_CSS.append(css_url)


def add_admin_head_js(js_url: str) -> None:
    """
    add a js url to the admin head.
    """
    if js_url not in ADMIN_HEAD_JS:
        ADMIN_HEAD_JS.append(js_url)


def add_admin_head_css_raw(css: str) -> None:
    """
    add a css code to the admin head.
    """
    if css not in ADMIN_HEAD_CSS_RAW:
        ADMIN_HEAD_CSS_RAW.append(css)


def add_admin_head_js_raw(js: str) -> None:
    """
    add a js code to the admin head.
    """
    if js not in ADMIN_HEAD_JS_RAW:
        ADMIN_HEAD_JS_RAW.append(js)


def add_admin_head(setting: BaseSetting) -> None:
    """
    add a setting to the admin head.
    """
    for css in setting.get_admin_head_css():
        add_admin_head_css(css)
    for js in setting.get_admin_head_js():
        add_admin_head_js(js)
    for css in setting.get_admin_head_css_raw():
        add_admin_head_css_raw(css)
    for js in setting.get_admin_head_js_raw():
        add_admin_head_js_raw(js)


def get_admin_head() -> str:
    """
    get the admin head.
    """

    def gen():
        for link in ADMIN_HEAD_CSS:
            yield f"<link rel='stylesheet' href='{link}' />"
        for link in ADMIN_HEAD_JS:
            yield f"<script src='{link}'></script>"
        for code in ADMIN_HEAD_CSS_RAW:
            yield f"<style>{code}</style>"

    return "".join(gen())


def get_admin_raw_js() -> str:
    """
    get the admin raw js.
    """

    def gen():
        for code in ADMIN_HEAD_JS_RAW:
            yield f"(function($){{{code}}})(django.jQuery);"

    return "".join(gen())


def register_prefix(name: str) -> Callable:
    """
    decorator for registration a new prefix
    """

    def _cover(func: Callable) -> Callable:
        assert name not in PREFIXSES
        PREFIXSES[name] = func
        return func

    return _cover
