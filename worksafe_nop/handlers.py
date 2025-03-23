from playwright.sync_api import Page
from worksafe_nop.settings import Settings


def handle_dropdown(page: Page, selector: str, value: str):
    """Handle dropdown selection with special handling for Angular selects."""
    try:
        # First try standard select method
        page.select_option(selector, label=value)
        return
    except:
        pass

    # Get all options
    options = page.locator(f"{selector} option").all()
    for i, option in enumerate(options):
        option_text = option.inner_text().strip()
        option_value = option.get_attribute("value") or ""

        # Try different matching strategies
        if option_text == value or option_value == value:
            page.select_option(selector, index=i)
            return

        # Check for partial text match (ignoring spaces)
        if value.strip() in option_text.replace(" ", ""):
            page.select_option(selector, index=i)
            return

        # Handle Angular's format "1: Hours"
        if ":" in option_value and value in option_value:
            page.select_option(selector, index=i)
            return

        # Extra check for time values like "08:00" in "8: 08:00"
        if ":" in option_value and value.lstrip("0") in option_value:
            page.select_option(selector, index=i)
            return

    # JavaScript fallback for stubborn selects
    options = page.evaluate(f"""() => {{
        const select = document.querySelector("{selector}");
        const options = Array.from(select.options);
        for (let i = 0; i < options.length; i++) {{
            const option = options[i];
            if (option.text.includes("{value}")) {{
                select.selectedIndex = i;
                select.dispatchEvent(new Event('change'));
                return true;
            }}
        }}
        return false;
    }}""")

    if not options:
        print(f"Could not find dropdown option for: {value}")


def handle_radio_button(page: Page, selector: str, value: str):
    """Handle radio button selection."""
    try:
        # Find all radio inputs with this name
        radio_inputs = page.locator(f"{selector}").all()
        if not radio_inputs:
            print(f"Error: No radio inputs found with selector: {selector}")
            return

        # Find the radio input whose ID contains the value
        value_lower = value.lower()
        for radio in radio_inputs:
            radio_id = radio.get_attribute("id") or ""
            radio_element_value = radio.get_attribute("value") or ""

            # Check if ID or value match
            if (
                value_lower in radio_id.lower()
                or radio_element_value.lower() == value_lower
                or radio_element_value.lower().replace(" ", "") == value_lower.replace(" ", "")
            ):
                # For Angular applications, clicking the span might be more reliable
                radio_id_selector = f"#{radio_id}"
                span_selector = f'label[for="{radio_id}"] span.checkmark'

                try:
                    # Try clicking the span first
                    if page.is_visible(span_selector, timeout=Settings.SHORT_TIMEOUT):
                        page.click(span_selector)
                        print(f"Clicked radio span: {span_selector}")
                    # If not, click the input directly
                    else:
                        page.click(radio_id_selector)
                        print(f"Clicked radio input: {radio_id_selector}")
                    return
                except Exception as direct_click_error:
                    print(f"Direct click failed, trying label: {direct_click_error}")

                    # Try clicking the label if span/input clicks failed
                    try:
                        label_selector = f'label[for="{radio_id}"]'
                        if page.is_visible(label_selector, timeout=Settings.SHORT_TIMEOUT):
                            page.click(label_selector)
                            print(f"Clicked radio label: {label_selector}")
                            return
                    except Exception as label_click_error:
                        print(f"Label click also failed: {label_click_error}")

        # If we got here, we didn't find a matching radio
        print(f"Could not find radio option matching value: {value}")
        # Try clicking the first radio as fallback
        if radio_inputs:
            first_radio_id = radio_inputs[0].get_attribute("id")
            try:
                page.click(f"#{first_radio_id}")
                print(f"Clicked first radio as fallback: #{first_radio_id}")
            except:
                print("Could not click any radio button")

    except Exception as e:
        print(f"Error in handle_radio_button: {e}")
        # Last resort: try clicking original selector
        try:
            page.click(selector)
            print(f"Clicked original selector as last resort: {selector}")
        except:
            pass


def handle_checkbox(page: Page, selector: str, value: str):
    """Handle checkbox selection."""
    try:
        # Convert value to boolean if it's not already
        if isinstance(value, str):
            should_check = value.lower() in ["yes", "true", "1", "on"]
        else:
            should_check = bool(value)

        # First try direct checkbox
        try:
            is_checked = page.is_checked(selector)
            if is_checked != should_check:
                page.click(selector, timeout=Settings.SHORT_TIMEOUT)
                print(f"Clicked checkbox {selector} directly")
                return
        except Exception as e:
            print(f"Direct checkbox click failed: {e}")

        # Try clicking the associated span.checkmark-checkbox
        try:
            # First identify if this is an Angular style checkbox
            input_exists = page.evaluate(f'!!document.querySelector("{selector}")')
            if input_exists:
                # Get current checked state
                is_checked = page.evaluate(f'document.querySelector("{selector}").checked')

                # If state needs to be changed
                if is_checked != should_check:
                    # Try clicking the span
                    span_selector = (
                        f'label[for="{selector.replace("#", "")}"] span.checkmark-checkbox'
                    )
                    if page.is_visible(span_selector):
                        page.click(span_selector)
                        print(f"Clicked checkbox span {span_selector}")
                        return

                    # Try clicking the label
                    label_selector = f'label[for="{selector.replace("#", "")}"]'
                    if page.is_visible(label_selector):
                        page.click(label_selector)
                        print(f"Clicked checkbox label {label_selector}")
                        return

        except Exception as e:
            print(f"Span/label click failed: {e}")

        print(f"WARNING: Could not set checkbox {selector} to {should_check}")

    except Exception as e:
        print(f"Error in handle_checkbox: {e}")


def handle_address(page: Page, selector: str, value: str):
    """Handle address input with autocomplete."""
    # Fill the address field
    page.fill(selector, value)

    # Wait for autocomplete suggestions to appear
    page.wait_for_timeout(Settings.STANDARD_TIMEOUT)

    # Try to select the first Google Maps autocomplete suggestion
    try:
        # Check for Google's autocomplete dropdown
        suggestion_selectors = [
            ".pac-container .pac-item:first-child",  # Standard Google Places API
            ".pac-container div:first-child",  # Alternative structure
            "ul.pac-container li:first-child",  # Another variation
            "[data-reach-combobox-popover] [data-reach-combobox-option]:first-child",  # For some React implementations
        ]

        for suggestion_selector in suggestion_selectors:
            if page.is_visible(suggestion_selector, timeout=Settings.SHORT_TIMEOUT):
                page.click(suggestion_selector)
                print(f"Selected address from Google autocomplete using: {suggestion_selector}")
                break
        else:
            # If no suggestions found, try pressing Enter to select the top suggestion
            page.press(selector, "Enter")
            print("Pressed Enter to select top Google autocomplete suggestion")
    except Exception as e:
        print(f"Error selecting address from Google autocomplete: {e}")
