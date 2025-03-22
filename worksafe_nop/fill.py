import json
import os
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import argparse

def load_json_file(filename):
    """Load JSON data from a file."""
    with open(filename, 'r') as file:
        return json.load(file)

def fill_form(driver, page_name, mappings, data):
    """Fill form fields based on mappings."""
    # Find the correct page mapping
    page_mapping = None
    for page in mappings["pages"]:
        if page_name in page:
            page_mapping = page[page_name]
            break

    if not page_mapping:
        print(f"No mappings found for page: {page_name}")
        return

    print(f"Filling form for page: {page_name}")

    # Wait for Angular to load (adjust timeout as needed)
    time.sleep(3)

    # Fill each field based on the mapping
    for field_id, field_config in page_mapping.items():
        data_key = field_config["data_key"]
        field_type = field_config["type"]

        if data_key in data:
            value = data[data_key]
            # Try multiple methods to find and fill the element
            fill_element(driver, field_id, value, data_key, field_type)
            time.sleep(0.5)

def fill_element(driver, field_id, value, data_key, field_type):
    """Try multiple strategies to find and fill form elements."""
    # Special handling for radio buttons with ID values
    if field_type == "radio" and value.startswith("rd"):
        try:
            # If value is a radio button ID (like rdAsbestos), use it directly
            radio = driver.find_element(By.ID, value)
            driver.execute_script("arguments[0].click();", radio)
            print(f"Selected radio button with ID: {value}")
            return
        except Exception as e:
            # Continue with other strategies if direct ID approach fails
            print(f"Could not select radio directly, trying other methods: {e}")

    # List of strategies to find elements in Angular app
    strategies = [
        # By ID
        (By.ID, field_id),
        # By name
        (By.NAME, field_id),
        # Common Angular attribute patterns
        (By.XPATH, f"//*[@ng-model='{field_id}']"),
        (By.XPATH, f"//*[@formcontrolname='{field_id}']"),
        (By.XPATH, f"//*[@name='{field_id}']"),
        (By.XPATH, f"//*[contains(@id, '{field_id}')]"),
        # Label-based approach
        (By.XPATH, f"//label[contains(text(), '{field_id}')]/following::input[1]"),
        # Input with placeholder
        (By.XPATH, f"//input[@placeholder='{field_id}']"),
    ]

    for by, selector in strategies:
        try:
            # Wait for element to be clickable
            wait = WebDriverWait(driver, 0.2)  # Increased wait time
            element = wait.until(EC.element_to_be_clickable((by, selector)))

            # Handle different input types based on field_type
            if field_type == "text" or field_type == "number" or field_type == "email":
                element.clear()
                element.send_keys(value)
            elif field_type == "textarea":
                element.clear()
                element.send_keys(value)
            elif field_type == "radio":
                handle_radio_button(driver, element, value)
            elif field_type == "checkbox":
                handle_checkbox(element, value)
            elif field_type == "select":
                handle_dropdown(driver, element, value)
            elif field_type == "date":
                handle_date_input(driver, element, value)
            elif field_type == "time":
                handle_time_input(driver, element, value)
            else:
                # Default case - try to send keys
                element.clear()
                element.send_keys(value)

            print(f"Filled {field_id} with {value} using {by} selector: {selector}")
            return
        except Exception as e:
            continue

    print(f"Could not find field: {field_id} for {data_key}")

def handle_date_input(driver, element, value):
    """Handle date input fields."""
    # Clear existing value
    element.clear()

    # Some date fields require special handling
    try:
        # Try direct input first
        element.send_keys(value)
    except:
        # If direct input fails, try JavaScript
        driver.execute_script(
            "arguments[0].value = arguments[1]", element, value)

def handle_time_input(driver, element, value):
    """Handle time input fields."""
    # Clear existing value
    element.clear()

    # Try direct input first
    try:
        element.send_keys(value)
    except:
        # If direct input fails, try JavaScript
        driver.execute_script(
            "arguments[0].value = arguments[1]", element, value)

