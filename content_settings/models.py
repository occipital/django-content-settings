"""
Django Models for the content settings.
"""

from collections import defaultdict

from django.db import models
from django.core.validators import RegexValidator
from django.utils import timezone
from django.conf import settings
from django.utils.translation import gettext_lazy as _
from django.contrib.auth import get_user_model
from typing import Optional

User = get_user_model()


class ContentSetting(models.Model):
    """
    The main model for the content settings. Is stores all of the raw values for the content settings.
    """

    id = models.AutoField(primary_key=True, verbose_name=_("ID"))
    name = models.CharField(
        max_length=200,
        unique=True,
        validators=[
            RegexValidator(
                regex=r"^[A-Z][A-Z0-9_]*$",
                message=_(
                    "Value must be uppercase, can include numbers and underscores, and cannot start with a number."
                ),
            ),
        ],
        verbose_name=_("Name"),
    )
    value = models.TextField(blank=True, verbose_name=_("Value"))
    version = models.CharField(max_length=50, null=True, verbose_name=_("Version"))
    help = models.TextField(blank=True, null=True, verbose_name=_("Help"))
    tags = models.TextField(blank=True, null=True, verbose_name=_("Tags"))
    user_defined_type = models.CharField(
        max_length=50,
        null=True,
        default=None,
        db_index=True,
        verbose_name=_("User Defined Type"),
    )

    class Meta:
        ordering = ("name",)
        permissions = [
            ("can_preview_on_site", _("Can preview on site")),
        ]

    @property
    def tags_set(self):
        """
        tags field stores tags in a newline separated format. The property returns a set of tags.
        """
        if not self.tags:
            return set()

        return set(tag for tag in self.tags.splitlines() if tag.strip())

    def __str__(self):
        return self.name


class HistoryContentSetting(models.Model):
    """
    The model for the history of the content settings. Is used to store the history of changes for the content settings such as changed/added/removed.

    The the generation of the history is done in two steps.
    First step is to create a record when the setting is changed.
    Second step is to assign other changing parameters such as by_user.
    """

    CHANGED_CHOICES = (
        (True, _("Changed")),
        (False, _("Added")),
        (None, _("Removed")),
    )
    BY_USER_CHOICES = (
        (True, _("by user")),
        (False, _("by app")),
        (None, _("unknown")),
    )

    id = models.AutoField(primary_key=True, verbose_name=_("ID"))
    created_on = models.DateTimeField(
        null=False, default=timezone.now, verbose_name=_("Created On")
    )

    name = models.CharField(max_length=200, verbose_name=_("Name"))
    value = models.TextField(blank=True, null=True, verbose_name=_("Value"))
    version = models.CharField(max_length=50, null=True, verbose_name=_("Version"))

    was_changed = models.BooleanField(
        null=True, default=True, choices=CHANGED_CHOICES, verbose_name=_("Was Changed")
    )
    by_user = models.BooleanField(
        null=True, default=None, choices=BY_USER_CHOICES, verbose_name=_("By User")
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        verbose_name=_("User"),
    )
    help = models.TextField(blank=True, null=True, verbose_name=_("Help"))
    tags = models.TextField(blank=True, null=True, verbose_name=_("Tags"))
    user_defined_type = models.CharField(
        max_length=50, null=True, default=None, verbose_name=_("User Defined Type")
    )

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
            models.Index(fields=["name", "-id"], name="static_cont_name_d40020_idx"),
        ]

    @classmethod
    def update_last_record_for_name(cls, name: str, user: Optional[User] = None):
        """
        Update the last record with the information about the source of the update.
        """
        last_setting = cls.objects.filter(name=name).first()
        if not last_setting or last_setting.by_user is not None:
            return

        last_setting.user = user
        last_setting.by_user = user is not None
        last_setting.save()

    @classmethod
    def gen_unique_records(cls, name):
        """
        The current issue is that sometimes the same setting is changed multiple times in a row.
        This method is used to generate unique records for the history.
        """
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
    """
    User can assign personal tags to the settings for extending tags-filtering functionality.
    The model contains those assignees.

    The allowed tags to assign in Django Admin panel can be found in `CONTENT_SETTINGS_USER_TAGS` django setting.
    """

    id = models.AutoField(primary_key=True, verbose_name=_("ID"))
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, verbose_name=_("User")
    )
    name = models.CharField(max_length=200, verbose_name=_("Name"))
    tag = models.TextField(verbose_name=_("Tag"))

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


class UserPreview(models.Model):
    """
    The user is allowed to preview settings before applying.

    The model contains the information of which settings are currently previewing.
    """

    id = models.AutoField(primary_key=True, verbose_name=_("ID"))
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, verbose_name=_("User")
    )
    name = models.CharField(max_length=200, verbose_name=_("Name"))
    from_value = models.TextField(verbose_name=_("From Value"))
    value = models.TextField(verbose_name=_("Value"))

    class Meta:
        unique_together = (("user", "name"),)

    def __str__(self):
        return f"{self.user} - {self.name}"


class UserPreviewHistory(models.Model):
    """
    Contains history of the user's preview settings. Because the settings can also change logic, so we want to keep the history of the settings for future investigations.
    """

    STATUS_CREATED = 0
    STATUS_APPLIED = 10
    STATUS_REMOVED = 20
    STATUS_IGNORED = 30

    id = models.AutoField(primary_key=True, verbose_name=_("ID"))
    created_on = models.DateTimeField(null=False, default=timezone.now)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

    name = models.CharField(max_length=200)
    value = models.TextField(null=True)
    status = models.IntegerField(
        default=STATUS_CREATED,
        choices=(
            (STATUS_CREATED, _("Created")),
            (STATUS_APPLIED, _("Applied")),
            (STATUS_REMOVED, _("Removed")),
            (STATUS_IGNORED, _("Ignored")),
        ),
    )

    @classmethod
    def user_record(
        cls, user: User, preview_setting: UserPreview, status: int = STATUS_CREATED
    ):
        """
        Making a record in the history of the user's preview settings.
        """
        return cls.objects.create(
            user=user,
            name=preview_setting.name,
            value=preview_setting.value,
            status=status,
        )

    @classmethod
    def user_record_by_name(
        cls, user: User, name: str, value: str, status: int = STATUS_CREATED
    ):
        """
        Making a record in the history of the user's preview settings by the name of the setting and the value.
        """
        return cls.objects.create(
            user=user,
            name=name,
            value=value,
            status=status,
        )

    def __str__(self):
        return f"{self.user} - {self.name}"
