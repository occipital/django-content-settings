# Generated by Django 4.2.9 on 2024-01-16 11:35

from django.db import migrations, models
import django.core.validators


class Migration(migrations.Migration):
    dependencies = [
        ("content_settings", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="contentsetting",
            name="help",
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name="contentsetting",
            name="tags",
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name="contentsetting",
            name="user_defined_type",
            field=models.CharField(
                db_index=True, default=None, max_length=50, null=True
            ),
        ),
        migrations.AddField(
            model_name="historycontentsetting",
            name="help",
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name="historycontentsetting",
            name="tags",
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name="historycontentsetting",
            name="user_defined_type",
            field=models.CharField(default=None, max_length=50, null=True),
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
            ),
        ),
    ]
