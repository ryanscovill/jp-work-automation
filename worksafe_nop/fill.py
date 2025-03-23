import json
import os
import time
import argparse
from playwright.sync_api import sync_playwright, Page, Playwright

def load_json_file(filename):
    """Load JSON data from a file."""
    with open(filename, 'r') as file:
        return json.load(file)

def fill_form(page: Page, page_name: str, mappings, data):
    """Fill form fields based on mappings."""
    # Find the correct page mapping
    page_mapping = None
    for p in mappings["pages"]:
        if page_name in p:
            page_mapping = p[page_name]
            break

    if not page_mapping:
        print(f"No mappings found for page: {page_name}")
        return

    print(f"Filling form for page: {page_name}")

    # Wait for Angular to load
    page.wait_for_load_state("networkidle")

    # Fill each field based on the mapping
    for field_id, field_config in page_mapping.items():
        data_key = field_config["data_key"]
        field_type = field_config["type"]

        if data_key in data:
            value = data[data_key]
            if value:
                fill_element(page, field_id, value, data_key, field_type)
                # Small pause between field interactions
                page.wait_for_timeout(100)

def fill_element(page: Page, field_id: str, value: str, data_key: str, field_type: str):
    """Fill a form element using the appropriate method based on field type."""
    try:
        # Try to find the element using various selectors
        selectors = [
            f"#{field_id}",  # By ID
            f"[name={field_id}]",  # By name
            f"[ng-model='{field_id}']",  # Angular ng-model
            f"[formcontrolname='{field_id}']",  # Angular reactive forms
            f"[id*='{field_id}']",  # ID contains
            f"label:has-text('{field_id}') + input, label:has-text('{field_id}') ~ input",  # Label + adjacent input
            f"[placeholder='{field_id}']"  # Placeholder
        ]

        # Add specific selector for select elements
        if field_type == "select":
            selectors.append(f"label:has-text('{field_id}') ~ select")

        # Try each selector
        element_handle = None
        used_selector = None

        for selector in selectors:
            if page.locator(selector).count() > 0:
                element_handle = page.locator(selector).first
                used_selector = selector
                break

        if not element_handle:
            print(f"Could not find field: {field_id} for {data_key}")
            return

        # Handle based on field type
        if field_type == "text" or field_type == "number" or field_type == "email":
            page.fill(used_selector, value)

        elif field_type == "address":
            handle_address(page, used_selector, value)

        elif field_type == "textarea":
            page.fill(used_selector, value)

        elif field_type == "select":
            handle_dropdown(page, used_selector, value)

        elif field_type == "date":
            page.fill(used_selector, value)
            # Fallback to JS if needed
            page.evaluate(f'document.querySelector("{used_selector}").value = "{value}"')

        elif field_type == "radio":
            handle_radio_button(page, used_selector, value)

        elif field_type == "checkbox":
            handle_checkbox(page, used_selector, value)

        else:
            # Default to fill
            page.fill(used_selector, value)

        print(f"Filled {field_id} with {value} using selector: {used_selector}")

    except Exception as e:
        print(f"Error filling {field_id}: {e}")

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
        radio_inputs = page.locator(f'{selector}').all()
        if not radio_inputs:
            print(f"Error: No radio inputs found with selector: {selector}")
            return
            
        # Find the radio input whose ID contains the value
        value_lower = value.lower()
        for radio in radio_inputs:
            radio_id = radio.get_attribute('id') or ''
            radio_element_value = radio.get_attribute('value') or ''
            
            # Check if ID or value match
            if (value_lower in radio_id.lower() or 
                radio_element_value.lower() == value_lower or
                radio_element_value.lower().replace(" ", "") == value_lower.replace(" ", "")):
                
                # For Angular applications, clicking the span might be more reliable
                radio_id_selector = f'#{radio_id}'
                span_selector = f'label[for="{radio_id}"] span.checkmark'
                
                try:
                    # Try clicking the span first
                    if page.is_visible(span_selector, timeout=100):
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
                        if page.is_visible(label_selector, timeout=100):
                            page.click(label_selector)
                            print(f"Clicked radio label: {label_selector}")
                            return
                    except Exception as label_click_error:
                        print(f"Label click also failed: {label_click_error}")
                        
        # If we got here, we didn't find a matching radio
        print(f"Could not find radio option matching value: {value}")
        # Try clicking the first radio as fallback
        if radio_inputs:
            first_radio_id = radio_inputs[0].get_attribute('id')
            try:
                page.click(f'#{first_radio_id}')
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
                page.click(selector, timeout=300)
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
                    span_selector = f'label[for="{selector.replace("#", "")}"] span.checkmark-checkbox'
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
    page.wait_for_timeout(1000)

    # Try to select the first Google Maps autocomplete suggestion
    try:
        # Check for Google's autocomplete dropdown
        suggestion_selectors = [
            ".pac-container .pac-item:first-child",  # Standard Google Places API
            ".pac-container div:first-child",        # Alternative structure
            "ul.pac-container li:first-child",       # Another variation
            "[data-reach-combobox-popover] [data-reach-combobox-option]:first-child"  # For some React implementations
        ]

        for suggestion_selector in suggestion_selectors:
            if page.is_visible(suggestion_selector, timeout=300):
                page.click(suggestion_selector)
                print(f"Selected address from Google autocomplete using: {suggestion_selector}")
                break
        else:
            # If no suggestions found, try pressing Enter to select the top suggestion
            page.press(selector, "Enter")
            print("Pressed Enter to select top Google autocomplete suggestion")
    except Exception as e:
        print(f"Error selecting address from Google autocomplete: {e}")

