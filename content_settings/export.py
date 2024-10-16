"""
Module for exporting, previewing and importing content settings from and to JSON
"""

import json

from django.utils.translation import gettext as _
from django.contrib.auth import get_user_model

from typing import Iterable, Tuple, List, Optional, Dict

from .types import BaseSetting
from .models import ContentSetting, HistoryContentSetting, UserPreview
from .conf import (
    USER_DEFINED_TYPES_INITIAL,
    get_type_by_name,
    validate_all_with_context,
)
from .migrate import import_settings


User = get_user_model()


class Error(Exception):
    def __init__(self, message: str) -> None:
        self.message = message
        super().__init__()

    def __str__(self) -> str:
        return self.message


def export_to_format(content_settings: Iterable[ContentSetting]) -> str:
    """
    Export content settings to JSON format
    """
    data = {}
    data_settings = data["settings"] = {}
    for cs in content_settings:

        if cs.user_defined_type:
            data_settings[cs.name] = {
                "value": cs.value,
                "tags": cs.tags,
                "help": cs.help,
                "version": cs.version,
                "user_defined_type": cs.user_defined_type,
            }
        else:
            data_settings[cs.name] = {
                "value": cs.value,
                "version": cs.version,
            }

    return json.dumps(data, indent=2)


def preview_data(data: dict, user: Optional[User] = None) -> Tuple[List, List, List]:
    """
    Validate data and return three lists: errors, applied, skipped

    Those list are used for previewing import and applying import.
    """
    errors = []
    applied = []
    skipped = []
    for name, value in data["settings"].items():
        try:
            if applied_row := applied_preview(name, value, user):
                applied.append(applied_row)
            else:
                skipped.append({"name": name, "reason": _("Value is the same")})
        except Exception as e:
            errors.append({"name": name, "reason": str(e)})
    return errors, applied, skipped


def applied_preview(
    name: str, value: dict, user: Optional[User] = None
) -> Optional[dict]:
    """
    the function returns applied element for previewing import.

    if function returns None, the setting is not applied, added to skipped list instead.

    if function raises an exception, the setting is not applied, added to errors list instead.
    """

    if "user_defined_type" in value:
        return applied_preview_user_defined_type(name, value, user)

    try:
        db_setting = ContentSetting.objects.get(name=name)
    except ContentSetting.DoesNotExist:
        raise Error(_("Setting does not exist"))

    cs_type = get_type_by_name(name)

    if cs_type is None:
        raise Error(_("Setting does not exist (type not found)"))

    for key in ["value", "version"]:
        if key not in value or not isinstance(value[key], str):
            raise Error(_('"%s" is not set or not a string' % key))

    if db_setting.value == value["value"]:
        return None

    if db_setting.version != value["version"]:
        raise Error(_("Version is not the same"))

    if user is not None and not cs_type.can_update(user):
        raise Error(_("You don't have permissions to update the setting"))

    cs_type.validate_value(value["value"])

    return {
        "name": name,
        "old_value": db_setting.value,
        "new_value": value["value"],
        "full": {"value": value["value"]},
    }


def applied_preview_user_defined_type(
    name: str, value: dict, user: Optional[User] = None
) -> Optional[dict]:
    """
    `applied_preview` for user defined type.
    """
    for key in ["value", "version", "tags", "help"]:
        if key not in value or not isinstance(value[key], str):
            raise Error('"%s" is not set or not a string' % key)

    cs_type = USER_DEFINED_TYPES_INITIAL.get(value["user_defined_type"])

    if cs_type is None:
        raise Error(_("Invalid user_defined_type"))

    if cs_type.version != value["version"]:
        raise Error(_("Invalid version"))

    if user is not None and not cs_type.can_update(user):
        raise Error(_("You don't have permissions to update the setting"))

    cs_type.validate_value(value["value"])

    try:
        db_setting = ContentSetting.objects.get(name=name)
    except ContentSetting.DoesNotExist:
        return {"name": name, "new_value": value, "full": value}

    if not db_setting.user_defined_type:
        raise Error(_("Setting is not user defined"))

    applied_new_value = {}
    applied_old_value = {}
    for key, in_value in value.items():
        if (
            key == "tags"
            and set(getattr(db_setting, key).splitlines()) != set(in_value.splitlines())
            or key != "tags"
            and getattr(db_setting, key) != in_value
        ):
            applied_new_value[key] = in_value
            applied_old_value[key] = getattr(db_setting, key)

    if not applied_new_value:
        return None

    return {
        "name": name,
        "old_value": applied_old_value,
        "new_value": applied_new_value,
        "full": value,
    }


def import_to(
    data: Dict, applied: List[Dict], preview: bool, user: Optional[User] = None
):
    """
    Import content settings from JSON data and previewed apply data. Arguments:
    - data: JSON data
    - applied: List of applied settings. The list is returned by import_preview_data.
    - user: User object
    - preview: If True, import to preview

    It raises Error if something is wrong.
    """
    prepared_names = {}
    for v in applied:
        data_setting = data["settings"][v["name"]]
        if "user_defined_type" in data_setting:
            prepared_names[v["name"]] = (
                data_setting["value"],
                data_setting["user_defined_type"],
                (
                    set(data_setting["tags"].splitlines())
                    if data_setting["tags"]
                    else set()
                ),
                data_setting["help"],
            )
        else:
            prepared_names[v["name"]] = v["new_value"]

    validate_all_with_context(prepared_names)

    if preview:
        assert user is not None, "User is required"
        for value in applied:
            UserPreview.add_by_user(
                user=user,
                name=value["name"],
                **{k: v for k, v in value["full"].items() if k != "version"},
            )
    else:
        import_settings(
            {"settings": {value["name"]: value["full"] for value in applied}},
            model_cs=ContentSetting,
            model_cs_history=HistoryContentSetting,
            user=user,
        )
