from django.core.management.base import BaseCommand
from core.models import UncheckedPlates
from vehicles.models import Vehicle


class Command(BaseCommand):
    help = "Check and remove license plates from UncheckedPlates if they already exist in the Vehicle database."

    def handle(self, *args, **options):
        # Get all unchecked plates
        unchecked_plates = UncheckedPlates.objects.values_list("plate", flat=True)

        # Track removed plates for reporting
        removed_count = 0

        for plate in unchecked_plates:
            # Check if the plate exists in the Vehicle database
            if Vehicle.objects.filter(licence_plate=plate).exists():
                # Delete the plate from UncheckedPlates
                UncheckedPlates.objects.filter(plate=plate).delete()
                removed_count += 1
                print(f"Removed plate: {plate}")

        # Print the summary
        print(f"Total plates checked: {len(unchecked_plates)}")
        print(f"Total plates removed: {removed_count}")
        print(f"Plates left in UncheckedPlates: {UncheckedPlates.objects.count()}")
