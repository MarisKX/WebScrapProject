# Python imports
import time as t
import random as r
import locale
from datetime import datetime
import itertools

# Django Imports
from django.core.management.base import BaseCommand
from django.utils.timezone import now

# Selenium Imports
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException

# Terminal color import
from colorama import Fore, Back, Style, init

"""
Pattern and Utility Imports
"""
# 99-XX-XX pattern
from core.patterns.pattern_99_XX_XX import generate_license_plate_99_xx_xx

# XX-00-00 pattern
from core.patterns.pattern_xx_99_99 import generate_license_plate_xx_99_99

# XX-999-X pattern
from core.patterns.pattern_99_XXX_9 import generate_license_plate_99_xxx_9

# XXX-99-X pattern
from core.patterns.pattern_XXX_99_X import generate_license_plate_xxx_99_x

# FROM DB pattern
from core.patterns.from_db import generate_license_plates_from_db

# TEST pattern
from core.patterns.test_plates import generate_license_plates_test

# UNCHECKED pattern
from core.patterns.unchecked import generate_license_plates_unchecked

# Data Clearning and Utilities Imports
from core.utilities.clean_data import clean_make, clean_model, clean_vehicle_category
from core.utilities.random_pause import random_pause
from core.utilities.licence_plate_formatter import format_license_plate as formatted
from core.utilities.get_table_element import get_element_text_by_label as get_text
from core.utilities.get_date import get_date as get_date

