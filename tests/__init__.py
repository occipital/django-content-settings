import os

yaml_installed = False
try:
    import yaml

    yaml_installed = True
except ImportError:
    pass

testing_settings = os.environ.get("TESTING_SETTINGS", "normal")
testing_settings_normal = testing_settings == "normal"
testing_settings_full = testing_settings == "full"
testing_settings_min = testing_settings == "min"

testing_disable_precached_py_values = os.environ.get(
    "TESTING_DISABLE_PRECACHED_PY_VALUES", False
)