def monitor_navigation(page: Page, current_page: str, mappings, data):
    """Monitor for Angular client-side navigation and fill forms as needed."""
    # Install route change detector for Angular
    page.evaluate("""() => {
        // Monitor for Angular route changes using router events
        window._prevPathname = location.pathname;
        window._routeChanges = [];
        
        // Watch for DOM changes that might indicate navigation
        const observer = new MutationObserver((mutations) => {
            // Check if URL path has changed
            if (location.pathname !== window._prevPathname) {
                window._routeChanges.push(location.pathname);
                window._prevPathname = location.pathname;
            }
            
            // Check for Angular view container changes
            const hasRouterOutlet = document.querySelector('router-outlet, [ng-view], .ng-view');
            if (hasRouterOutlet) {
                // If router outlet's next sibling changed, likely a view change
                window._routeChanges.push('view-changed');
            }
        });
        
        // Observe the entire document for changes
        observer.observe(document.body, {
            childList: true,
            subtree: true
        });
        
        // Intercept history methods for SPA navigation
        const originalPushState = history.pushState;
        const originalReplaceState = history.replaceState;
        
        history.pushState = function() {
            originalPushState.apply(this, arguments);
            window._routeChanges.push(location.pathname);
        };
        
        history.replaceState = function() {
            originalReplaceState.apply(this, arguments);
            window._routeChanges.push(location.pathname);
        };
    }""")

    # Check for visible page indicators instead of URL
    def detect_current_page():
        """Try to determine which page we're currently on based on visible content"""
        try:
            # Look for page-specific elements or content
            page_title = page.evaluate("""() => {
                // Try different ways to find the page title/heading
                const h1 = document.querySelector('h1, .page-title, .title');
                if (h1) return h1.innerText;
                
                // Look for breadcrumb
                const breadcrumb = document.querySelector('.breadcrumb li:last-child');
                if (breadcrumb) return breadcrumb.innerText;
                
                // Look for form legend or fieldset title
                const legend = document.querySelector('legend, fieldset > h2');
                if (legend) return legend.innerText;
                
                return document.title;
            }""")

            if page_title:
                page_title = page_title.lower()
                print(f"Detected page title: {page_title}")

                # Match against our known pages
                for page_data in mappings["pages"]:
                    page_name = list(page_data.keys())[0]
                    if page_name.lower() in page_title or page_title in page_name.lower():
                        return page_name

            return None
        except Exception as e:
            print(f"Error detecting current page: {e}")
            return None

    # Process the current page
    current_detected_page = detect_current_page()
    if current_detected_page:
        print(f"Initial page detected: {current_detected_page}")
        fill_form(page, current_detected_page, mappings, data)
    else:
        print(f"Using URL-based initial page: {current_page}")
        fill_form(page, current_page, mappings, data)

    # Watch for "Next" button clicks
    def watch_for_next_button():
        try:
            next_button = page.query_selector("button:has-text('Next'), input[value='Next'], .btn-primary:has-text('Next')")
            if next_button and next_button.is_visible():
                print("Found Next button - setting up click monitor")

                # Save current state before click
                pre_click_content = page.evaluate("document.body.innerHTML.length")

                # Set up detection for the page change after click
                def check_after_click():
                    page.wait_for_timeout(1500)  # Wait for Angular to update the view
                    new_content_size = page.evaluate("document.body.innerHTML.length")

                    # If content size changed significantly, likely a new page loaded
                    if abs(new_content_size - pre_click_content) > 1000:
                        print("Content changed after button click - checking for new page")
                        new_page = detect_current_page()
                        if new_page:
                            print(f"New page detected after navigation: {new_page}")
                            fill_form(page, new_page, mappings, data)

                # Install click event listener on the next button
                next_button.evaluate("el => el.addEventListener('click', () => window._clickedNext = true)")

                # Return the checker function
                return check_after_click
            return None
        except Exception as e:
            print(f"Error watching for next button: {e}")
            return None

    # Main monitoring loop
    processed_pages = set([current_detected_page or current_page])
    last_check_time = time.time()

    while True:
        time.sleep(1)
        try:
            # Check if user clicked Next
            clicked_next = page.evaluate("window._clickedNext === true")
            if clicked_next:
                page.evaluate("window._clickedNext = false")
                print("Detected Next button click")
                page.wait_for_timeout(1500)  # Wait for Angular to update

                new_page = detect_current_page()
                if new_page and new_page not in processed_pages:
                    print(f"New page detected after Next button: {new_page}")
                    fill_form(page, new_page, mappings, data)
                    processed_pages.add(new_page)

            # Check for route changes
            route_changes = page.evaluate("window._routeChanges || []")
            if route_changes:
                page.evaluate("window._routeChanges = []")
                print(f"Detected route changes: {route_changes}")

                # Wait for Angular to finish rendering
                page.wait_for_timeout(1000)
                page.wait_for_load_state("networkidle", timeout=3000)

                new_page = detect_current_page()
                if new_page and new_page not in processed_pages:
                    print(f"New page detected after route change: {new_page}")
                    fill_form(page, new_page, mappings, data)
                    processed_pages.add(new_page)

            # Periodically check for Next button
            if time.time() - last_check_time > 5:
                checker_fn = watch_for_next_button()
                if checker_fn:
                    last_check_time = time.time()

            # Fallback: periodically check if page content changed substantially
            if time.time() - last_check_time > 10:
                last_check_time = time.time()
                new_page = detect_current_page()
                if new_page and new_page not in processed_pages:
                    print(f"Detected new page during periodic check: {new_page}")
                    fill_form(page, new_page, mappings, data)
                    processed_pages.add(new_page)

        except Exception as e:
            print(f"Error in navigation monitor: {e}")
            # Don't break the loop on transient errors

