# Generated by Django 4.2.9 on 2024-01-16 11:35

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("content_settings", "0001_initial"),
    ]

    operations = [
        migrations.RenameIndex(
            model_name="historycontentsetting",
            new_name="content_set_name_86a215_idx",
            old_name="static_cont_name_d40020_idx",
        ),
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
            name="id",
            field=models.BigAutoField(
                auto_created=True, primary_key=True, serialize=False, verbose_name="ID"
            ),
        ),
        migrations.AlterField(
            model_name="historycontentsetting",
            name="id",
            field=models.BigAutoField(
                auto_created=True, primary_key=True, serialize=False, verbose_name="ID"
            ),
        ),
        migrations.AlterField(
            model_name="usertagsetting",
            name="id",
            field=models.BigAutoField(
                auto_created=True, primary_key=True, serialize=False, verbose_name="ID"
            ),
        ),
    ]
