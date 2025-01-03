def generate_license_plate_99_xxx_9():
    """Generate sequential license plates with the 99XXX9 pattern."""

    # Letters and patterns to exclude
    excluded_letters = {
        "A",
        "C",
        "E",
        "I",
        "M",
        "O",
        "Q",
        "U",
        "W",
        "Y",
    }
    excluded_patterns = {
        "SS",
        "SD",
    }

    # Iterate through the components of the license plate
    for digit1 in range(10):
        for digit2 in range(10):
            for letter1 in range(ord("A"), ord("Z") + 1):
                for letter2 in range(ord("A"), ord("Z") + 1):
                    for letter3 in range(ord("A"), ord("Z") + 1):
                        for digit3 in range(10):
                            # Convert letters to characters
                            char1, char2, char3 = (
                                chr(letter1),
                                chr(letter2),
                                chr(letter3),
                            )

                            # Skip excluded letters
                            if (
                                char1 in excluded_letters
                                or char2 in excluded_letters
                                or char3 in excluded_letters
                            ):
                                continue

                            # Skip excluded patterns
                            if (
                                f"{char1}{char2}" in excluded_patterns
                                or f"{char2}{char3}" in excluded_patterns
                            ):
                                continue

                            # Generate the license plate
                            yield f"{digit1}{digit2}{char1}{char2}{char3}{digit3}"
