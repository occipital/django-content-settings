"""
the module is used for connecting signals to the content settings.
"""

from django.db.models.signals import post_save, post_migrate, post_delete, pre_save
from django.core.signals import request_started
from django.db.backends.signals import connection_created
from django.apps import apps
from django.db import transaction

from .settings import (
    USER_DEFINED_TYPES,
    UPDATE_DB_VALUES_BY_MIGRATE,
    CHECK_UPDATE_CELERY,
    CHECK_UPDATE_HUEY,
    PRECACHED_PY_VALUES,
    VALIDATE_DEFAULT_VALUE,
)

from django.dispatch import receiver

from .caching import (
    check_update,
    recalc_checksums,
    validate_default_values,
    populate,
)
from .conf import set_initial_values_for_db, get_type_by_name, get_str_tags
from .models import ContentSetting, HistoryContentSetting
from .utils import call_base_str


@receiver(post_delete, sender=ContentSetting)
@receiver(post_save, sender=ContentSetting)
def do_update_stored_checksum(*args, **kwargs):
    """
    update the stored checksum of the settings.
    """
    connection = transaction.get_connection()
    if connection.in_atomic_block:
        transaction.on_commit(recalc_checksums)
    else:
        recalc_checksums()


@receiver(post_save, sender=ContentSetting)
def trigger_on_change(sender, instance, created, **kwargs):
    """
    Trigger on_change and on_change_commited for the content setting
    """
    if created:
        return

    cs_type = get_type_by_name(instance.name)
    if cs_type is None:
        return

    for on_change in cs_type.get_on_change():
        call_base_str(on_change, instance)

    on_changes = cs_type.get_on_change_commited()
    if not on_changes:
        return

    connection = transaction.get_connection()
    if connection.in_atomic_block:
        transaction.on_commit(lambda: [call_base_str(f, instance) for f in on_changes])
    else:
        for on_change in on_changes:
            call_base_str(on_change, instance)


@receiver(post_save, sender=ContentSetting)
def create_history_settings(sender, instance, created, **kwargs):
    HistoryContentSetting.objects.create(
        name=instance.name,
        value=instance.value,
        version=instance.version,
        tags=instance.tags,
        help=instance.help,
        user_defined_type=instance.user_defined_type,
        was_changed=not created,
    )


@receiver(pre_save, sender=ContentSetting)
def update_value_tags(sender, instance, **kwargs):
    if instance.user_defined_type:
        return

    cs_type = get_type_by_name(instance.name)
    if cs_type is None:
        return

    instance.tags = get_str_tags(instance.name, cs_type, instance.value)


if USER_DEFINED_TYPES:

    @receiver(pre_save, sender=ContentSetting)
    def check_user_defined_type_version(sender, instance, **kwargs):
        from .conf import USER_DEFINED_TYPES_INITIAL

        if instance.user_defined_type not in USER_DEFINED_TYPES_INITIAL:
            return
        instance.version = USER_DEFINED_TYPES_INITIAL[
            instance.user_defined_type
        ].version
        if instance.tags:
            instance.tags = instance.tags.replace("\r\n", "\n")


@receiver(post_delete, sender=ContentSetting)
def create_history_settings_delete(sender, instance, **kwargs):
    HistoryContentSetting.objects.create(
        name=instance.name,
        value=instance.value,
        version=instance.version,
        tags=instance.tags,
        help=instance.help,
        was_changed=None,
    )


if VALIDATE_DEFAULT_VALUE:

    @receiver(connection_created)
    def validate_default_values_for_connection(*args, **kwargs):
        validate_default_values()


if PRECACHED_PY_VALUES:

    @receiver(connection_created)
    def reset_all_values_by_connection(*args, **kwargs):
        populate()


@receiver(request_started)
def check_update_for_request(*args, **kwargs):
    check_update()


if UPDATE_DB_VALUES_BY_MIGRATE:

    @receiver(post_migrate, sender=apps.get_app_config("content_settings"))
    def update_stored_values(*args, **kwargs):
        try:
            with transaction.atomic():
                log = set_initial_values_for_db(apply=True)
        except Exception as e:
            log = [("Error", str(e))]

        if not log:
            return

        for l in log:
            print(" ".join(l))


# INTEGRATIONS

if CHECK_UPDATE_CELERY:
    try:
        from celery.signals import task_prerun
    except ImportError:
        pass
    else:

        @task_prerun.connect
        def check_update_for_celery(*args, **kwargs):
            check_update()


if CHECK_UPDATE_HUEY:
    try:
        from huey.contrib.djhuey import pre_execute
    except ImportError:
        pass
    else:

        @pre_execute()
        def check_update_for_huey(*args, **kwargs):
            check_update()
