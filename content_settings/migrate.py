"""
A set of functions that can be used inside migrations.
"""

from typing import Union, Optional, Type, Dict, Any
import json

from django.db import migrations, models
from django.contrib.auth.models import User


def RunImport(data: Union[str, dict], reverse_data: Optional[Union[str, dict]] = None):
    """
    The function that can be used inside your migration file.

    Args:
        data (Union[str, dict]): The data to import. Can be either a JSON string or a dictionary.
        reverse_data (Optional[Union[str, dict]], optional): The data to use for reversing the migration.
            Can be either a JSON string or a dictionary. If None, the migration will not be reversible. Defaults to None.

    Returns:
        migrations.RunPython: A RunPython operation that can be used in a migration file.

    Example:
        In your migration file:

        from content_settings.migrate import RunImport

        class Migration(migrations.Migration):
            dependencies = [
                ('content_settings', '0004_userdefined_preview'),
            ]

            operations = [
                RunImport({
                    "settings": {
                        "AFTER_TITLE": {
                            "value": "Best Settings Framework",
                            "version": ""
                        },
                        "ARTIST_LINE": {
                            "value": "",
                            "version": ""
                        },
                        "DAYS_WITHOUT_FAIL": {
                            "value": "5",
                            "version": "
                        },
                        "WEE": {
                            "value": "12",
                            "tags": "",
                            "help": "12",
                            "version": "",
                            "user_defined_type": "text"
                        }
                    }
                }),
            ]

    Note:
        This function is designed to be used within Django migration files. It handles the import of content settings,
        creating or updating them as necessary. If reverse_data is provided, it also sets up the reverse operation
        for the migration.
    """
    if isinstance(data, str):
        data = json.loads(data)

    def run(apps, schema_editor):

        import_settings(
            data,
            model_cs=apps.get_model("content_settings", "ContentSetting"),
            model_cs_history=apps.get_model(
                "content_settings", "HistoryContentSetting"
            ),
        )

    if reverse_data is None:
        return migrations.RunPython(run, lambda apps, schema_editor: None)

    if isinstance(reverse_data, str):
        reverse_data = json.loads(reverse_data)

    def reverse_run(apps, schema_editor):
        import_settings(
            reverse_data,
            model_cs=apps.get_model("content_settings", "ContentSetting"),
            model_cs_history=apps.get_model(
                "content_settings", "HistoryContentSetting"
            ),
        )

    return migrations.RunPython(run, reverse_run)


def import_settings(
    data: Dict[str, Any],
    model_cs: Type[models.Model],
    model_cs_history: Optional[Type[models.Model]] = None,
    user: Optional[User] = None,
) -> None:
    """
    Import content settings from a dictionary.

    Args:
        data (Dict[str, Any]): A dictionary containing the settings to import.
        model_cs (Type[models.Model]): The ContentSetting model class.
        model_cs_history (Optional[Type[models.Model]]): The ContentSettingHistory model class, if history tracking is enabled.
        user (Optional[User]): The user performing the import, if applicable.

    Returns:
        None

    This function iterates through the settings in the provided data dictionary,
    creating or updating ContentSetting objects as necessary. It also handles
    history tracking if a history model is provided.
    """
    for name, value in data["settings"].items():
        cs = model_cs.objects.filter(name=name).first()
        was_changed: Optional[bool] = cs is not None
        if value is None:
            was_changed = None

        if value is None:
            if cs:
                cs.delete()
        else:
            if not cs:
                cs = model_cs(name=name)
            for key, in_value in value.items():
                setattr(cs, key, in_value)
            cs.save()

        if user is not None:
            model_cs_history.update_last_record_for_name(name, user)

        elif model_cs_history is not None:
            history = model_cs_history(
                name=name, was_changed=was_changed, by_user=False
            )

            for key, in_value in value.items():
                setattr(history, key, in_value)
            history.save()
