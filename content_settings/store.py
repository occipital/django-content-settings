APP_NAME_STORE = {}  # setting_name: app_name


def add_app_name(cs_name, app_name):
    APP_NAME_STORE[cs_name] = app_name


def cs_has_app(cs_name):
    return cs_name in APP_NAME_STORE


def get_app_name(cs_name):
    return APP_NAME_STORE[cs_name]