# Custom models imports
from vehicles.models import (
    Make,
    Model,
    Vehicle,
    Color,
    FuelType,
    VehicleCategory,
    BodyType,
)
from core.models import LastPlatechecked, UncheckedPlates


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

    def generate_license_plates_test(self):
        """Generate license plates with the AA0000 pattern."""
        yield "01DBBH"

    def generate_unchecked_license_plates_from_db(self):
        """
        Generator to yield unchecked license plates.
        """
        for plate in UncheckedPlates.objects.values_list("plate", flat=True):
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
            General data
            """
            # Make
            make_raw = driver.find_element(
                By.CLASS_NAME,
                "vehicle-brand",
            ).text
            make = clean_make(make_raw)

            # Model
            model_raw = driver.find_element(
                By.CLASS_NAME,
                "vehicle-trade-name",
            ).text
            model = clean_model(make, model_raw)

            # Color
            color = get_text(driver, "Kleur")

            # Category/Tye
            category_raw = get_text(driver, "Voertuigcategorie")
            vehicle_category, category_code = clean_vehicle_category(category_raw)

            # Body Type
            for field_name in ["Carrosserietype", "Speciale doeleinden"]:
                body_type_raw = get_text(driver, field_name)
                if body_type_raw is not None:
                    break
            else:
                body_type_raw = "Undefined (NA)"

            body_type, body_type_code = clean_vehicle_category(body_type_raw)

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
            Expand weight dropdown
            Gewichten
            """
            expand_overzicht_gewichten = driver.find_element(
                By.ID,
                "acc-overzicht-gewichten-toggle",
            )
            expand_overzicht_gewichten.click()
            t.sleep(2)
            curb_weight = get_text(driver, "Massa rijklaar")
            empty_weight = get_text(driver, "Massa ledig voertuig")
            max_weight_tech = get_text(driver, "Technische max. massa voertuig")
            max_weight_legal = get_text(driver, "Toegestane max. massa voertuig")
            gross_combination_weight = get_text(driver, "Maximum massa samenstel")
            trailer_with_brakes = get_text(driver, "Aanhangwagen geremd")
            trailer_without_brakes = get_text(driver, "Aanhangwagen ongeremd")

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

            """
            Open Engine Data Tab
            Motor & Milieu
            """
            try:
                engine_data_tab = driver.find_element(
                    By.ID,
                    "tab-motor-milieu",
                )
                engine_data_tab.click()
                t.sleep(2)

                # Engine volume
                engine_volume = get_text(driver, "Cilinderinhoud")

                # Cylinder Count
                cylinder_count = get_text(driver, "Aantal cilinders")
                if len(cylinder_count) > 2:
                    cylinder_count = "NA"

                # Milieu data tab
                milieu_data_tab = driver.find_element(
                    By.ID,
                    "acc-motor-milleu-prestaties-toggle",
                )
                milieu_data_tab.click()
                t.sleep(2)
                # Fuel Type

                dt_elements_fuel = driver.find_elements(
                    By.XPATH, "//dt[text()='Brandstof']"
                )
                print(f"Number of 'Brandstof' elements found: {len(dt_elements_fuel)}")

                try:
                    # Fuel 1
                    fuel_list_1 = driver.find_element(
                        By.ID,
                        "acc-brandstof-milieu-tabel-brandstof-milieu-tabel-1-toggle",
                    )
                    fuel_list_1.click()
                    t.sleep(2)
                    print("Fuel Dropdown found, car has 2 fuel types")
                    dt_element_fuel_1 = driver.find_element(
                        By.XPATH,
                        "//dt[text()='Brandstof']",
                    )
                    dd_element_fuel_1 = dt_element_fuel_1.find_element(
                        By.XPATH,
                        "following-sibling::dd",
                    )
                    fuel_1 = dd_element_fuel_1.text
                    kw = get_text(driver, "Nettomaximumvermogen")
                    print(f"Fuel 1: {fuel_1}")
                    fuel_list_1.click()
                    t.sleep(2)

                    # Fuel 2
                    fuel_list_2 = driver.find_element(
                        By.ID,
                        "acc-brandstof-milieu-tabel-brandstof-milieu-tabel-2-toggle",
                    )
                    fuel_list_2.click()
                    t.sleep(2)
                    print("Fuel Dropdown found, car has 2 fuel types")
                    dt_elements_fuel_2 = driver.find_elements(
                        By.XPATH, "//dt[text()='Brandstof']"
                    )
                    dt_element_fuel_2 = next(
                        (el for el in dt_elements_fuel_2 if el.is_displayed()), None
                    )
                    dd_element_fuel_2 = dt_element_fuel_2.find_element(
                        By.XPATH,
                        "following-sibling::dd",
                    )
                    fuel_2 = dd_element_fuel_2.text
                    print(f"Fuel 2: {fuel_2}")
                    fuel_list = [fuel_1, fuel_2]
                    dt_elements_kw_2 = driver.find_elements(
                        By.XPATH, "//dt[text()='Nettomaximumvermogen']"
                    )
                    dt_element_kw_2 = next(
                        (el for el in dt_elements_kw_2 if el.is_displayed()), None
                    )
                    dd_element_kw_2 = dt_element_kw_2.find_element(
                        By.XPATH,
                        "following-sibling::dd",
                    )
                    kw2 = dd_element_kw_2.text

                except NoSuchElementException:
                    print("Fuel List is None, car has 1 fuel type")
                    fuel_1 = get_text(driver, "Brandstof")
                    kw = get_text(driver, "Nettomaximumvermogen")
                    kw2 = None
                    fuel_list = [fuel_1]
            except NoSuchElementException:
                print("Engine Data Tab not found, skipping engine data...")
                engine_volume = None
                cylinder_count = None
                fuel_list = None
                kw = None
                kw2 = None
            # Print all data
            print(
                f"{Fore.GREEN}Licence Plate: {formatted(plate)}, Vehicle Category: {vehicle_category}, Make: {make}, Model: {model}, First Reg: {first_reg}, APK: {apk}{Style.RESET_ALL}"  # noqa
            )

            """
            Save all data
            """
            # Create or update the VehicleCategory model
            vehicle_category_instance, vehicle_category_created = (
                VehicleCategory.objects.get_or_create(
                    code=category_code, defaults={"display_name": vehicle_category}
                )
            )
            # Create or update the VehicleBodyType model
            vehicle_body_type_instance, vehicle_body_type_created = (
                BodyType.objects.get_or_create(
                    code=body_type_code, defaults={"display_name": body_type}
                )
            )
            # Create or update the Make (Brand) model
            make_instance, make_created = Make.objects.get_or_create(
                vehicle_category=vehicle_category_instance,
                display_name=make.title(),
                raw_make=make_raw,
            )
            # Create or update the Model model
            model_instance, model_created = Model.objects.get_or_create(
                make=make_instance,
                display_name=model,
                raw_model=model_raw,
            )
            # Create or update the Color model
            color_instance, color_created = Color.objects.get_or_create(
                display_name=color.title() if color else "-"
            )
            # Create or update car instance
            vehicle_instance, vehicle_created = Vehicle.objects.update_or_create(
                licence_plate=plate,
                defaults={
                    "make": make_instance,
                    "model": model_instance,
                    "vehicle_category": vehicle_category_instance,
                    "body_type": vehicle_body_type_instance,
                    "first_reg": first_reg,
                    "first_reg_in_NL": first_reg_in_NL,
                    "imported_in_NL": imported_in_NL,
                    "apk": apk,
                    "color": color_instance,
                    "engine_volume": engine_volume,
                    "cylinder_count": cylinder_count,
                    "kw": kw,
                    "kw2": kw2,
                    "exported": exported,
                    "insurance": insurance,
                    "curb_weight": curb_weight,
                    "empty_weight": empty_weight,
                    "max_weight_tech": max_weight_tech,
                    "max_weight_legal": max_weight_legal,
                    "gross_combination_weight": gross_combination_weight,
                    "trailer_with_brakes": trailer_with_brakes,
                    "trailer_without_brakes": trailer_without_brakes,
                },
            )
            undefined_fuel = FuelType.objects.get_or_create(
                code="NA", display_name="Undefined"
            )[0]
            # Assign valid fuel types to the car
            if fuel_list:
                for fuel in fuel_list:
                    if fuel:  # Check if fuel is not None or empty
                        fuel_type = FuelType.objects.filter(
                            display_name__iexact=fuel
                        ).first()
                        if not fuel_type:
                            print(f"Fuel type '{fuel}' not found. Assigning Undefined.")
                            fuel_type = undefined_fuel
                        vehicle_instance.fuel_type.add(fuel_type)
                        vehicle_instance.save()
            else:
                vehicle_instance.fuel_type.add(undefined_fuel)
                vehicle_instance.save

            if not vehicle_created:
                vehicle_instance.save()

            """
            Print saved data
            """
            # Vehicle Category
            if vehicle_category_created:
                print(
                    f"New Vehicle Category created: {vehicle_category_instance.display_name}"
                )
            else:
                print(
                    f"Vehicle Category retrieved: {vehicle_category_instance.display_name}"
                )
            # Body Type
            if vehicle_body_type_created:
                print(
                    f"New Body Type created: {vehicle_body_type_instance.display_name}"
                )
            else:
                print(f"Body Type retrieved: {vehicle_body_type_instance.display_name}")
            # Make
            if make_created:
                print(f"New Make created: {make_instance.display_name}")
            else:
                print(f"Make retrieved: {make_instance.display_name}")
            # Model
            if model_created:
                print(f"New Model created: {model_instance.display_name}")
            else:
                print(f"Model retrieved: {model_instance.display_name}")
            # Color
            if color_created:
                print(f"New Color created: {color_instance.display_name}")
            elif color_instance:
                print(f"Color retrieved: {color_instance.display_name}")
            else:
                print("No color registered for this vehicle.")
            # Vehicle
            if vehicle_created:
                print(f"New Vehicle created: {vehicle_instance.display_name}")
            else:
                print(f"Vehicle retrieved: {vehicle_instance.display_name}")

        except NoSuchElementException:
            # Check for "no car found" notification
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
            except NoSuchElementException:
                print(f"Unexpected structure for license plate: {plate}")
                plate_instance, plate_created = UncheckedPlates.objects.get_or_create(
                    plate=plate,
                )
                if plate_created:
                    print(f"Adding plate {plate_instance.plate} to check it later...")
                t.sleep(10)

    def handle(self, *args, **options):
        """
        Command main handler
        """
        pattern_to_function = {
            "XX9999": generate_license_plate_xx_99_99,
            "99XXXX": generate_license_plate_99_xx_xx,
            "99XXX9": generate_license_plate_99_xxx_9,
            "XXX99X": generate_license_plate_xxx_99_x,
            "FROMDB": generate_license_plates_from_db,
            "TEST": generate_license_plates_test,
            "UNCHEC": generate_license_plates_unchecked,
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
            print(Fore.YELLOW + "Closing browser..." + Style.RESET_ALL)
            driver.quit()
            end_time = datetime.now()  # End timestamp
            print(f"End time: {end_time.strftime('%Y-%m-%d %H:%M:%S')}")
            total_elapsed_time = (end_time - start_time).total_seconds()
            print(f"Total elapsed time: {total_elapsed_time:.2f} seconds.")
            # Closing steps done
