def generate_license_plate_xxx_99_x():
    """Generate sequential license plates with the XXX-99-X pattern."""

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
    for letter1 in range(ord("A"), ord("Z") + 1):
        for letter2 in range(ord("A"), ord("Z") + 1):
            for letter3 in range(ord("A"), ord("Z") + 1):
                # Skip excluded letters in the main block
                if (
                    chr(letter1) in excluded_letters
                    or chr(letter2) in excluded_letters
                    or chr(letter3) in excluded_letters
                ):
                    continue

                for letter4 in range(ord("A"), ord("Z") + 1):
                    # Skip excluded letters for the last character
                    char4 = chr(letter4)
                    if char4 in excluded_letters:
                        continue

                    # Skip excluded patterns
                    if (
                        f"{chr(letter1)}{chr(letter2)}" in excluded_patterns
                        or f"{chr(letter2)}{chr(letter3)}" in excluded_patterns
                        or f"{chr(letter3)}{char4}" in excluded_patterns
                    ):
                        continue

                    for digit1 in range(10):
                        for digit2 in range(10):
                            # Convert letters to characters
                            char1, char2, char3 = (
                                chr(letter1),
                                chr(letter2),
                                chr(letter3),
                            )

                            # Generate the license plate
                            yield f"{char1}{char2}{char3}{digit1}{digit2}{char4}"
