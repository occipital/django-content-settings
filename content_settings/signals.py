from django.db.models.signals import post_save, post_migrate, post_delete
from django.core.signals import request_started
from django.db.backends.signals import connection_created
from django.apps import apps
from django.db import transaction

from django.dispatch import receiver

from .caching import (
    check_update,
    reset_all_values,
    recalc_checksums,
)
from .conf import set_initial_values_for_db
from .models import ContentSetting, HistoryContentSetting


@receiver(post_delete, sender=ContentSetting)
@receiver(post_save, sender=ContentSetting)
def do_update_stored_checksum(*args, **kwargs):
    connection = transaction.get_connection()
    if connection.in_atomic_block:
        transaction.on_commit(recalc_checksums)
    else:
        recalc_checksums()


@receiver(post_save, sender=ContentSetting)
def create_history_settings(sender, instance, created, **kwargs):
    HistoryContentSetting.objects.create(
        name=instance.name,
        value=instance.value,
        version=instance.version,
        was_changed=not created,
    )


@receiver(post_delete, sender=ContentSetting)
def create_history_settings_delete(sender, instance, **kwargs):
    HistoryContentSetting.objects.create(
        name=instance.name,
        value=instance.value,
        version=instance.version,
        was_changed=None,
    )


@receiver(request_started)
def check_update_for_request(*args, **kwargs):
    check_update()


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


@receiver(connection_created)
def db_connection_done(*args, **kwargs):
    reset_all_values()
