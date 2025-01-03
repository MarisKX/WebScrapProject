def generate_license_plate_xx_99_99():
    """Generate license plates with the AA0000 pattern."""
    for letter1 in range(ord("A"), ord("Z") + 1):
        for letter2 in range(ord("A"), ord("Z") + 1):
            for digit1 in range(10):
                for digit2 in range(10):
                    for digit3 in range(10):
                        for digit4 in range(10):
                            yield f"{chr(letter1)}{chr(letter2)}{digit1}{digit2}{digit3}{digit4}"
