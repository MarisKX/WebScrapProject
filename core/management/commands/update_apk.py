# Python imports
import time as t
import random as r
import locale
from datetime import datetime, date
import itertools

# Django Imports
from django.core.management.base import BaseCommand
from django.utils.timezone import now
from django.shortcuts import get_object_or_404
from django.http import Http404

# Selenium Imports
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException

# Terminal color import
from colorama import Fore, Back, Style, init

"""
Pattern and Utility Imports
"""
# APK pattern
from core.patterns.pattern_apk import generate_license_plates_from_db_for_APK_check


# Data Clearning and Utilities Imports
from core.utilities.random_pause import random_pause
from core.utilities.licence_plate_formatter import format_license_plate as formatted
from core.utilities.get_table_element import get_element_text_by_label as get_text
from core.utilities.get_date import get_date as get_date

# Custom models imports
from vehicles.models import (
    Vehicle,
)
from core.models import (
    LastPlatechecked,
    UncheckedPlates,
    RecheckForAPKPlates,
)


locale.setlocale(locale.LC_TIME, "Dutch_Netherlands.1252")
init(autoreset=True)


class Command(BaseCommand):
    help = "Scrape car data from RDW and save to database"

    def add_arguments(self, parser):
        """Add custom arguments to the command."""
        parser.add_argument(
            "--chunk-size",
            type=int,
            default=5,
            help="Number of license plates to process in each chunk",
        )
        parser.add_argument(
            "--pattern",
            type=str,
            default=None,
            help="Pattern to check for license plates",
        )

    def chunked_generator(self, generator, chunk_size):
        """Split generator into chunks of given size."""
        iterator = iter(generator)
        for first in iterator:
            yield itertools.chain([first], itertools.islice(iterator, chunk_size - 1))

    # Save and get last plate, skip plate function
    def save_last_plate(self, plate, pattern):
        """Save the last checked plate to the database."""
        last_plate, created = LastPlatechecked.objects.get_or_create(pattern=pattern)
        last_plate.plate = plate
        last_plate.save()
        print(f"Saved last checked plate: {formatted(plate)}")

    def get_last_plate(self, pattern):
        """Retrieve the most recently checked plate from the database."""
        if pattern:
            last_plate = LastPlatechecked.objects.filter(pattern=pattern).first()
            return last_plate.plate if last_plate else None
        return None

    def skip_to_last_plate(self, generator, last_plate):
        """Skip the generator to the plate after the last processed plate."""
        skip = True
        for plate in generator:
            if skip and plate == last_plate:
                skip = False  # Stop skipping once we reach the last plate
                continue  # Skip the last plate itself
            if not skip:
                yield plate

    def try_to_find_element(self, driver, by, value, max_retries=3):

        max_retries = int(max_retries)
        attempt = 0
        while attempt < max_retries:
            try:
                element = driver.find_element(by, value)
                print(f"Element found on attempt {attempt + 1}")
                return element
            except NoSuchElementException:
                attempt += 1
                print(f"Attempt {attempt} failed. Refreshing the page...")
                t.sleep(5)
                driver.refresh()
        raise Exception(
            f"Licence plate field not found after {max_retries} attempts."
        )  # noqa

    def scrape_license_plate(self, driver, plate):
        """Scrape RDW data for a given license plate."""

        try:
            vehicle_object = get_object_or_404(Vehicle, licence_plate=plate)
        except Http404:
            print(f"icense plate {plate} not found in the database.")
            plate_instance, plate_created = UncheckedPlates.objects.get_or_create(
                plate=plate,
            )
            if plate_created:
                print(f"Adding plate {plate_instance.plate} to check it later...")
            t.sleep(10)
            return

        # Fill in the license plate
        driver.get("https://ovi.rdw.nl/")
        kenteken_input = self.try_to_find_element(
            driver=driver, by=By.ID, value="kenteken", max_retries=3
        )
        kenteken_input.clear()

        kenteken_input.send_keys(plate)
        t.sleep(1)

        # Click the search button
        search_btn = driver.find_element(By.CLASS_NAME, "icon-search")
        search_btn.click()
        t.sleep(5)

        try:

            """
            Expand history dropdown
            Vervaldata en historie
            """
            expand_vervaldata_en_historie = driver.find_element(
                By.ID,
                "acc-overzicht-verval-historie-toggle",
            )
            expand_vervaldata_en_historie.click()
            t.sleep(2)

            # First Reg
            first_reg_raw = get_text(driver, "Datum eerste toelating")
            first_reg = get_date(first_reg_raw)

            # First Reg in NL
            first_reg_in_NL_raw = get_text(
                driver, "Datum eerste tenaamstelling in Nederland"
            )
            first_reg_in_NL = get_date(first_reg_in_NL_raw)

            # Imported in NL / assigned licence plate
            imported_in_NL_raw = get_text(
                driver, "Datum inschrijving voertuig in Nederland"
            )
            imported_in_NL = get_date(imported_in_NL_raw)

            # APK
            apk_raw = get_text(driver, "Vervaldatum APK")
            apk = get_date(apk_raw)

            """
            Expand status dropdown
            Status van het voertuig
            """
            expand_overzicht_status = driver.find_element(
                By.ID,
                "acc-overzicht-status-toggle",
            )
            expand_overzicht_status.click()
            t.sleep(2)

            exported_raw = get_text(driver, "Geëxporteerd")
            if exported_raw == "Nee":
                exported = False
            else:
                exported = True

            # Insurance
            insurance_raw = get_text(driver, "WAM-verzekerd")
            if insurance_raw == "Nee":
                insurance = False
            else:
                insurance = True

            # Print all data
            print(
                f"{Fore.GREEN}Licence Plate: {formatted(plate)}, Make and Model: {vehicle_object.display_name}, First Reg: {first_reg}, APK: {apk}, Last_update: {vehicle_object.last_updated}{Style.RESET_ALL}"  # noqa
            )

            # Check if APK has changed
            if vehicle_object.apk != apk and apk:
                print(
                    f"{Fore.GREEN}APK has changed for licence plate {Style.RESET_ALL}{Back.YELLOW}{formatted(plate)}{Style.RESET_ALL}{Fore.GREEN} from {vehicle_object.apk} to {Style.RESET_ALL}{Fore.WHITE}{Back.BLUE}{apk}{Style.RESET_ALL}"
                )
                self.updated_count += 1
            else:
                print(f"{Fore.RED}APK has not changed{Style.RESET_ALL}")
                self.no_changes_count += 1

            # Check if the APK date is in the future
            if apk and apk > date.today():
                print(
                    f"{Fore.GREEN}APK for {plate} is valid and in the future: {apk}{Style.RESET_ALL}"
                )
            elif apk and apk <= date.today():
                print(
                    f"{Fore.RED}APK for {plate} is expired or in the past: {apk}{Style.RESET_ALL}"
                )
            else:
                print(f"{Fore.YELLOW}No valid APK data for {plate}{Style.RESET_ALL}")

            """
            Save all data
            """
            # Update car instance
            vehicle_object.first_reg = first_reg
            vehicle_object.first_reg_in_NL = first_reg_in_NL
            vehicle_object.imported_in_NL = imported_in_NL
            vehicle_object.apk = apk
            vehicle_object.exported = exported
            vehicle_object.insurance = insurance

            # Save the updated object
            vehicle_object.save()

            checked_plate = get_object_or_404(RecheckForAPKPlates, plate=plate)
            checked_plate.delete()
            print(
                f"{Fore.GREEN}Deleted plate {formatted(plate)} from UncheckedPlates{Style.RESET_ALL}"
            )

            """
            Print saved data
            """

        except NoSuchElementException:
            # Check for "no car found" notification
            self.unknown_count += 1
            try:
                no_data_notification = driver.find_element(
                    By.CLASS_NAME, "notification-content"
                )
                if (
                    "Er zijn geen voertuiggegevens gevonden"
                    in no_data_notification.text
                ):
                    print(
                        f"{Fore.RED}No car data found for license plate: {plate}{Style.RESET_ALL}"
                    )
                    print(
                        f"{Fore.RED}Marking vehicle {vehicle_object.display_name} with licence plate {plate} as archived!{Style.RESET_ALL}"
                    )
                    vehicle_object.archived = True
                    vehicle_object.save()

            except NoSuchElementException:
                print(f"Unexpected structure for license plate: {plate}")
                plate_instance, plate_created = UncheckedPlates.objects.get_or_create(
                    plate=plate,
                )
                if plate_created:
                    print(f"Adding plate {plate_instance.plate} to check it later...")
                t.sleep(10)
                return

    def handle(self, *args, **options):
        """
        Command main handler
        """

        self.updated_count = 0
        self.no_changes_count = 0
        self.unknown_count = 0

        pattern_to_function = {
            "APK": generate_license_plates_from_db_for_APK_check,
        }
        # Init steps start
        print(Fore.GREEN + "Command executed!" + Style.RESET_ALL)
        start_time = datetime.now()  # Start timestamp
        print(f"Start time: {start_time.strftime('%Y-%m-%d %H:%M:%S')}")
        print(Fore.YELLOW + "Opening browser..." + Style.RESET_ALL)
        driver = webdriver.Chrome()
        # driver = webdriver.Chrome()
        driver.get("https://ovi.rdw.nl/")
        print(Fore.GREEN + "Browser open" + Style.RESET_ALL)
        t.sleep(5)
        # Init steps done

        # Setting args from command
        chunk_size = options["chunk_size"]
        print(f"Chunk size set to: {chunk_size}")
        pattern = options["pattern"]
        print(f"Pattern set to: {formatted(pattern)}")

        # Retrieve the last plate checked
        last_plate = self.get_last_plate(pattern)
        if last_plate:
            print(
                f"Resuming from plate after: {Fore.BLACK}{Back.YELLOW}{formatted(last_plate)}{Style.RESET_ALL}"
            )
        else:
            print("Starting from the beginning of the pattern.")

        # Check if the pattern exists in the mapping
        if pattern in pattern_to_function:
            plates_generator = pattern_to_function[pattern]()
        else:
            # Handle invalid patterns
            print(
                f"Error: Unknown pattern '{pattern}'. Please provide a valid pattern."
            )
            return

        try:
            # Generate license plates
            if last_plate:
                plates_generator = self.skip_to_last_plate(plates_generator, last_plate)

            # Process only one chunk
            chunk = next(
                self.chunked_generator(plates_generator, chunk_size),
                None,
            )

            if chunk:
                print(f"Processing a new chunk of plates ({chunk_size} plates)...")
                plate_start_time = t.time()  # Track time for plates
                processed_plates = 0  # Track processed plates
                for count, plate in enumerate(chunk, start=1):
                    print(
                        f"Processing licence plate {count}/{chunk_size}: {Fore.BLACK}{Back.YELLOW}{formatted(plate)}{Style.RESET_ALL}"
                    )
                    self.scrape_license_plate(driver, plate)
                    self.save_last_plate(plate, pattern)
                    processed_plates += 1
                    random_pause()  # Pause between requests
                print("Finished processing the chunk. Command will now exit.")
                plate_end_time = t.time()  # End time for plates
                elapsed_time = plate_end_time - plate_start_time
                average_time_per_plate = (
                    elapsed_time / processed_plates if processed_plates else 0
                )
                print(f"Elapsed time: {elapsed_time:.2f} seconds.")
                print(f"Average time per plate: {average_time_per_plate:.2f} seconds.")
            else:
                print("No more plates to process. Command will now exit.")

        finally:
            # Closing steps start
            print(
                Fore.YELLOW
                + f"Total Count of APK data changed: {self.updated_count}"
                + Style.RESET_ALL
            )
            print(
                Fore.YELLOW
                + f"Total Count of APK data NOT changed: {self.no_changes_count}"
                + Style.RESET_ALL
            )
            print(
                Fore.YELLOW
                + f"Total Count of Unknown APK data: {self.unknown_count}"
                + Style.RESET_ALL
            )
            print(Fore.YELLOW + "Deleting Last PLate..." + Style.RESET_ALL)
            last_plate_object = get_object_or_404(LastPlatechecked, pattern=pattern)
            last_plate_object.delete()
            print(Fore.YELLOW + "Closing browser..." + Style.RESET_ALL)
            driver.quit()
            end_time = datetime.now()  # End timestamp
            print(f"End time: {end_time.strftime('%Y-%m-%d %H:%M:%S')}")
            total_elapsed_time = (end_time - start_time).total_seconds()
            print(f"Total elapsed time: {total_elapsed_time:.2f} seconds.")
            # Closing steps done
