import json
from django.core.management.base import BaseCommand
from content_settings.models import ContentSetting
from content_settings.export import export_to_format


class Command(BaseCommand):
    help = "Export selected content settings (by name) or all content settings into JSON format."

    def add_arguments(self, parser):
        parser.add_argument(
            "--names",
            nargs="+",
            type=str,
            help="Names of the content settings to export. If not provided, all content settings will be exported.",
        )

    def handle(self, *args, **options):
        names = options["names"]
        if names:
            content_settings = ContentSetting.objects.filter(name__in=names)
        else:
            content_settings = ContentSetting.objects.all()

        json_data = export_to_format(content_settings)

        self.stdout.write(json_data)
