"""
the caching backend is working with local thread storage to store the checksum raw and py objects.

`DATA` is a local thread storage with the following attributes:

* `ALL_RAW_VALUES: Dict[str, str]` - the raw values (values from the database) of the all settings
* `ALL_VALUES: Dict[str, Any]` - the python objects of the all settings
* `ALL_USER_DEFINES: Dict[str, BaseSetting]` - key is the setting name, value is the user defined type (with tags and help text)
* `POPULATED: bool` - the flag that indicates that all values were populated from the database
"""

from threading import local
from typing import Any, Dict, Set, Optional, List

from django.core.cache import caches
from django.conf import settings

from .utils import import_object
from .types import BaseSetting
from .settings import (
    VALUES_ONLY_FROM_DB,
    VALIDATE_DEFAULT_VALUE,
    CACHE_TRIGGER,
    USER_DEFINED_TYPES,
)


TRIGGER = import_object(CACHE_TRIGGER["backend"])(
    **{k: v for k, v in CACHE_TRIGGER.items() if k != "backend"}
)

DATA = local()


def get_form_checksum():
    return TRIGGER.get_form_checksum()


def set_new_type(
    name: str, user_defined_type: str, tags_set: Set[str], help: str = ""
) -> Optional[BaseSetting]:
    """
    create a new user defined type and saves it to the local thread. The previous type is returned.
    """
    from .conf import USER_DEFINED_TYPES_INSTANCE

    prev_cs_type = cs_type = DATA.ALL_USER_DEFINES.get(name)

    if not cs_type or cs_type.tags != tags_set or cs_type.help != help:
        cs_type = USER_DEFINED_TYPES_INSTANCE[user_defined_type](
            help=help,
            tags=tags_set,
        )

    DATA.ALL_USER_DEFINES[name] = cs_type
    return prev_cs_type


def replace_user_type(name: str, cs_type: BaseSetting) -> Optional[BaseSetting]:
    """
    replace the user defined type with the new one. The previous type is returned.
    """
    prev_cs_type = DATA.ALL_USER_DEFINES.get(name)
    DATA.ALL_USER_DEFINES[name] = cs_type
    return prev_cs_type


def set_new_value(name: str, new_value: str, version: Optional[str] = None) -> str:
    """
    takes name, raw value and saves it to the local thread if the value was changed. The previous value is returned.

    raw value converts to the python object and saves to the local thread.

    if version is not None - it will be verified against the version of the type
    """
    cs_type = get_type_by_name(name)
    if cs_type is None:
        return None

    prev_value = DATA.ALL_RAW_VALUES.get(name)

    if version is None or cs_type.version == version and prev_value != new_value:
        DATA.ALL_RAW_VALUES[name] = new_value
        DATA.ALL_VALUES[name] = cs_type.to_python(new_value)

    return prev_value


def delete_user_value(name: str) -> Optional[str]:
    """
    delete user defined setting from the local thread and returns its raw value
    """
    if name not in DATA.ALL_RAW_VALUES:
        return None

    prev_value = DATA.ALL_RAW_VALUES.get(name)
    del DATA.ALL_RAW_VALUES[name]
    del DATA.ALL_VALUES[name]
    del DATA.ALL_USER_DEFINES[name]

    return prev_value


def get_type_by_name(name: str) -> Optional[BaseSetting]:
    """
    get the type of the setting (inluding user defined types) by its name
    """
    from .conf import ALL

    if name in ALL:
        return ALL[name]

    return get_userdefined_type_by_name(name)


def get_userdefined_type_by_name(name: str) -> Optional[BaseSetting]:
    """
    get the user defined type by its name
    """
    return DATA.ALL_USER_DEFINES.get(name)


def get_value(name: str, suffix: Optional[str] = None) -> Any:
    """
    get the value of the setting by its name and optional suffix
    """
    assert DATA.POPULATED
    cs_type = get_type_by_name(name)
    if cs_type is None:
        raise AttributeError(f"{name} is not defined in any content_settings.py file")

    return cs_type.give(get_py_value(name), suffix)


def get_raw_value(name: str) -> Optional[str]:
    """
    get the raw value of the setting by its name
    """
    assert DATA.POPULATED

    return DATA.ALL_RAW_VALUES.get(name)


def get_py_value(name: str) -> Any:
    """
    get the python object of the setting by its name
    """
    assert DATA.POPULATED

    return DATA.ALL_VALUES[name]


