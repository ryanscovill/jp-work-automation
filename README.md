## Procedure Generator

Takes a work order and creates a safe work procedure PDF from a template and procedure documents.


## Worksafe NOP

`python -m playwright install chromium`

## Configuration Management

The project now uses a centralized configuration system with `swp_config.json` containing all hardcoded paths and settings. This improves maintainability and allows easy customization without code changes.

### Key Configuration Sections:
- **paths**: File system paths for templates, procedures, and executables
- **debug_paths**: Development/testing specific paths
- **timeouts**: Web automation timing configurations  
- **ui_settings**: Application window and viewport settings
- **field_names**: PDF form field identifiers
- **worksafe_bc**: Service-specific configurations
- **NOP**: Notice of Project form mappings