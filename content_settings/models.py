from collections import defaultdict

from django.db import models
from django.core.exceptions import ValidationError
from django.utils import timezone
from django.conf import settings


class ContentSetting(models.Model):
    name = models.CharField(max_length=200, unique=True)
    value = models.TextField(blank=True)
    version = models.CharField(max_length=50, null=True)

    class Meta:
        ordering = ("name",)

    def __str__(self):
        return self.name


class HistoryContentSetting(models.Model):
    CHANGED_CHOICES = (
        (True, "Changed"),
        (False, "Added"),
        (None, "Removed"),
    )
    BY_USER_CHOICES = (
        (True, "by user"),
        (False, "by app"),
        (None, "unknown"),
    )

    created_on = models.DateTimeField(null=False, default=timezone.now)

    name = models.CharField(max_length=200)
    value = models.TextField(blank=True, null=True)
    version = models.CharField(max_length=50, null=True)

    was_changed = models.BooleanField(null=True, default=True, choices=CHANGED_CHOICES)
    by_user = models.BooleanField(null=True, default=None, choices=BY_USER_CHOICES)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True
    )

    class Meta:
        ordering = ("-id",)
        indexes = [
            models.Index(fields=["name", "-id"]),
        ]

    @classmethod
    def update_last_record_for_name(cls, name, user=None):
        last_setting = cls.objects.filter(name=name).first()
        last_setting.user = user
        last_setting.by_user = user is not None
        last_setting.save()

    @classmethod
    def gen_unique_records(cls, name):
        next_obj = None
        records = cls.objects.filter(name=name)
        if not records.exists():
            return []

        for obj in records:
            if next_obj is None:
                next_obj = obj
                continue

            if next_obj.value != obj.value or next_obj.was_changed != obj.was_changed:
                yield next_obj

            next_obj = obj

        yield obj


class UserTagSetting(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    name = models.CharField(max_length=200)
    tag = models.TextField()

    class Meta:
        unique_together = (("user", "name", "tag"),)

    def __str__(self):
        return f"{self.user} - {self.name} - {self.tag}"

    @classmethod
    def get_user_settings(cls, user):
        settings = defaultdict(set)
        for name, tag in cls.objects.filter(user=user).values_list("name", "tag"):
            settings[name].add(tag)
        return settings
