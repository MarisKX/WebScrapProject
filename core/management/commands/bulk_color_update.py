from django.core.management.base import BaseCommand
from vehicles.models import Vehicle, Color


class Command(BaseCommand):
    help = "Bulk update vehicles to set default color if not assigned"

    def handle(self, *args, **kwargs):
        # Fetch all vehicles
        vehicles = Vehicle.objects.all()

        # Get or create the default color instance
        default_color, _ = Color.objects.get_or_create(display_name="-")

        # Update color for vehicles where it is None
        for vehicle in vehicles:
            if vehicle.color is None:
                vehicle.color = default_color

        # Bulk update the vehicles in a single query
        Vehicle.objects.bulk_update(vehicles, ["color"])

        self.stdout.write(f"Updated {len(vehicles)} vehicles to have a default color.")
