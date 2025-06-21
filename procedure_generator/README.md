# Safe Work Procedure Generator

Takes a work order and creates a safe work procedure PDF from a template and procedure documents.

## Development 

`pip install -r requirements.txt`


## Building

To make an executable

`PLAYWRIGHT_BROWSERS_PATH="0"`
`playwright uninstall`

`pyinstaller script.spec --clean`

## Configuration

The application uses a centralized configuration system with the `swp_config.json` file. This file contains all configurable settings including:

- **Paths**: Default folders for templates, work procedures, and browser executable
- **Debug Paths**: Development/testing paths  
- **UI Settings**: Window sizes, viewport dimensions
- **Timeouts**: Various timeout values for web automation
- **Field Names**: PDF form field names and constants
- **WorkSafe BC**: URL and other service-specific settings
- **NOP Mappings**: Form field mappings for Notice of Project forms

To modify default paths or settings, edit the `swp_config.json` file. The application will automatically load these settings on startup.

### Using the Config Loader

In code, use the `config_loader` module:

```python
from config_loader import config, get_default_template_folder

# Get specific values
template_folder = get_default_template_folder()
timeout = config.get("timeouts.standard_timeout", 1000)
```