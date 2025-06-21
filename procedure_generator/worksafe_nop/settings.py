from ..config_loader import config


class Settings:
    """Class to store all configurable settings"""

    URL = config.get("worksafe_bc.url", "https://prevnop.online.worksafebc.com/")

    # Timeouts
    FIELD_INTERACTION_DELAY = config.get("timeouts.field_interaction_delay", 50)  # ms between field interactions
    SHORT_TIMEOUT = config.get("timeouts.short_timeout", 300)  # ms for quick operations
    STANDARD_TIMEOUT = config.get("timeouts.standard_timeout", 1000)  # ms standard wait
    NAVIGATION_TIMEOUT = config.get("timeouts.navigation_timeout", 500)  # ms wait after navigation

    # Navigation and detection
    CONTENT_CHANGE_THRESHOLD = config.get("timeouts.content_change_threshold", 500)  # threshold to detect significant DOM changes
    NEXT_BUTTON_CHECK_INTERVAL = config.get("timeouts.next_button_check_interval", 5)  # seconds
    PERIODIC_PAGE_CHECK_INTERVAL = config.get("timeouts.periodic_page_check_interval", 10)  # seconds

    # Viewport settings
    VIEWPORT_WIDTH = config.get("ui_settings.viewport_width", 1400)
    VIEWPORT_HEIGHT = config.get("ui_settings.viewport_height", 900)

    BROWSER_PATH = config.get("paths.browser_path", r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe")
