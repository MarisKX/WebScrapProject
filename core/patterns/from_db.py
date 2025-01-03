from vehicles.models import Vehicle


def generate_license_plates_from_db():
    """
    Generator to yield license plates from the Vehicle model
    where the vehicle_category.name is 'undefined'.
    """
    vehicles = Vehicle.objects.filter(
        vehicle_category__name="undefined"  # Filter by related field
    ).values_list(
        "licence_plate", flat=True
    )  # Only get licence_plate field

    for licence_plate in vehicles:
        yield licence_plate
