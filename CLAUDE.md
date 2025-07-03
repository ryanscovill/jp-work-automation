# CLAUDE.md - JP Work Automation Guidelines

## Project Overview
This is a work procedure automation tool with both GUI (Gooey) and web interfaces for PDF processing, form filling, and document generation.

## Project Structure
- `procedure_generator/script.py`: Main GUI application using Gooey
- `procedure_generator/web/backend/main.py`: FastAPI web backend
- `procedure_generator/web/frontend/`: React TypeScript frontend with Tailwind CSS
- `procedure_generator/swp/`: Safe Work Procedure generation module
- `procedure_generator/worksafe_nop/`: NOP form filling functionality
- `procedure_generator/excel_pdf/`: Excel to PDF processing
- `examples/`: Sample documents for testing

## Development Setup

### GUI Application
- Setup: `cd procedure_generator && pip install -r requirements.txt`
- Run: `python script.py`
- Build executable: `pyinstaller --onefile script.py`

### Web Application
Backend:
- Setup: `cd procedure_generator/web/backend && pip install -r requirements.txt`
- Run from project root: `cd /path/to/jp-work-automation/procedure_generator && python -m uvicorn web.backend.main:app --reload --host 0.0.0.0 --port 8000`

Frontend:
- Setup: `cd procedure_generator/web/frontend && npm install`
- Dev server: `npm run dev`
- Build: `npm run build`
- Lint: `npm run lint`

## Testing
- Playwright tests: `python test_playwright.py`
- Use examples directory for testing functionality

## Code Style Guidelines

### Python
- Use UTF-8 encoding for all files
- Follow PEP 8 style guidelines
- Use type hints for function definitions
- Use meaningful variable names (snake_case)
- Proper error handling with specific exceptions
- Document functions with docstrings
- Keep functions focused on single responsibility
- Use constants for configuration values
- Maintain consistent indentation (4 spaces)

### TypeScript/React
- Use TypeScript for all new code
- Follow React functional component patterns
- Use Tailwind CSS v4 for styling
- Use ShadCN components
- Use meaningful component names (PascalCase)
- Keep components focused and reusable
- Use proper TypeScript types and interfaces

### File Organization
- Keep related functionality in appropriate modules
- Use `__init__.py` files for Python packages
- Separate configuration into dedicated files
- Examples go in the examples directory

## Configuration
- Main config: `procedure_generator/swp_config.yaml`
- Web frontend build config: `vite.config.ts`
- Python project config: `pyproject.toml`
- TypeScript config: `tsconfig.json`

## Key Features
- PDF form filling and generation
- Excel to PDF conversion
- Safe Work Procedure (SWP) generation
- NOP form processing
- Multi-interface support (GUI and web)

## Dependencies Management
- Python dependencies in `requirements.txt` files
- Node.js dependencies in `package.json`
- Keep dependencies up to date and secure
- Test after dependency updates