def is_populated() -> bool:
    """
    check if the local thread is populated with the values from the database
    """
    return getattr(DATA, "POPULATED", False)


def get_db_objects() -> Dict[str, Any]:
    """
    get the database objects for the settings
    """
    from .models import ContentSetting

    return {v.name: v for v in ContentSetting.objects.all()}


def get_all_names() -> List[str]:
    """
    get the names of the settings (including user defined types) from the local thread
    """
    if not is_populated():
        return []
    return list(DATA.ALL_VALUES.keys()) + list(DATA.ALL_USER_DEFINES.keys())


def reset_all_values() -> None:
    """
    reset the local thread with the values from the database
    """
    if not is_populated():
        DATA.ALL_VALUES = {}
        DATA.ALL_RAW_VALUES = {}
        DATA.ALL_USER_DEFINES = {}
        DATA.POPULATED = False

    # test DB access
    try:
        from .models import ContentSetting

        ContentSetting.objects.all().first()
    except Exception:
        DATA.POPULATED = False
        return

    reset_values()
    TRIGGER.reset()

    DATA.POPULATED = True

    from .conf import ALL

    for name, cs_type in ALL.items():
        try:
            cs_type.validate(get_py_value(name))
        except Exception as e:
            raise AssertionError(f"Error validating {name}: {e}")


def validate_default_values():
    """
    validate default values for all of the registered settings.

    Only is VALIDATE_DEFAULT_VALUE is True.
    """

    if not VALIDATE_DEFAULT_VALUE:
        return

    from .conf import ALL

    for name, cs_type in ALL.items():
        if not isinstance(cs_type.default, str):
            continue
        try:
            cs_type.validate_value(cs_type.default)
        except Exception as e:
            raise AssertionError(f"Error validating {name}: {e}")


def reset_user_values(db: Optional[Dict[str, Any]] = None) -> None:
    """
    reset the local thread with the values from the database for user defined types

    if trigger_checksum is not the same as the checksum in the local thread, the checksum in the cache backend will be updated
    """
    from .conf import USER_DEFINED_TYPES_INSTANCE

    if db is None:
        db = get_db_objects()

    names = set()
    for name, cs in db.items():
        if not cs.user_defined_type:
            continue

        assert (
            cs.user_defined_type in USER_DEFINED_TYPES_INSTANCE
        ), f"{cs.user_defined_type} is not in USER_DEFINED_TYPES"
        names.add(name)
        set_new_type(
            name,
            cs.user_defined_type,
            cs.tags_set,
            cs.help,
        )
        set_new_value(
            name,
            db[name].value,
            version=(None if settings.DEBUG else db[name].version),
        )

    for name in set(DATA.ALL_USER_DEFINES.keys()) - names:
        delete_user_value(name)


def reset_values(db: Optional[Dict[str, Any]] = None) -> None:
    """
    reset the local thread with the values from the database for code settings

    if trigger_checksum is not the same as the checksum in the local thread, the checksum in the cache backend will be updated
    """
    from .conf import ALL

    if db is None:
        db = get_db_objects()

    # the first run (not raw values)
    is_init = not bool(DATA.ALL_RAW_VALUES)

    for name, cs_type in ALL.items():
        if cs_type.constant:
            set_new_value(name, ALL[name].default)

        elif name in db:
            assert (
                not db[name].user_defined_type or cs_type.overwrite_user_defined
            ), f"{name} is not a code setting and not overwrite_user_defined"

            set_new_value(
                name,
                db[name].value,
                version=(None if settings.DEBUG else db[name].version),
            )

        elif is_init:
            if VALUES_ONLY_FROM_DB:  # todo: only if it is new
                raise AssertionError(f"VALUES_ONLY_FROM_DB: {name} is not in DB")
            set_new_value(name, ALL[name].default, version=ALL[name].version)

    if USER_DEFINED_TYPES:
        reset_user_values(db)


def check_update() -> None:
    """
    check if checksum in the cache backend is the same as the checksum in the local thread

    if not, the values from the database will be loaded
    """
    if not is_populated():
        reset_all_values()
        return

    if TRIGGER.check():
        reset_values()

        TRIGGER.after_update()


def recalc_checksums():
    """
    recalculate the checksums in the cache backend
    """
    TRIGGER.db_changed()
