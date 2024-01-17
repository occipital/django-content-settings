from importlib import import_module
from functools import partial

from django.apps import apps

from .types.basic import BaseSetting
from .caching import get_value, get_type_by_name
from .settings import USER_DEFINED_TYPES

LAZY_ATTRIBUTE_PREFIX = "lazy"
CLS_ATTRIBUTE_PREFIX = "type"

USER_DEFINED_TYPES_INSTANCE = {}
USER_DEFINED_TYPES_VERSION = {}
ALL = {}

if USER_DEFINED_TYPES:
    for slug, imp_line, name in USER_DEFINED_TYPES:
        imp_line_parts = imp_line.split(".")
        type_module = import_module(".".join(imp_line_parts[:-1]))
        type_class = getattr(type_module, imp_line_parts[-1])
        USER_DEFINED_TYPES_INSTANCE[slug] = partial(
            type_class, is_user_defined=True, version=type_class.version
        )
        USER_DEFINED_TYPES_VERSION[slug] = type_class.version


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
            return get_type_by_name(name)
        elif prefix == LAZY_ATTRIBUTE_PREFIX:
            return get_type_by_name(name).lazy_give(
                lambda: get_value(name, suffix), suffix
            )
        else:
            return get_value(name, suffix)

    def __contains__(self, value):
        _, name, suffix = split_attr(value)
        cs_type = get_type_by_name(name)
        return cs_type is not None and cs_type.can_suffix(suffix)


def get_str_tags(cs_type):
    if cs_type.get_tags():
        return "\n".join(sorted(cs_type.get_tags()))
    return ""


def set_initial_values_for_db(apply=False):
    from content_settings.models import ContentSetting, HistoryContentSetting

    changes = []

    def execute(name, key, func):
        changes.append((name, key))
        if apply:
            func()
            HistoryContentSetting.update_last_record_for_name(name)

    def execute_update_version(name, cs, **kwargs):
        def _():
            for k, v in kwargs.items():
                setattr(cs, k, v)
            cs.save()

        execute(name, "update", _)

    for k, cs_type in ALL.items():
        if cs_type.constant:
            continue

        try:
            ContentSetting.objects.get(name=k)
        except ContentSetting.DoesNotExist:
            execute(
                k,
                "create",
                lambda: ContentSetting.objects.create(
                    name=k,
                    value=cs_type.default,
                    version=cs_type.version,
                    tags=get_str_tags(cs_type),
                    help=cs_type.get_help(),
                ),
            )

    for cs in ContentSetting.objects.all():
        if cs.name in ALL:
            cs_type = ALL[cs.name]
            if cs_type.constant:
                execute(cs.name, "delete", lambda: cs.delete())
                continue

            if cs.version != cs_type.version:
                execute_update_version(
                    cs.name, cs, value=cs_type.default, version=cs_type.version
                )

            str_tags = get_str_tags(cs_type)
            str_help = cs_type.get_help()

            if cs.tags != str_tags or cs.help != str_help:
                execute_update_version(cs.name, cs, tags=str_tags, help=str_help)

        else:
            if cs.user_defined_type:
                if cs.user_defined_type not in USER_DEFINED_TYPES_INSTANCE:
                    execute(cs.name, "delete", lambda: cs.delete())
                elif cs.version != USER_DEFINED_TYPES_VERSION[cs.user_defined_type]:
                    cs_type = USER_DEFINED_TYPES_INSTANCE[cs.user_defined_type]()
                    execute_update_version(
                        cs.name, cs, value=cs_type.default, version=cs_type.version
                    )
            else:
                execute(cs.name, "delete", lambda: cs.delete())

    return changes


content_settings = _Settings()
