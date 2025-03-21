# CLAUDE.md - JP Work Automation Guidelines

## Build & Development Commands
- Setup: `pip install -r requirements.txt`
- Build executable: `pyinstaller --onefile --windowed script.py`
- Run application: `python script.py`

## Project Structure
- `procedure_generator/script.py`: Main GUI application using Gooey
- `procedure_generator/work_procedure_filter.js`: JavaScript for filtering PDF dropdown options
- Examples directory contains sample documents for testing

## Code Style Guidelines
- Use UTF-8 encoding for all files
- Follow PEP 8 style guidelines for Python
- Use type hints for function definitions
- Use meaningful variable names (snake_case for Python)
- Proper error handling with specific exceptions
- Document functions with docstrings
- Keep functions focused on a single responsibility
- Use constants for configuration values
- Maintain consistent indentation (4 spaces for Python)