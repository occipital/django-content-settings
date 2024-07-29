# Generated by Django 4.2.13 on 2024-07-29 10:46

from django.conf import settings
import django.core.validators
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):
    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("content_settings", "0003_user_preview"),
    ]

    operations = [
        migrations.AddField(
            model_name="userpreview",
            name="from_help",
            field=models.TextField(null=True, verbose_name="From Help"),
        ),
        migrations.AddField(
            model_name="userpreview",
            name="from_tags",
            field=models.TextField(null=True, verbose_name="From Tags"),
        ),
        migrations.AddField(
            model_name="userpreview",
            name="from_user_defined_type",
            field=models.CharField(
                max_length=50, null=True, verbose_name="From User Defined Type"
            ),
        ),
        migrations.AddField(
            model_name="userpreview",
            name="help",
            field=models.TextField(null=True, verbose_name="Help"),
        ),
        migrations.AddField(
            model_name="userpreview",
            name="tags",
            field=models.TextField(null=True, verbose_name="Tags"),
        ),
        migrations.AddField(
            model_name="userpreview",
            name="user_defined_type",
            field=models.CharField(
                max_length=50, null=True, verbose_name="User Defined Type"
            ),
        ),
        migrations.AddField(
            model_name="userpreviewhistory",
            name="help",
            field=models.TextField(null=True),
        ),
        migrations.AddField(
            model_name="userpreviewhistory",
            name="tags",
            field=models.TextField(null=True),
        ),
        migrations.AddField(
            model_name="userpreviewhistory",
            name="user_defined_type",
            field=models.CharField(max_length=50, null=True),
        ),
        migrations.AlterField(
            model_name="contentsetting",
            name="help",
            field=models.TextField(blank=True, null=True, verbose_name="Help"),
        ),
        migrations.AlterField(
            model_name="contentsetting",
            name="name",
            field=models.CharField(
                max_length=200,
                unique=True,
                validators=[
                    django.core.validators.RegexValidator(
                        message="Value must be uppercase, can include numbers and underscores, and cannot start with a number.",
                        regex="^[A-Z][A-Z0-9_]*$",
                    )
                ],
                verbose_name="Name",
            ),
        ),
        migrations.AlterField(
            model_name="contentsetting",
            name="tags",
            field=models.TextField(blank=True, null=True, verbose_name="Tags"),
        ),
        migrations.AlterField(
            model_name="contentsetting",
            name="user_defined_type",
            field=models.CharField(
                db_index=True,
                default=None,
                max_length=50,
                null=True,
                verbose_name="User Defined Type",
            ),
        ),
        migrations.AlterField(
            model_name="contentsetting",
            name="value",
            field=models.TextField(blank=True, verbose_name="Value"),
        ),
        migrations.AlterField(
            model_name="contentsetting",
            name="version",
            field=models.CharField(max_length=50, null=True, verbose_name="Version"),
        ),
        migrations.AlterField(
            model_name="historycontentsetting",
            name="by_user",
            field=models.BooleanField(
                choices=[(True, "by user"), (False, "by app"), (None, "unknown")],
                default=None,
                null=True,
                verbose_name="By User",
            ),
        ),
        migrations.AlterField(
            model_name="historycontentsetting",
            name="created_on",
            field=models.DateTimeField(
                default=django.utils.timezone.now, verbose_name="Created On"
            ),
        ),
        migrations.AlterField(
            model_name="historycontentsetting",
            name="help",
            field=models.TextField(blank=True, null=True, verbose_name="Help"),
        ),
        migrations.AlterField(
            model_name="historycontentsetting",
            name="name",
            field=models.CharField(max_length=200, verbose_name="Name"),
        ),
        migrations.AlterField(
            model_name="historycontentsetting",
            name="tags",
            field=models.TextField(blank=True, null=True, verbose_name="Tags"),
        ),
        migrations.AlterField(
            model_name="historycontentsetting",
            name="user",
            field=models.ForeignKey(
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                to=settings.AUTH_USER_MODEL,
                verbose_name="User",
            ),
        ),
        migrations.AlterField(
            model_name="historycontentsetting",
            name="user_defined_type",
            field=models.CharField(
                default=None, max_length=50, null=True, verbose_name="User Defined Type"
            ),
        ),
        migrations.AlterField(
            model_name="historycontentsetting",
            name="value",
            field=models.TextField(blank=True, null=True, verbose_name="Value"),
        ),
        migrations.AlterField(
            model_name="historycontentsetting",
            name="version",
            field=models.CharField(max_length=50, null=True, verbose_name="Version"),
        ),
        migrations.AlterField(
            model_name="historycontentsetting",
            name="was_changed",
            field=models.BooleanField(
                choices=[(True, "Changed"), (False, "Added"), (None, "Removed")],
                default=True,
                null=True,
                verbose_name="Was Changed",
            ),
        ),
        migrations.AlterField(
            model_name="userpreview",
            name="from_value",
            field=models.TextField(null=True, verbose_name="From Value"),
        ),
        migrations.AlterField(
            model_name="userpreview",
            name="name",
            field=models.CharField(max_length=200, verbose_name="Name"),
        ),
        migrations.AlterField(
            model_name="userpreview",
            name="user",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                to=settings.AUTH_USER_MODEL,
                verbose_name="User",
            ),
        ),
        migrations.AlterField(
            model_name="userpreview",
            name="value",
            field=models.TextField(verbose_name="Value"),
        ),
        migrations.AlterField(
            model_name="usertagsetting",
            name="name",
            field=models.CharField(max_length=200, verbose_name="Name"),
        ),
        migrations.AlterField(
            model_name="usertagsetting",
            name="tag",
            field=models.TextField(verbose_name="Tag"),
        ),
        migrations.AlterField(
            model_name="usertagsetting",
            name="user",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                to=settings.AUTH_USER_MODEL,
                verbose_name="User",
            ),
        ),
        migrations.AddIndex(
            model_name="historycontentsetting",
            index=models.Index(
                fields=["created_on", "user_id", "by_user"], name="static_batch_idx"
            ),
        ),
    ]