def main():
    parser = argparse.ArgumentParser(description='Fill WorkSafeBC forms automatically')
    parser.add_argument('--page', default='general-information',
                        help='Starting page name (default: general-information)')
    parser.add_argument('--headless', action='store_true',
                        help='Run in headless mode (default: false)')
    args = parser.parse_args()

    # Load data and mappings
    script_dir = os.path.dirname(os.path.abspath(__file__))
    data = load_json_file(os.path.join(script_dir, 'data.json'))
    mappings = load_json_file(os.path.join(script_dir, 'mappings.json'))

    with sync_playwright() as playwright:
        # Launch browser with specified options
        browser = playwright.chromium.launch(headless=args.headless)

        # Create a new browser context with viewport and device options
        context = browser.new_context(
            viewport={'width': 1400, 'height': 900},
            accept_downloads=True
        )

        # Create a new page
        page = context.new_page()

        try:
            # Open the website with the specified page
            url = f"https://prevnop.online.worksafebc.com/{args.page}"
            page.goto(url)

            # Monitor for navigation to other pages
            monitor_navigation(page, args.page, mappings, data)

            # Wait for user to close browser manually
            print("Form filling complete. Press Ctrl+C to exit.")
            while True:
                time.sleep(1)

        except KeyboardInterrupt:
            print("Exiting due to user interrupt")
        except Exception as e:
            print(f"Error: {e}")
        finally:
            if not args.headless:
                input("Press Enter to close the browser...")
            context.close()
            browser.close()

if __name__ == "__main__":
    main()
