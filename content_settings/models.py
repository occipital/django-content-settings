from collections import defaultdict

from django.db import models
from django.core.validators import RegexValidator
from django.utils import timezone
from django.conf import settings
from django.utils.translation import gettext_lazy as _


class ContentSetting(models.Model):
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
        if not self.tags:
            return set()

        return set(tag for tag in self.tags.splitlines() if tag.strip())

    def __str__(self):
        return self.name


class HistoryContentSetting(models.Model):
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
    def user_record(cls, user, preview_setting, status=STATUS_CREATED):
        return cls.objects.create(
            user=user,
            name=preview_setting.name,
            value=preview_setting.value,
            status=status,
        )

    def __str__(self):
        return f"{self.user} - {self.name}"
