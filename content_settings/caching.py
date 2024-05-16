from threading import local
import hashlib
from functools import lru_cache

from django.core.cache import caches
from django.conf import settings

from .settings import (
    CHECKSUM_KEY_PREFIX,
    CHECKSUM_USER_KEY_PREFIX,
    CACHE_SPLITER,
    CACHE_TIMEOUT,
    CACHE_BACKEND,
    VALUES_ONLY_FROM_DB,
    USER_DEFINED_TYPES,
)


DATA = local()


def get_cache():
    return caches[CACHE_BACKEND]


@lru_cache(maxsize=None)
def get_cache_key():
    from .conf import ALL

    return calc_checksum({name: ALL[name].version for name in ALL.keys()})


@lru_cache(maxsize=None)
def get_user_cache_key():
    if not USER_DEFINED_TYPES:
        return None

    from .conf import USER_DEFINED_TYPES_INITIAL

    return calc_checksum({k: v.version for k, v in USER_DEFINED_TYPES_INITIAL.items()})


def calc_checksum(values):
    """
    generate md5 hash for a dict with keys and values as strings
    """
    return hash_value(
        CACHE_SPLITER.join(
            f"{name}{CACHE_SPLITER}{values[name]}" for name in sorted(values.keys())
        )
    )


def hash_value(value):
    """
    generate md5 hash for a string
    """
    return hashlib.md5(value.encode("utf-8")).hexdigest()


def set_local_checksum():
    from .conf import ALL

    DATA.ALL_VALUES_CHECKSUM = calc_checksum(
        {k: v for k, v in DATA.ALL_RAW_VALUES.items() if k in ALL}
    )


def set_local_user_checksum():
    from .conf import ALL

    DATA.ALL_VALUES_USER_CHECKSUM = calc_checksum(
        {k: v for k, v in DATA.ALL_RAW_VALUES.items() if k not in ALL}
    )


def push_user_checksum(value=None, key=None):
    if key is None:
        key = get_user_cache_key()

    if value is None:
        value = DATA.ALL_VALUES_USER_CHECKSUM

    get_cache().set(CHECKSUM_USER_KEY_PREFIX + key, value, CACHE_TIMEOUT)


def push_checksum(value=None, key=None):
    if key is None:
        key = get_cache_key()

    if value is None:
        value = DATA.ALL_VALUES_CHECKSUM

    get_cache().set(CHECKSUM_KEY_PREFIX + key, value, CACHE_TIMEOUT)


def get_checksum_from_store():
    return get_cache().get(CHECKSUM_KEY_PREFIX + get_cache_key())


def get_user_checksum_from_store():
    return get_cache().get(CHECKSUM_USER_KEY_PREFIX + get_user_cache_key())


def get_checksum_from_local():
    return DATA.ALL_VALUES_CHECKSUM


def get_checksum_from_user_local():
    return DATA.ALL_VALUES_USER_CHECKSUM


def set_new_type(name, cs):
    from .conf import USER_DEFINED_TYPES_INSTANCE

    cs_type = DATA.ALL_USER_DEFINES.get(name)

    if not cs_type or cs_type.tags != cs.tags_set or cs_type.help != cs.help:
        cs_type = USER_DEFINED_TYPES_INSTANCE[cs.user_defined_type](
            help=cs.help,
            tags=cs.tags_set,
        )

    DATA.ALL_USER_DEFINES[name] = cs_type


def set_new_value(name, new_value, version=None):
    cs_type = get_type_by_name(name)
    if cs_type is None:
        return None

    prev_value = DATA.ALL_RAW_VALUES.get(name)

    if version is None or cs_type.version == version and prev_value != new_value:
        DATA.ALL_RAW_VALUES[name] = new_value
        DATA.ALL_VALUES[name] = cs_type.to_python(new_value)

    return prev_value


def delete_user_value(name):
    if name not in DATA.ALL_RAW_VALUES:
        return None

    prev_value = DATA.ALL_RAW_VALUES.get(name)
    del DATA.ALL_RAW_VALUES[name]
    del DATA.ALL_VALUES[name]
    del DATA.ALL_USER_DEFINES[name]

    return prev_value


def get_type_by_name(name):
    from .conf import ALL

    if name in ALL:
        return ALL[name]

    if name in DATA.ALL_USER_DEFINES:
        return DATA.ALL_USER_DEFINES[name]

    return None


def get_value(name, suffix=None):
    assert DATA.POPULATED
    cs_type = get_type_by_name(name)
    if cs_type is None:
        raise AttributeError(f"{name} is not defined in any content_settings.py file")

    return cs_type.give(DATA.ALL_VALUES[name], suffix)


def get_raw_value(name):
    assert DATA.POPULATED

    return DATA.ALL_RAW_VALUES[name]


def is_populated():  # better name?
    return getattr(DATA, "POPULATED", False)


def get_db_objects():
    from .models import ContentSetting

    return {v.name: v for v in ContentSetting.objects.all()}


def get_all_names():
    if not is_populated():
        return []
    return list(DATA.ALL_VALUES.keys())


def reset_all_values():
    if not is_populated():
        DATA.ALL_VALUES = {}
        DATA.ALL_RAW_VALUES = {}
        DATA.ALL_VALUES_CHECKSUM = None
        DATA.ALL_USER_DEFINES = {}
        DATA.POPULATED = False

    try:
        db = get_db_objects()
    except Exception:
        DATA.POPULATED = False
        return
    if USER_DEFINED_TYPES:
        reset_user_values(db)
    reset_code_values(db)

    DATA.POPULATED = True


def reset_user_values(db=None, trigger_checksum=None):

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
            cs,
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


def reset_code_values(db=None, trigger_checksum=None):
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


def check_update():
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
    db = get_db_objects()
    recalc_code_checksums(db)
    if USER_DEFINED_TYPES:
        recalc_user_checksums(db)


def recalc_user_checksums(db):
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


def recalc_code_checksums(db):
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
