from importlib import import_module
import operator

from collections import defaultdict


from django.conf import settings
from django.apps import apps

from .types.basic import BaseSetting
from .caching import get_value

LAZY_ATTRIBUTE_PREFIX = "lazy__"
CLS_ATTRIBUTE_PREFIX = "type__"

ALL = {}
FETCH_GROUPS = defaultdict(set)


class LazyObject:
    def __init__(self, factory):
        # Assign using __dict__ to avoid the setattr method.
        self.__dict__["_factory"] = factory

    def new_method_proxy(func):
        """
        Util function to help us route functions
        to the nested object.
        """

        def inner(self, *args):
            return func(self._factory(), *args)

        return inner

    def __call__(self, *args, **kwargs):
        return self._factory()(*args, **kwargs)

    __getattr__ = new_method_proxy(getattr)
    __bytes__ = new_method_proxy(bytes)
    __str__ = new_method_proxy(str)
    __bool__ = new_method_proxy(bool)
    __dir__ = new_method_proxy(dir)
    __hash__ = new_method_proxy(hash)
    __class__ = property(new_method_proxy(operator.attrgetter("__class__")))
    __eq__ = new_method_proxy(operator.eq)
    __lt__ = new_method_proxy(operator.lt)
    __le__ = new_method_proxy(operator.le)
    __gt__ = new_method_proxy(operator.gt)
    __ge__ = new_method_proxy(operator.ge)
    __ne__ = new_method_proxy(operator.ne)
    __mod__ = new_method_proxy(operator.mod)
    __hash__ = new_method_proxy(hash)
    __getitem__ = new_method_proxy(operator.getitem)
    __iter__ = new_method_proxy(iter)
    __len__ = new_method_proxy(len)
    __contains__ = new_method_proxy(operator.contains)


for app_config in apps.app_configs.values():
    app = app_config.name
    try:
        content_settings = import_module(app + ".content_settings")
    except ImportError as e:
        if e.name != app + ".content_settings":
            raise
        continue
    for attr in dir(content_settings):
        val = getattr(content_settings, attr)
        if isinstance(val, BaseSetting):
            if attr in ALL:
                raise ValueError("Overwriting content setting {}".format(attr))

            if val.fetch_groups is not None:
                fetch_groups = val.fetch_groups
                if isinstance(fetch_groups, str):
                    fetch_groups = [fetch_groups]
                for fetch_groups in fetch_groups:
                    FETCH_GROUPS[fetch_groups.upper().replace("-", "_")].add(attr)

            ALL[attr] = val


class _Settings:
    def __getattr__(self, name):
        if name.startswith(CLS_ATTRIBUTE_PREFIX):
            return ALL[name[len(CLS_ATTRIBUTE_PREFIX) :]]

        if name.startswith(LAZY_ATTRIBUTE_PREFIX):
            name = name[len(LAZY_ATTRIBUTE_PREFIX) :]
            return LazyObject(lambda: get_value(name))
        return get_value(name)

    def __contains__(self, name):
        if name.startswith(LAZY_ATTRIBUTE_PREFIX):
            name = name[len(LAZY_ATTRIBUTE_PREFIX) :]
        if name.startswith(CLS_ATTRIBUTE_PREFIX):
            name = name[len(CLS_ATTRIBUTE_PREFIX) :]
        return name in ALL


def set_initial_values_for_db(apply=False):
    from content_settings.models import ContentSetting, HistoryContentSetting

    changes = []
    for k in ALL.keys():
        try:
            ContentSetting.objects.get(name=k)
        except ContentSetting.DoesNotExist:
            if apply:
                ContentSetting.objects.create(
                    name=k,
                    value=ALL[k].default,
                    version=ALL[k].version,
                )
                HistoryContentSetting.update_last_record_for_name(k)

            changes.append((k, "create"))

    for cs in ContentSetting.objects.all():
        if cs.name in ALL:
            if cs.version != ALL[cs.name].version:
                if apply:
                    cs.value = ALL[cs.name].default
                    cs.version = ALL[cs.name].version
                    cs.save()
                    HistoryContentSetting.update_last_record_for_name(cs.name)

                changes.append((cs.name, "update"))

        else:
            if apply:
                cs.delete()
                HistoryContentSetting.update_last_record_for_name(cs.name)

            changes.append((cs.name, "delete"))


content_settings = _Settings()
