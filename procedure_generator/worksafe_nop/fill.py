import json
import os
import time
import sys
import argparse
from playwright.sync_api import sync_playwright, Page

from .handlers import (
    handle_address,
    handle_checkbox,
    handle_dropdown,
    handle_radio_button,
)
from ..config_loader import config


def load_json_file(filename):
    """Load JSON data from a file."""
    with open(filename, "r") as file:
        return json.load(file)


def apply_transformations(data_key, value, transformations, data):
    """Apply transformations to the value based on the transformation rules."""
    if not transformations or data_key not in transformations:
        return value

    transform = transformations[data_key]
    transform_type = transform.get("type")

    if transform_type == "map":
        # Simple mapping transformation
        mapping = transform.get("values", {})
        return mapping.get(value, value)  # Return original if no mapping found
    
    elif transform_type == "dynamic":
        source_fields = transform.get("source_fields", [])
        value_map = transform.get("value_map", {})
        
        for field in source_fields:
            if field in data and data[field]:
                if value_map:
                    return value_map.get(field, "")
                else:
                    return data[field]
    
    # Add other transformation types as needed
    return value


def fill_form(page: Page, page_name: str, mappings, data):
    """Fill form fields based on mappings."""
    # Find the correct page mapping
    page_mapping = None
    for p in mappings.pages:
        if page_name in p:
            page_mapping = p[page_name]
            break

    if not page_mapping:
        print(f"No mappings found for page: {page_name}")
        return

    print(f"Filling form for page: {page_name}")

    # Wait for Angular to load
    page.wait_for_load_state("networkidle")
    
    # Get transformations from mappings
    transformations = mappings.transformations

    # Fill each field based on the mapping
    for field_id, field_config in page_mapping.items():
        data_key = field_config["data_key"]
        field_type = field_config["type"]

        value = data.get(data_key, "") if data_key else ""
            
        if value or data_key in transformations:
            transformed_value = apply_transformations(data_key, value, transformations, data)
            
            if transformed_value:
                fill_element(page, field_id, transformed_value, data_key, field_type)
                # Small pause between field interactions
                page.wait_for_timeout(config.timeouts.field_interaction_delay)


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
            f"[placeholder='{field_id}']",  # Placeholder
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
                for page_data in mappings.pages:
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
            next_button = page.query_selector(
                "button:has-text('Next'), input[value='Next'], .btn-primary:has-text('Next')"
            )
            if next_button and next_button.is_visible():
                # print("Found Next button - setting up click monitor")

                # Save current state before click
                pre_click_content = page.evaluate("document.body.innerHTML.length")

                # Set up detection for the page change after click
                def check_after_click():
                    page.wait_for_timeout(
                        config.timeouts.navigation_timeout
                    )  # Wait for Angular to update the view
                    new_content_size = page.evaluate("document.body.innerHTML.length")

                    # If content size changed significantly, likely a new page loaded
                    if (
                        abs(new_content_size - pre_click_content)
                        > config.timeouts.content_change_threshold
                    ):
                        print("Content changed after button click - checking for new page")
                        new_page = detect_current_page()
                        if new_page:
                            print(f"New page detected after navigation: {new_page}")
                            fill_form(page, new_page, mappings, data)

                # Install click event listener on the next button
                next_button.evaluate(
                    "el => el.addEventListener('click', () => window._clickedNext = true)"
                )

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
                page.wait_for_timeout(config.timeouts.navigation_timeout)  # Wait for Angular to update

                new_page = detect_current_page()
                if new_page and new_page not in processed_pages:
                    print(f"New page detected after Next button: {new_page}")
                    fill_form(page, new_page, mappings, data)
                    processed_pages.add(new_page)

            # Check for route changes
            route_changes = page.evaluate("window._routeChanges || []")
            if route_changes:
                page.evaluate("window._routeChanges = []")
                # print(f"Detected route changes: {route_changes}")

                # Wait for Angular to finish rendering
                page.wait_for_timeout(config.timeouts.standard_timeout)
                page.wait_for_load_state("networkidle")

                new_page = detect_current_page()
                if new_page and new_page not in processed_pages:
                    print(f"New page detected after route change: {new_page}")
                    fill_form(page, new_page, mappings, data)
                    processed_pages.add(new_page)

            # Periodically check for Next button
            if time.time() - last_check_time > config.timeouts.next_button_check_interval:
                checker_fn = watch_for_next_button()
                if checker_fn:
                    last_check_time = time.time()            # Fallback: periodically check if page content changed substantially
            if time.time() - last_check_time > config.timeouts.periodic_page_check_interval:
                last_check_time = time.time()
                new_page = detect_current_page()
                if new_page and new_page not in processed_pages:
                    print(f"Detected new page during periodic check: {new_page}")
                    fill_form(page, new_page, mappings, data)
                    processed_pages.add(new_page)

        except Exception as e:
            error_message = str(e)
            print(f"Error in navigation monitor: {e}")
            
            # Check if the error indicates the browser/page was closed
            if any(keyword in error_message.lower() for keyword in [
                "target page, context or browser has been closed",
                "page has been closed",
                "browser has been closed", 
                "context has been closed",
                "connection closed"
            ]):
                print("Browser was closed by user - exiting monitoring loop")
                break
            
            # Don't break the loop on other transient errors
            continue


def fill_nop(data_file=None):
    start_page = "general-information"

    if data_file is None:
        raise ValueError("data_file must be provided")
    
    data = load_json_file(data_file)
    mappings = config.nop

    with sync_playwright() as playwright:
        # Launch browser with specified options
        browser = playwright.chromium.launch(executable_path=config.paths.browser_path, headless=False)

        # Create a new browser context with viewport and device options
        context = browser.new_context(
            viewport={"width": config.ui_settings.viewport_width, "height": config.ui_settings.viewport_height},
            accept_downloads=True,
        )        # Create a new page
        page = context.new_page()

        try:
            # Open the website with the specified page
            url = f"{config.worksafe_bc.url}{start_page}"
            page.goto(url)

            # Monitor for navigation to other pages
            monitor_navigation(page, start_page, mappings, data)

            # Form filling monitoring has ended (browser was likely closed)
            print("Form filling session ended.")

        except KeyboardInterrupt:
            print("Exiting due to user interrupt")
        except Exception as e:
            print(f"Error: {e}")
        finally:
            try:
                context.close()
                browser.close()
                print("Browser closed successfully.")
            except Exception as e:
                print(f"Error closing browser: {e}")


if __name__ == "__main__":
    # Command line argument parsing
    parser = argparse.ArgumentParser(description="Fill WorkSafe BC NOP forms automatically using data from a JSON file.")
    
    parser.add_argument(
        "data_file",
        help="Path to the JSON data file to be used for filling the form"
    )

    args = parser.parse_args()

    try:
        fill_nop(data_file=args.data_file)
    except FileNotFoundError as e:
        print(f"Error: Could not find data file '{args.data_file}': {e}")
        sys.exit(1)
    except ValueError as e:
        print(f"Error: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"Unexpected error: {e}")
        sys.exit(1)
