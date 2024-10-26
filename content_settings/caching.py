"""
the caching backend is working with local thread storage to store the checksum raw and py objects.

**Start App Workflow**

* The start of content setting use is call `reset_all_values` that is triggered by `receivers.db_connection_done` (triggered by `connection_created` signal)
* `get_cache_key` is a checksum of the current app. It holds a checksum of the current content settings configuration. It is calculated once and never changes. The calculated checksum is used as a key for cached backend. In that key the system stores checksum of the current raw values of the content settings.
* *side note: the system monitors updates values of the checksum only in the app checksum key, which means only changes that made by the same content settings configuration will trigger the update.*
* 

*django caching backend is used to store the checksum and validates if the checksum was changed.*

`DATA` is a local thread storage with the following attributes:

* `ALL_VALUES_CHECKSUM: str` - the checksum of the all values
* `ALL_VALUES_USER_CHECKSUM: str` - the checksum of the user defined values
* `ALL_RAW_VALUES: Dict[str, str]` - the raw values (values from the database) of the all settings
* `ALL_VALUES: Dict[str, Any]` - the python objects of the all settings
* `ALL_USER_DEFINES: Dict[str, BaseSetting]` - key is the setting name, value is the user defined type (with tags and help text)
* `POPULATED: bool` - the flag that indicates that all values were populated from the database
"""

from threading import local
import hashlib
from functools import lru_cache
from typing import Any, Dict, Set, Optional, List

from django.core.cache import caches
from django.conf import settings

from .types import BaseSetting
from .settings import (
    CHECKSUM_KEY_PREFIX,
    CHECKSUM_USER_KEY_PREFIX,
    CACHE_SPLITER,
    CACHE_TIMEOUT,
    CACHE_BACKEND,
    VALUES_ONLY_FROM_DB,
    USER_DEFINED_TYPES,
    VALIDATE_DEFAULT_VALUE,
)


DATA = local()


def get_cache() -> Any:
    """
    returns caching backend that used for caching checksum values
    """
    return caches[CACHE_BACKEND]


@lru_cache(maxsize=None)
def get_cache_key() -> str:
    """
    returns cache key for checksum values (one should not be changed over time)
    """
    from .conf import ALL

    return calc_checksum({name: ALL[name].version for name in ALL.keys()})


@lru_cache(maxsize=None)
def get_user_cache_key() -> Optional[str]:
    """
    returns cache key for user defined types (one should not be changed over time) if user defined types are not used, returns None
    """
    if not USER_DEFINED_TYPES:
        return None

    from .conf import USER_DEFINED_TYPES_INITIAL

    return calc_checksum({k: v.version for k, v in USER_DEFINED_TYPES_INITIAL.items()})


def calc_checksum(values: Dict[str, Any]) -> str:
    """
    generate md5 hash for a dict with keys and values as strings
    """
    return hash_value(
        CACHE_SPLITER.join(
            f"{name}{CACHE_SPLITER}{values[name]}" for name in sorted(values.keys())
        )
    )


def hash_value(value: str) -> str:
    """
    generate md5 hash for a string
    """
    return hashlib.md5(value.encode("utf-8")).hexdigest()


def set_local_checksum() -> None:
    """
    calculate and set checksum in the local thread
    """
    from .conf import ALL

    DATA.ALL_VALUES_CHECKSUM = calc_checksum(
        {k: v for k, v in DATA.ALL_RAW_VALUES.items() if k in ALL}
    )


def set_local_user_checksum() -> None:
    """
    calculate and set checksum in the local thread for user defined types
    """
    from .conf import ALL

    DATA.ALL_VALUES_USER_CHECKSUM = calc_checksum(
        {k: v for k, v in DATA.ALL_RAW_VALUES.items() if k not in ALL}
    )


def push_user_checksum(value=None, key=None) -> None:
    """
    save to cache backend the checksum for user defined types
    """
    if key is None:
        key = get_user_cache_key()

    if value is None:
        value = DATA.ALL_VALUES_USER_CHECKSUM

    get_cache().set(CHECKSUM_USER_KEY_PREFIX + key, value, CACHE_TIMEOUT)


def push_checksum(value=None, key=None) -> None:
    """
    save to cache backend the checksum
    """
    if key is None:
        key = get_cache_key()

    if value is None:
        value = DATA.ALL_VALUES_CHECKSUM

    get_cache().set(CHECKSUM_KEY_PREFIX + key, value, CACHE_TIMEOUT)


def get_checksum_from_store() -> Optional[str]:
    """
    get the checksum from the cache backend
    """
    return get_cache().get(CHECKSUM_KEY_PREFIX + get_cache_key())


def get_user_checksum_from_store() -> Optional[str]:
    """
    get the checksum from the cache backend for user defined types
    """
    return get_cache().get(CHECKSUM_USER_KEY_PREFIX + get_user_cache_key())


