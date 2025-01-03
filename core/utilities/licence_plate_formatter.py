import re

# Terminal color import
from colorama import Fore, Style

plate_format_rules = {
    r"([A-Z]{2})(\d{2})(\d{2})": r"\1-\2-\3",  # XX9999 -> XX-99-99
    r"(\d{2})([A-Z]{2})(\d{2})": r"\1-\2-\3",  # 99XX99 -> 99-XX-99
    r"(\d{2})([A-Z]{2})([A-Z]{2})": r"\1-\2-\3",  # 99XXXX -> 99-XX-XX
    r"(\d{2})(\d{2})([A-Z]{2})": r"\1-\2-\3",  # 9999XX -> 99-99-XX
    r"([A-Z]{2})(\d{2})([A-Z]{2})": r"\1-\2-\3",  # XX99XX -> XX-99-XX
    r"(\d{2})([A-Z]{3})(\d{1})": r"\1-\2-\3",  # 99XXX9 -> 99-XXX-9
    r"(\d{1})([A-Z]{3})(\d{2})": r"\1-\2-\3",  # 9XXX99 -> 9-XXX-99
    r"([A-Z]{3})(\d{2})([A-Z]{1})": r"\1-\2-\3",  # XXX99X -> XXX-99-X
    r"([A-Z]{1})(\d{3})([A-Z]{2})": r"\1-\2-\3",  # XXX99X -> X-999-XX
}


def format_license_plate(plate):
    """
    Format a raw license plate based on known patterns.

    Args:
        plate (str): The raw license plate.

    Returns:
        str: The formatted license plate, or the original if no pattern matches.
    """
    for pattern, replacement in plate_format_rules.items():
        if re.fullmatch(pattern, plate):  # Match the full plate
            return re.sub(pattern, replacement, plate)
    print(f"{Fore.RED}Unknown format: {plate}{Style.RESET_ALL}")
    return plate  # Return as-is if no pattern matches
