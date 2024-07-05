"""
the module is used for collecting information.

the `APP_NAME_STORE` a dict `setting_name: app_name` is used to store the name of the app that uses the setting. Which later on can be used in `tags.app_name` to generate a tag with the name of the app.
"""

APP_NAME_STORE = {}  # setting_name: app_name


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