def get_checksum_from_local() -> str:
    """
    get the checksum from the local thread
    """
    return DATA.ALL_VALUES_CHECKSUM


def get_checksum_from_user_local() -> Optional[str]:
    """
    get the checksum from the local thread for user defined types
    """
    return DATA.ALL_VALUES_USER_CHECKSUM


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
        DATA.ALL_VALUES: Dict[str, Any] = {}
        DATA.ALL_RAW_VALUES: Dict[str, str] = {}
        DATA.ALL_VALUES_CHECKSUM: str = ""
        DATA.ALL_VALUES_USER_CHECKSUM: str = ""
        DATA.ALL_USER_DEFINES: Dict[str, BaseSetting] = {}
        DATA.POPULATED: bool = False

    try:
        db = get_db_objects()
    except Exception:
        DATA.POPULATED = False
        return
    if USER_DEFINED_TYPES:
        reset_user_values(db)
    reset_code_values(db)

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


def reset_user_values(
    db: Dict[str, Any] = None, trigger_checksum: Optional[str] = None
) -> None:
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

    set_local_user_checksum()

    if trigger_checksum != get_checksum_from_user_local():
        push_user_checksum()


def reset_code_values(
    db: Dict[str, Any] = None, trigger_checksum: Optional[str] = None
) -> None:
    """
    reset the local thread with the values from the database for code settings

    if trigger_checksum is not the same as the checksum in the local thread, the checksum in the cache backend will be updated
    """
    from .conf import ALL

    if db is None:
        db = get_db_objects()

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

        else:
            if VALUES_ONLY_FROM_DB:
                raise AssertionError(f"VALUES_ONLY_FROM_DB: {name} is not in DB")
            set_new_value(name, ALL[name].default, version=ALL[name].version)

    set_local_checksum()

    if trigger_checksum != get_checksum_from_local():
        push_checksum()


def check_update() -> None:
    """
    check if checksum in the cache backend is the same as the checksum in the local thread

    if not, the values from the database will be loaded
    """
    if not is_populated():
        reset_all_values()
        return
    store_checksum = get_checksum_from_store()
    if store_checksum is not None and store_checksum != get_checksum_from_local():
        reset_code_values(trigger_checksum=store_checksum)

    if USER_DEFINED_TYPES:
        store_user_checksum = get_user_checksum_from_store()
        if (
            store_user_checksum is not None
            and store_user_checksum != get_checksum_from_user_local()
        ):
            reset_user_values(trigger_checksum=store_user_checksum)


def recalc_checksums():
    """
    recalculate the checksums in the cache backend
    """
    db = get_db_objects()
    recalc_code_checksums(db)
    if USER_DEFINED_TYPES:
        recalc_user_checksums(db)


def recalc_user_checksums(db):
    """
    recalculate the checksums in the cache backend for user defined types and saves them to the cache backend
    """
    from .conf import USER_DEFINED_TYPES_INITIAL

    values = {}
    for name, cs in db.items():
        if not cs.user_defined_type:
            continue
        if cs.user_defined_type not in USER_DEFINED_TYPES_INITIAL:
            break
        if cs.version == USER_DEFINED_TYPES_INITIAL[cs.user_defined_type].version:
            values[name] = cs.user_defined_type + CACHE_SPLITER + db[name].value
        elif name in DATA.ALL_RAW_VALUES:
            values[name] = (
                cs.user_defined_type + CACHE_SPLITER + DATA.ALL_RAW_VALUES[name]
            )
        else:
            break
    else:
        push_user_checksum(calc_checksum(values))


def recalc_code_checksums(db: Dict[str, Any]) -> None:
    """
    recalculate the checksums in the cache backend for code settings and saves them to the cache backend

    it staves it two keys - one in the cache backend with the local checksum and one with the db checksum
    """
    from .conf import ALL

    push_checksum(
        calc_checksum({k: v.value for k, v in db.items()}),
        calc_checksum({k: v.version for k, v in db.items()}),
    )

    db_versions = {}
    db_values = {}

    for name in set(ALL.keys()) | set(db.keys()):
        if name not in ALL or ALL[name].constant:
            continue

        if name in db:
            db_versions[name] = db[name].version
            db_values[name] = db[name].value
        else:
            db_versions[name] = ALL[name].version
            db_values[name] = ALL[name].default

    db_version_key = calc_checksum(db_versions)
    push_checksum(calc_checksum(db_values), db_version_key)

    if db_version_key == get_cache_key() or not is_populated():
        return

    local_values = {}
    for name in ALL.keys():
        if name in db:
            db_version = db[name].version
            if db_version != ALL[name].version:
                local_values[name] = DATA.ALL_RAW_VALUES[name]
            else:
                local_values[name] = db[name].value
        else:
            local_values[name] = ALL[name].default

    push_checksum(calc_checksum(local_values))
