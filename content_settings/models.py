from collections import defaultdict

from django.db import models
from django.core.validators import RegexValidator
from django.utils import timezone
from django.conf import settings


class ContentSetting(models.Model):
    name = models.CharField(
        max_length=200,
        unique=True,
        validators=[
            RegexValidator(
                regex=r"^[A-Z][A-Z0-9_]*$",
                message="Value must be uppercase, can include numbers and underscores, and cannot start with a number.",
            ),
        ],
    )
    value = models.TextField(blank=True)
    version = models.CharField(max_length=50, null=True)
    help = models.TextField(blank=True, null=True)
    tags = models.TextField(blank=True, null=True)
    user_defined_type = models.CharField(
        max_length=50, null=True, default=None, db_index=True
    )

    class Meta:
        ordering = ("name",)

    @property
    def tags_set(self):
        if not self.tags:
            return set()

        return set(tag for tag in self.tags.splitlines() if tag.strip())

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
    help = models.TextField(blank=True, null=True)
    tags = models.TextField(blank=True, null=True)
    user_defined_type = models.CharField(max_length=50, null=True, default=None)

    @property
    def user_defined_type_display(self):
        from .conf import USER_DEFINED_TYPES_NAME

        if not self.user_defined_type:
            return "---"

        if self.user_defined_type in USER_DEFINED_TYPES_NAME:
            return USER_DEFINED_TYPES_NAME[self.user_defined_type]

        return f"{self.user_defined_type} (unknown)"

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

            if (
                next_obj.value != obj.value
                or next_obj.was_changed != obj.was_changed
                or next_obj.tags != obj.tags
                or next_obj.help != obj.help
                or next_obj.user_defined_type != obj.user_defined_type
            ):
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
