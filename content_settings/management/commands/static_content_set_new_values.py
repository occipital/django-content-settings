import argparse

from django.core.management.base import BaseCommand
from django.db import transaction


from content_settings.conf import set_initial_values_for_db


class Command(BaseCommand):
    help = "Create new records and remove unused settings for content settings"

    def add_arguments(self, parser):
        parser.add_argument(
            "--apply", action="store_true", default=False, help="Apply "
        )

    def handle(self, *args, **options):
        with transaction.atomic():
            log = set_initial_values_for_db(apply=options.get("apply"))
            if not log:
                print("No Static Content Settings Updated")
                return

            for l in log:
                print(" ".join(l))

            print("Applied!" if options.get("apply") else "Ignored")
