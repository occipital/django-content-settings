from threading import local
import hashlib
from functools import lru_cache

from django.core.cache import caches

from .settings import (
    CHECKSUM_KEY_PREFIX,
    CACHE_SPLITER,
    CACHE_TIMEOUT,
    CACHE_BACKEND,
    VALUES_ONLY_FROM_DB,
)


DATA = local()


def get_cache():
    return caches[CACHE_BACKEND]


@lru_cache(maxsize=None)
def get_cache_key():
    from .conf import ALL

    return calc_checksum({name: ALL[name].version for name in ALL.keys()})


def calc_checksum(values):
    """
    generate md5 hash for a dict with keys and values as strings
    """
    return hash_value(
        CACHE_SPLITER.join(values[name] for name in sorted(values.keys()))
    )


def hash_value(value):
    """
    generate md5 hash for a string
    """
    return hashlib.md5(value.encode("utf-8")).hexdigest()


def set_local_checksum():
    DATA.ALL_VALUES_CHECKSUM = calc_checksum(DATA.ALL_RAW_VALUES)


def push_checksum(value=None, key=None):
    if key is None:
        key = get_cache_key()

    if value is None:
        value = DATA.ALL_VALUES_CHECKSUM

    get_cache().set(CHECKSUM_KEY_PREFIX + key, value, CACHE_TIMEOUT)


def get_checksum_from_store():
    return get_cache().get(CHECKSUM_KEY_PREFIX + get_cache_key())


def get_checksum_from_local():
    return DATA.ALL_VALUES_CHECKSUM


def set_new_value(name, new_value, version=None):
    from .conf import ALL

    prev_value = DATA.ALL_RAW_VALUES.get(name)

    if version is None or ALL[name].version == version and prev_value != new_value:
        DATA.ALL_RAW_VALUES[name] = new_value
        DATA.ALL_VALUES[name] = ALL[name].to_python(new_value)

    return prev_value


def get_value(name):
    assert DATA.POPULATED

    from .conf import ALL

    return ALL[name].give(DATA.ALL_VALUES[name])


def is_populated():  # better name?
    return getattr(DATA, "POPULATED", False)


def get_db_objects():
    from .models import ContentSetting

    return {v.name: v for v in ContentSetting.objects.all()}


def reset_all_values(trigger_checksum=None):
    if not is_populated():
        DATA.ALL_VALUES = {}
        DATA.ALL_RAW_VALUES = {}
        DATA.ALL_VALUES_CHECKSUM = None
        DATA.POPULATED = False

    from .conf import ALL

    try:
        db = get_db_objects()
    except Exception:
        DATA.POPULATED = False
        return

    DATA.POPULATED = True
    for name in ALL.keys():
        if name in db:
            set_new_value(name, db[name].value, version=db[name].version)
        else:
            if VALUES_ONLY_FROM_DB:
                raise AssertionError(f"VALUES_ONLY_FROM_DB: {name} is not in DB")
            set_new_value(name, ALL[name].default, ALL[name].version)

    assert len(DATA.ALL_VALUES) == len(ALL), "Not all values are populated"

    set_local_checksum()

    if trigger_checksum != get_checksum_from_local():
        push_checksum()


def check_update():
    if not is_populated():
        return

    store_checksum = get_checksum_from_store()
    if store_checksum is not None and store_checksum != get_checksum_from_local():
        reset_all_values(trigger_checksum=store_checksum)


def recalc_checksums():
    """ """

    from .conf import ALL

    db = get_db_objects()

    db_versions = {}
    db_values = {}

    for name in set(ALL.keys()) | set(db.keys()):
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