def handle_radio_button(driver, element, value):
    """Handle radio button selection."""
    tag_name = element.tag_name.lower()

    # If element is already the radio button
    if tag_name == "input" and element.get_attribute("type") == "radio":
        # If the value is a radio button ID
        if value.startswith("rd"):
            try:
                radio = driver.find_element(By.ID, value)
                driver.execute_script("arguments[0].click();", radio)
                return
            except:
                # If ID not found, continue with normal handling
                pass

        # Standard Yes/No handling
        if value.lower() in ["yes", "true", "1"]:
            radio_value = "true"
        elif value.lower() in ["no", "false", "0"]:
            radio_value = "false"
        else:
            radio_value = value

        # Try to find the related radio button with the matching value
        try:
            form_group = element.find_element(By.XPATH,
                "./ancestor::div[contains(@class, 'form') or contains(@class, 'radio')]")
            radio_buttons = form_group.find_elements(By.XPATH, ".//input[@type='radio']")

            for radio in radio_buttons:
                if radio.get_attribute("value") == radio_value or radio.get_attribute("id") == radio_value:
                    driver.execute_script("arguments[0].click();", radio)
                    return
        except:
            pass

    # If specific value not found or element isn't a radio, just click the provided element
    driver.execute_script("arguments[0].click();", element)

def handle_checkbox(element, value):
    """Handle checkbox selection."""
    is_checked = element.is_selected()
    should_check = value.lower() in ["yes", "true", "1"]

    if is_checked != should_check:
        element.click()


def handle_dropdown(driver, element, value):
    """Handle dropdown selection."""
    tag_name = element.tag_name.lower()

    if tag_name != "select":
        # If not a select element, try as a regular input
        element.clear()
        element.send_keys(value)
        return

    # Get all options
    options = element.find_elements(By.TAG_NAME, "option")

    # Try several matching strategies
    for option in options:
        option_text = option.text.strip()
        option_value = option.get_attribute("value")

        # Check for exact matches first
        if option_text == value or option_value == value:
            option.click()
            return

        # Check for partial text match (ignoring spaces)
        if value.strip() in option_text.replace(" ", ""):
            option.click()
            return

        # Handle Angular's format "1: Hours"
        if ":" in option_value and value in option_value:
            option.click()
            return

        # Extra check for time values like "08:00" in "8: 08:00"
        if ":" in option_value and value.lstrip("0") in option_value:
            option.click()
            return

        print("Could not find dropdown option for:", value)

def monitor_navigation(driver, current_page, mappings, data):
    """Monitor for page navigation and fill new forms as needed."""
    current_url = driver.current_url

    while True:
        time.sleep(1)  # Check every second
        try:
            new_url = driver.current_url
            if new_url != current_url:
                # URL changed, check if it's a known page
                current_url = new_url
                for page in mappings["pages"]:
                    page_name = list(page.keys())[0]
                    if page_name in current_url:
                        fill_form(driver, page_name, mappings, data)
                        break
        except:
            print("Browser closed, exiting.")
            break

def main():
    parser = argparse.ArgumentParser(description='Fill WorkSafeBC forms automatically')
    parser.add_argument('--page', default='general-information',
                        help='Starting page name (default: general-information)')
    args = parser.parse_args()

    # Load data and mappings
    script_dir = os.path.dirname(os.path.abspath(__file__))
    data = load_json_file(os.path.join(script_dir, 'data.json'))
    mappings = load_json_file(os.path.join(script_dir, 'mappings.json'))

    # Set up Chrome options
    chrome_options = Options()
    chrome_options.add_experimental_option("detach", True)  # Keep browser open

    # Initialize the WebDriver
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()),
                             options=chrome_options)

    # Open the website with the specified page
    url = f"https://prevnop.online.worksafebc.com/{args.page}"
    driver.get(url)

    # Fill the initial form
    fill_form(driver, args.page, mappings, data)

    # Monitor for navigation to other pages
    monitor_navigation(driver, args.page, mappings, data)

if __name__ == "__main__":
    main()
