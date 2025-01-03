# General imports
import time as t

# Django Imports
from django.core.management.base import BaseCommand

# Terminal color import
from colorama import Fore, Back, Style, init

# Selenium Imports
from selenium import webdriver
from selenium.webdriver.common.by import By

# Custom models import
from core.models import LastPlateIssued  # Replace with your actual app/model


def cleaning_plate(plate):
    clean_plate = plate.replace("-", "")
    return clean_plate


def determine_license_plate_pattern(plate):
    """
    Determine the pattern of a license plate.

    Args:
        plate (str): The license plate string (e.g., "HBH12H", "GP25KL").

    Returns:
        str: The pattern of the license plate (e.g., "XXX99X", "XX99XX").
    """
    pattern = ""
    for char in plate:
        if char.isalpha():  # Check if the character is a letter
            pattern += "X"
        elif char.isdigit():  # Check if the character is a digit
            pattern += "9"
    return pattern


class Command(BaseCommand):
    help = "Get latest issued plate from RDW database"

    def handle(self, *args, **options):
        # Init steps start
        print(Fore.GREEN + "Command executed!" + Style.RESET_ALL)
        print(Fore.YELLOW + "Opening browser..." + Style.RESET_ALL)
        driver = webdriver.Chrome()
        # driver = webdriver.Chrome()
        driver.get("https://www.rdw.nl/")
        print(Fore.GREEN + "Browser open" + Style.RESET_ALL)
        t.sleep(4)
        try:
            last_plate_raw = driver.find_element(
                By.XPATH,
                "//section[@data-luk-service-uri='/api/rdw/licenseplate/lastissued/v1/get']//span[@class='kenteken__code']",
            ).text
            print("Last Plate (content): " + last_plate_raw)
            last_plate = cleaning_plate(last_plate_raw)
            pattern = determine_license_plate_pattern(last_plate)
            print(last_plate)
            print(pattern)

            plate_instance, plate_created = LastPlateIssued.objects.get_or_create(
                pattern=pattern,
                plate=last_plate,
            )
            if plate_created:
                print("Plate created: " + plate_instance.plate)
                print("Pattern: " + plate_instance.pattern)
            else:
                print("Save failed")
        except Exception as e:
            print(f"Error occurred: {e}")
        finally:
            if driver:
                driver.quit()  # Ensure the browser is closed
                print("Browser closed!")
