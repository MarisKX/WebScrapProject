from core.models import RecheckForAPKPlates


def generate_license_plates_from_db_for_APK_check():
    """
    Generator to yield license plates from the Car model.
    """
    for vehicle in RecheckForAPKPlates.objects.values_list("plate", flat=True):
        yield vehicle
