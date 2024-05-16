from importlib import import_module
from functools import partial

from django.apps import apps
from django.conf import settings as django_settings

from .types.basic import BaseSetting
from .caching import get_value, get_type_by_name, get_all_names
from .settings import USER_DEFINED_TYPES, TAGS
from .store import add_app_name

USER_DEFINED_TYPES_INSTANCE = {}
USER_DEFINED_TYPES_INITIAL = {}
USER_DEFINED_TYPES_NAME = {}
ALL = {}
PREFIXSES = {}


def import_object(path):
    parts = path.split(".")
    module = import_module(".".join(parts[:-1]))
    return getattr(module, parts[-1])


if USER_DEFINED_TYPES:
    for slug, imp_line, name in USER_DEFINED_TYPES:
        type_class = import_object(imp_line)
        USER_DEFINED_TYPES_INSTANCE[slug] = partial(
            type_class, user_defined_slug=slug, version=type_class.version
        )
        USER_DEFINED_TYPES_INITIAL[slug] = USER_DEFINED_TYPES_INSTANCE[slug]()
        USER_DEFINED_TYPES_NAME[slug] = name


CALL_TAGS = None


def get_call_tags():
    global CALL_TAGS

    if CALL_TAGS is not None:
        return CALL_TAGS

    CALL_TAGS = []
    for func_tag in TAGS:
        if isinstance(func_tag, str):
            func_tag = import_object(func_tag)
        elif callable(func_tag):
            pass
        else:
            raise AssertionError(f"func_tag: {func_tag} should be str or callable")
        CALL_TAGS.append(func_tag)
    return CALL_TAGS


def gen_tags(name, cs_type, value):
    tags = set()
    for func_tag in get_call_tags():
        tags |= func_tag(name, cs_type, value)
    return tags


def register_prefix(name):
    def _cover(func):
        PREFIXSES[name] = func
        return func

    return _cover


@register_prefix("lazy")
def lazy_prefix(name, suffix):
    return get_type_by_name(name).lazy_give(lambda: get_value(name, suffix), suffix)


@register_prefix("type")
def type_prefix(name, suffix):
    assert not suffix, "type prefix can not have suffix"

    return get_type_by_name(name)


@register_prefix("startswith")
def startswith_prefix(name, suffix):
    return content_settings.startswith(name, suffix)


@register_prefix("withtag")
def withtag_prefix(name, suffix):
    return {
        **content_settings.withtag(name, suffix),
        **content_settings.withtag(name.lower(), suffix),
    }


for app_config in apps.app_configs.values():
    app = app_config.name
    try:
        content_settings = import_module(app + ".content_settings")
    except ImportError as e:
        if e.name != app + ".content_settings":
            raise
        continue
    for attr in dir(content_settings):
        if not attr.isupper():
            continue

        val = getattr(content_settings, attr)

        if not isinstance(val, BaseSetting):
            continue

        assert attr not in ALL, "Content Setting {} defined twice".format(attr)

        if attr in ALL and not ALL[attr].user_defined_slug:
            raise AssertionError("Overwriting content setting {}".format(attr))

        assert (
            not val.user_defined_slug
        ), "Do not set user_defined_slug in content_settings.py"

        ALL[attr] = val
        add_app_name(attr, app)


def split_attr(value):
    """
    splits the name of the attr on 3 parts: prefix, name, suffix

    * prefix should be registered by register_prefix
    * name should be uppercase
    * suffix can be any string, but not uppercase
    """
    prefix = None
    parts = value.split("__")

    if parts[0] in PREFIXSES:
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
        if prefix:
            assert (
                prefix in PREFIXSES
            ), f"Invalid attribute name: {value}; prefix not found"
            return PREFIXSES[prefix](name, suffix)
        return get_value(name, suffix)

    def __dir__(self):
        return get_all_names()

    def startswith(self, value, suffix=None):
        return {k: get_value(k, suffix) for k in dir(self) if k.startswith(value)}

    def withtag(self, value, suffix=None):
        return {
            k: get_value(k, suffix)
            for k in dir(self)
            if value in get_type_by_name(k).get_tags()
        }

    def __contains__(self, value):
        _, name, suffix = split_attr(value)
        cs_type = get_type_by_name(name)
        return cs_type is not None and cs_type.can_suffix(suffix)


class _UnitedSettings(_Settings):
    def __getattr__(self, value):
        if hasattr(django_settings, value):
            return getattr(django_settings, value)

        return super().__getattr__(value)

    def __contains__(self, value):
        return hasattr(django_settings, value) or super().__contains__(value)


def get_str_tags(cs_name, cs_type, value=None):
    tags = cs_type.get_tags()
    if not cs_type.user_defined_slug:
        tags |= cs_type.get_content_tags(
            cs_name, cs_type.default if value is None else value
        )
    return "\n".join(sorted(tags))


# TODO: remove preview settings during migration


def set_initial_values_for_db(apply=False):
    from content_settings.models import ContentSetting, HistoryContentSetting

    changes = []

    def execute(name, key, func):
        changes.append((name, key))
        if apply:
            func()
            HistoryContentSetting.update_last_record_for_name(name)

    def execute_update_obj(name, cs, show="update", **kwargs):
        def _up():
            for k, v in kwargs.items():
                setattr(cs, k, v)
            cs.save()

        execute(name, show, _up)

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
                    tags=get_str_tags(k, cs_type),
                    help=cs_type.get_help(),
                ),
            )

    for cs in ContentSetting.objects.all():
        if cs.name in ALL:
            cs_type = ALL[cs.name]
            if cs_type.constant:
                execute(cs.name, "delete", lambda: cs.delete())
                continue

            assert (
                not cs.user_defined_type or cs_type.overwrite_user_defined
            ), f"{cs.name} is not a code setting and not overwrite_user_defined"

            if cs.version != cs_type.version:
                execute_update_obj(
                    cs.name,
                    cs,
                    value=cs_type.default,
                    version=cs_type.version,
                    user_defined_type=None,
                )

            if cs.user_defined_type:
                execute_update_obj(
                    cs.name,
                    cs,
                    user_defined_type=None,
                    show="adjust",
                )

            str_tags = get_str_tags(cs.name, cs_type, cs.value)
            str_help = cs_type.get_help()

            if cs.tags != str_tags or cs.help != str_help:
                execute_update_obj(
                    cs.name,
                    cs,
                    tags=str_tags,
                    help=str_help,
                    show="adjust",
                )

        else:
            if cs.user_defined_type:
                if cs.user_defined_type not in USER_DEFINED_TYPES_INSTANCE:
                    execute(cs.name, "delete", lambda: cs.delete())
                elif (
                    cs.version
                    != USER_DEFINED_TYPES_INITIAL[cs.user_defined_type].version
                ):
                    cs_type = USER_DEFINED_TYPES_INSTANCE[cs.user_defined_type]()
                    execute_update_obj(
                        cs.name, cs, value=cs_type.default, version=cs_type.version
                    )
            else:
                execute(cs.name, "delete", lambda: cs.delete())

    return changes


content_settings = _Settings()
settings = _UnitedSettings()
