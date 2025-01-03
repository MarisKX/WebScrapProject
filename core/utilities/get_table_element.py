from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException


def get_element_text_by_label(driver, search_text):
    """
    Retrieve the text of an element based on the given label (e.g., "Kleur").

    Args:
        driver: Selenium WebDriver instance.
        search_text (str): The label text to search for (e.g., "Kleur").

    Returns:
        str: The text associated with the label, or None if not found.
    """
    try:
        # Find the <dt> element with the specified label
        dt_element = driver.find_element(By.XPATH, f"//dt[text()='{search_text}']")
        # Find the corresponding <dd> element
        dd_element = dt_element.find_element(By.XPATH, "following-sibling::dd")
        # Return the text content of the <dd> element
        return dd_element.text
    except NoSuchElementException:
        print(f"Element with label '{search_text}' not found.")
        return None
