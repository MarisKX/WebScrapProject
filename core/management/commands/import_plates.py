import json
from django.core.management.base import BaseCommand
from core.models import UncheckedPlates  # Replace with your actual app/model


class Command(BaseCommand):
    help = "Import license plates from a JSON file and add them to UncheckedPlates"

    def add_arguments(self, parser):
        parser.add_argument(
            "--input",
            type=str,
            required=True,
            help="Input JSON file with license plates",
        )

    def handle(self, *args, **options):
        input_file = options["input"]

        # Load the JSON file
        with open(input_file, "r", encoding="utf-8") as file:
            plates = json.load(file)

        # Add plates to UncheckedPlates model
        for plate in plates:
            UncheckedPlates.objects.get_or_create(plate=plate)

        self.stdout.write(
            self.style.SUCCESS(
                f"Imported {len(plates)} license plates from {input_file}"
            )
        )
