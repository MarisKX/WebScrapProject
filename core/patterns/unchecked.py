from core.models import UncheckedPlates


def generate_license_plates_unchecked():
    """
    Generator to yield unchecked license plates.
    """
    for plate in UncheckedPlates.objects.values_list("plate", flat=True):
        yield plate
