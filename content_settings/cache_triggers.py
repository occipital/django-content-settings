"""
# Cache Trigger is a backend to sending a signal of when py-object(s) should be updated
"""

from typing import Any, Dict, Set, Optional, List
import hashlib
from functools import cached_property
from threading import local

from django.core.cache import caches

from . import __version__
from .settings import (
    USER_DEFINED_TYPES,
)


class ThreadLocalData(local):
    ALL_VALUES_CHECKSUM: str = ""


DATA = ThreadLocalData()


class BaseCacheTrigger:
    def __init__(self, params: dict) -> None:
        pass

    def check(self):
        """
        check if the trigger condition is met.
        """
        raise NotImplementedError

    def reset(self):
        """
        reset the trigger state.

        Called during the first run of the system.
        """
        raise NotImplementedError

    def get_form_checksum(self):
        """
        returns checksum that uses for checksum validation during form submit
        """
        raise NotImplementedError

    def db_changed(self):
        """
        recalculate the trigger state for the current DB state and save it to the outside source (cache backend).

        Called when the db value is changed.
        """
        raise NotImplementedError


class VersionChecksum(BaseCacheTrigger):
    """
    Arguments:
        * cache_backend (str, default="default"): cache backend name
        * cache_timeout (int, default=60 * 60 * 24): cache timeout
        * spliter (str, default="::"): spliter for the checksum
        * key_prefix (str, default="CS_CHECKSUM_"): key prefix for the checksum

    The algorithm:

        * during the first run, the checksum is calculated for all the values from the DB and saved to the cache backend
        * the cache key is calculated based on the current versions of all of the settings.
        * if the DB values are changed it saves the new checksum under the same cache key (so only instances with the same configuration will see the change)
        * if the checksum is changed comparing to the checksum in the local storage
    """

    def __init__(
        self,
        cache_backend: str = "default",
        cache_timeout: int = 60 * 60 * 24,
        spliter: str = "::",
        key_prefix: str = "CS_CHECKSUM_",
    ):
        self.cache_backend = caches[cache_backend]
        self.cache_timeout = cache_timeout
        self.spliter = spliter
        self.key_prefix = key_prefix + __version__
        self.last_checksum_from_cache = None

    def hash_value(self, value: str) -> str:
        """
        generate md5 hash for a string
        """
        return hashlib.md5(value.encode("utf-8")).hexdigest()

    def dict_checksum(self, values: Dict[str, Any]) -> str:
        """
        generate md5 hash for a dict with keys and values as strings
        """
        return self.hash_value(
            self.spliter.join(
                f"{name}{self.spliter}{values[name]}" for name in sorted(values.keys())
            )
        )

    @cached_property
    def cache_key(self) -> str:
        """
        returns cache key for checksum values (one should not be changed over time)
        """
        from .conf import ALL

        return (
            self.key_prefix
            + self.dict_checksum(
                {
                    name: ALL[name].version
                    for name in ALL.keys()
                    if not ALL[name].constant
                }
            )
            + self.user_cache_key_prefix
        )

    @property
    def user_cache_key_prefix(self) -> str:
        """
        returns cache key for user defined types (one should not be changed over time) if user defined types are not used, returns None
        """
        if not USER_DEFINED_TYPES:
            return ""

        from .conf import USER_DEFINED_TYPES_INITIAL

        return self.dict_checksum(
            {k: v.version for k, v in USER_DEFINED_TYPES_INITIAL.items()}
        )

    def set_local_checksum(self, value: Optional[str] = None) -> None:
        """
        calculate and set checksum in the local thread
        """
        if value is None:
            value = self.calc_checksum()
        DATA.ALL_VALUES_CHECKSUM = value

    def get_local_checksum(self) -> str:
        return DATA.ALL_VALUES_CHECKSUM

    def get_form_checksum(self):
        return self.get_local_checksum()

    def calc_checksum(self) -> str:
        from .models import ContentSetting

        return self.dict_checksum(
            {
                cs.name: cs.value + (cs.tags or "") + (cs.version or "")
                for cs in ContentSetting.objects.all()
            }
        )

    def push_checksum(self, value: Optional[str] = None) -> None:
        """
        save to cache backend the checksum
        """

        if value is None:
            value = DATA.ALL_VALUES_CHECKSUM

        self.cache_backend.set(self.cache_key, value, self.cache_timeout)

    def get_checksum_from_cache(self) -> Optional[str]:
        """
        get the checksum from the cache backend
        """
        return self.cache_backend.get(self.cache_key)

    def check(self):
        self.last_checksum_from_cache = self.get_checksum_from_cache()
        return (
            self.last_checksum_from_cache is not None
            and self.get_local_checksum() != self.last_checksum_from_cache != ""
        )

    def reset(self):
        if self.last_checksum_from_cache is None:
            self.set_local_checksum()
            self.push_checksum()
        else:
            self.set_local_checksum(self.last_checksum_from_cache)

    def db_changed(self):
        self.push_checksum(self.calc_checksum())
