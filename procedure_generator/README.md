# Safe Work Procedure Generator

Takes a work order and creates a safe work procedure PDF from a template and procedure documents.

## Development 

`pip install -r requirements.txt`

## Building

To make an executable:

```bash
PLAYWRIGHT_BROWSERS_PATH="0"
playwright uninstall
pyinstaller script.spec --clean
```

## Configuration

The application uses a centralized configuration system with the `swp_config.yaml` file. To modify default paths or settings, edit this file and the application will automatically load the settings on startup.