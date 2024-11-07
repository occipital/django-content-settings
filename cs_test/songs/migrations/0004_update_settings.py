# Generated by Django 4.2.16 on 2024-10-16 18:22

from django.db import migrations
from content_settings.migrate import RunImport


class Migration(migrations.Migration):
    dependencies = [
        ("songs", "0003_admin"),
    ]

    operations = [
        RunImport(
            {
                "settings": {
                    "AFTER_TITLE": {"value": "Best Settings Framework", "version": ""},
                    "ARTIST_LINE": {"value": "The Line", "version": ""},
                    "DAYS_WITHOUT_FAIL": {"value": "8", "version": ""},
                    "DJANGO_TEMPLATE": {"value": "Hi Man", "version": ""},
                }
            }
        )
    ]