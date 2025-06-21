class Settings:
    """Class to store all configurable settings"""

    URL = "https://prevnop.online.worksafebc.com/"

    # Timeouts
    FIELD_INTERACTION_DELAY = 50  # ms between field interactions
    SHORT_TIMEOUT = 300  # ms for quick operations
    STANDARD_TIMEOUT = 1000  # ms standard wait
    NAVIGATION_TIMEOUT = 500  # ms wait after navigation

    # Navigation and detection
    CONTENT_CHANGE_THRESHOLD = 500  # threshold to detect significant DOM changes
    NEXT_BUTTON_CHECK_INTERVAL = 5  # seconds
    PERIODIC_PAGE_CHECK_INTERVAL = 10  # seconds

    # Viewport settings
    VIEWPORT_WIDTH = 1400
    VIEWPORT_HEIGHT = 900

    BROWSER_PATH = r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe"
