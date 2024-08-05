import argparse
import json
from django.core.management.base import BaseCommand
from content_settings.export import preview_data, import_to
from django.contrib.auth import get_user_model

User = get_user_model()


class Command(BaseCommand):
    help = "Import content settings from a JSON file."

    def add_arguments(self, parser):
        parser.add_argument(
            "filename",
            type=str,
            help="Path to the JSON file containing content settings.",
        )
        parser.add_argument(
            "--import",
            action="store_true",
            default=False,
            help="Apply the import if set, otherwise just preview.",
        )
        parser.add_argument(
            "--preview-for",
            type=str,
            default=None,
            help="Import as a preview for a specific user.",
        )
        parser.add_argument(
            "--names",
            nargs="+",
            type=str,
            help="Names of specific content settings to import.",
        )

        parser.add_argument(
            "--show-skipped",
            action="store_true",
            default=False,
            help="Show skipped settings.",
        )
        parser.add_argument(
            "--show-only-errors",
            action="store_true",
            default=False,
            help="Show only errors.",
        )

    def handle(self, *args, **options):
        filename = options["filename"]
        do_import = options["import"]
        preview_for = options["preview_for"]
        names = options["names"]
        show_skipped = options["show_skipped"]
        show_only_errors = options["show_only_errors"]

        with open(filename, "r") as file:
            data = json.load(file)

        if preview_for:
            preview_for = User.objects.get(username=preview_for)

        errors, applied, skipped = preview_data(data, preview_for)

        if skipped and show_skipped and not show_only_errors:
            self.stdout.write("Skipped:")
            self.stdout.write(json.dumps(skipped, indent=2))

        if errors:
            self.stderr.write("Errors:")
            self.stderr.write(json.dumps(errors, indent=2))

        if applied and not show_only_errors:
            self.stdout.write("Applied:")
            self.stdout.write(json.dumps(applied, indent=2))

        if do_import or preview_for:
            if names:
                applied = [row for row in applied if row["name"] in names]

            import_to(data, applied, preview_for is not None, preview_for)

            if preview_for:
                self.stdout.write(
                    self.style.SUCCESS(
                        "Preview saved for user %s" % preview_for.username
                    )
                )
            else:
                self.stdout.write(self.style.SUCCESS("Import completed."))
