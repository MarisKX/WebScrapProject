from django.utils.timezone import now
from datetime import date, timedelta
from django.core.management.base import BaseCommand
from core.models import RecheckForAPKPlates
from vehicles.models import Vehicle

# Terminal color import
from colorama import Fore, Back, Style, init


class Command(BaseCommand):
    help = "Import license plates from a JSON file and add them to UncheckedPlates"

    def handle(self, *args, **options):

        print(Fore.GREEN + "Command executed!" + Style.RESET_ALL)
        # Get the current year and calculate the cutoff year (50 years ago)
        current_year = date.today().year
        cutoff_year = current_year - 50
        yesterday = date.today() - timedelta(days=1)
        one_hour_ago = date.now() - timedelta(days=2)
        print(Fore.GREEN + f"Current Year: {current_year}" + Style.RESET_ALL)
        print(Fore.GREEN + f"Check cars no older than: {cutoff_year}" + Style.RESET_ALL)
        print(Fore.GREEN + f"Yeasterday was: {yesterday}" + Style.RESET_ALL)

        expired_vehicles = Vehicle.objects.filter(
            vehicle_category__name="personenauto",  # Include only personenauto category
            exported=False,  # Exclude exported vehicles
            first_reg__year__gte=cutoff_year,  # Include vehicles registered in 1975 or later
            apk__isnull=False,  # Exclude vehicles with no APK date
            apk__lte=yesterday,  # Include vehicles with APK expiry on or before yesterday
            archived=False,  # Exclude archived vehicles
        ).exclude(
            last_updated__gte=one_hour_ago  # Exclude vehicles updated in the last 1 hour
        )

        for vehicle in expired_vehicles:
            print(
                f"License Plate: {vehicle.licence_plate}, , Vehicle: {vehicle.display_name}, "
                f"First Reg: {vehicle.first_reg}, APK Expiry: {vehicle.apk}, Last Updated: {vehicle.last_updated}"
            )
            vehicle_instance, vehicle_created = (
                RecheckForAPKPlates.objects.get_or_create(
                    plate=vehicle.licence_plate,
                    vehicle=vehicle.display_name,
                    first_reg=vehicle.first_reg,
                    apk=vehicle.apk,
                )
            )
        print(expired_vehicles.count())
