def generate_license_plate_99_xx_xx():
    """Generate license plates with the XX9999 pattern."""

    # Add individual letters to exclude
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
    }
    # Add specific patterns to exclude
    excluded_patterns = {
        "SS",
        "SD",
    }

    for digit1 in range(10):
        for digit2 in range(10):
            for letter1 in range(ord("A"), ord("Z") + 1):
                for letter2 in range(ord("A"), ord("Z") + 1):
                    for letter3 in range(ord("A"), ord("Z") + 1):
                        for letter4 in range(ord("A"), ord("Z") + 1):
                            char1, char2, char3, char4 = (
                                chr(letter1),
                                chr(letter2),
                                chr(letter3),
                                chr(letter4),
                            )
                            if (
                                char1 in excluded_letters
                                or char2 in excluded_letters
                                or char3 in excluded_letters
                                or char4 in excluded_letters
                            ):
                                continue
                            # Skip plates with excluded patterns
                            if f"{char1}{char2}" in excluded_patterns:
                                continue
                            if f"{char3}{char4}" in excluded_patterns:
                                continue
                            yield f"{digit1}{digit2}{char1}{char2}{char3}{char4}"  # noqa
