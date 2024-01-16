from importlib import import_module


from django.apps import apps

from .types.basic import BaseSetting
from .caching import get_value
from .settings import USER_DEFINED_TYPES

LAZY_ATTRIBUTE_PREFIX = "lazy"
CLS_ATTRIBUTE_PREFIX = "type"

USER_DEFINED_TYPES_INSTANCE = {}
ALL = {}

if USER_DEFINED_TYPES:
    for slug, imp_line, name in USER_DEFINED_TYPES:
        imp_line_parts = imp_line.split(".")
        type_module = import_module(".".join(imp_line_parts[:-1]))
        type_class = getattr(type_module, imp_line_parts[-1])
        USER_DEFINED_TYPES_INSTANCE[slug] = type_class(is_user_defined=True)


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
        if not isinstance(val, BaseSetting):
            continue

        assert attr not in ALL, "Content Setting {} defined twice".format(attr)

        if attr in ALL and not ALL[attr].is_user_defined:
            raise AssertionError("Overwriting content setting {}".format(attr))

        if not attr.isupper():
            raise AssertionError("content setting {} should be uppercase".format(attr))

        assert (
            not val.is_user_defined
        ), "Do not set is_user_defined=True in content_settings.py"

        ALL[attr] = val


def split_attr(value):
    """
    splits the name of the attr on 3 parts: prefix, name, suffix

    * prefix can only be LAZY_ATTRIBUTE_PREFIX or CLS_ATTRIBUTE_PREFIX
    * name should be uppercase
    * suffix can be any string, but not uppercase
    """
    prefix = None
    parts = value.split("__")

    if parts[0] in (LAZY_ATTRIBUTE_PREFIX, CLS_ATTRIBUTE_PREFIX):
        prefix = parts.pop(0)

    assert len(parts), f"Invalid attribute name: {value}; can not be only prefix"

    name = parts.pop(0)
    assert name.isupper(), f"Invalid attribute name: {value}; name should be uppercase"

    while parts:
        if not parts[0].isupper():
            break

        name += "__" + parts.pop(0)

    if len(parts):
        return prefix, name, "__".join(parts).lower()

    return prefix, name, None


class _Settings:
    def __getattr__(self, value):
        prefix, name, suffix = split_attr(value)
        if prefix == CLS_ATTRIBUTE_PREFIX:
            return ALL[name]
        elif prefix == LAZY_ATTRIBUTE_PREFIX:
            return ALL[name].lazy_give(lambda: get_value(name, suffix), suffix)
        else:
            return get_value(name, suffix)

    def __contains__(self, value):
        _, name, suffix = split_attr(value)
        return name in ALL and ALL[name].can_suffix(suffix)


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
